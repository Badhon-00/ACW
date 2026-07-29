#!/usr/bin/env python3
"""Validate observent observability backend configuration.

Usage:
  python validate_setup.py phoenix [--smoke-test]
  python validate_setup.py langfuse [--smoke-test]
  python validate_setup.py signoz [--smoke-test]
  python validate_setup.py elastic-apm [--smoke-test]
  python validate_setup.py langsmith [--smoke-test]
  python validate_setup.py opik [--smoke-test]
  python validate_setup.py jaeger [--smoke-test]
  python validate_setup.py phoenix,signoz [--smoke-test]   # multi-backend fan-out
  python validate_setup.py all

Per backend:
  - Verifies required env vars
  - Verifies required Python packages installed
  - Probes the configured endpoint for reachability
  - With --smoke-test: emits one synthetic LLM span (carrying the convention
    that backend prefers — OI for Phoenix, OTel-GenAI for Langfuse / SigNoz /
    Elastic APM / LangSmith / Opik / Jaeger)

Exit code: 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import socket
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import urlparse

from observent_matrix import backend_conventions

# Per-backend convention preference, derived from the single source of truth in
# observent_matrix.py. See references/matrix.md § Convention resolution: Phoenix
# is OpenInference-native; Langfuse / SigNoz / Elastic APM / LangSmith / Opik /
# Jaeger consume OTel-GenAI.
BACKEND_CONVENTION: dict[str, str] = backend_conventions()


def resolve_convention(backends: list[str]) -> str:
    """Derive the span-attribute convention for a *set* of backends.

    Mechanical rule, mirroring references/matrix.md § Convention resolution and
    SKILL.md Phase 1 § 1.4 — not a free choice:

      - ``{phoenix}``                                   -> "oi"
      - any non-empty subset of the OTel-GenAI backends -> "otel-genai"
      - phoenix *and* >=1 OTel-GenAI backend            -> "both"

    Phoenix renders its native UI from OpenInference keys; Langfuse / SigNoz /
    Elastic APM / LangSmith / Opik / Jaeger consume OTel-GenAI. "both" is
    justified only when a fan-out spans Phoenix and at least one of the others,
    so each UI lights up.
    """
    has_phoenix = "phoenix" in backends
    has_otel_genai = any(BACKEND_CONVENTION.get(b) == "otel-genai" for b in backends)
    if has_phoenix and has_otel_genai:
        return "both"
    if has_phoenix:
        return "oi"
    if has_otel_genai:
        return "otel-genai"
    raise ValueError(f"cannot resolve convention for backends: {backends!r}")


@dataclass
class Result:
    backend: str
    passed: bool = True
    messages: list[str] = field(default_factory=list)

    def ok(self, msg: str) -> None:
        self.messages.append(f"  [OK]   {msg}")

    def warn(self, msg: str) -> None:
        self.messages.append(f"  [WARN] {msg}")

    def fail(self, msg: str) -> None:
        self.messages.append(f"  [FAIL] {msg}")
        self.passed = False

    def info(self, msg: str) -> None:
        self.messages.append(f"  [INFO] {msg}")


def _load_dotenv_if_available() -> None:
    """Best-effort load of a project .env so standalone runs see the project's
    real values (e.g. LANGFUSE_HOST=http://localhost:3000) instead of cloud
    defaults. python-dotenv is an OPTIONAL soft dependency — never required
    (skill scripts stay stdlib-only); absence degrades silently."""
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found,unused-ignore]
    except ImportError:
        return
    load_dotenv()


def _is_installed(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def _check_env(result: Result, var: str, required: bool = True) -> str | None:
    val = os.environ.get(var)
    if val:
        masked = (val[:6] + "..." + val[-4:]) if len(val) > 12 else "***"
        result.ok(f"{var} = {masked}")
        return val
    if required:
        result.fail(f"{var} is not set")
    else:
        result.info(f"{var} not set (optional)")
    return None


_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def _is_local(host: str | None) -> bool:
    return (host or "").lower() in _LOCAL_HOSTS


def _provision_hint(result: Result, backend: str, host: str | None) -> None:
    """On an unreachable *local* self-host endpoint, point the user at provisioning.

    LangSmith has no free self-host edition, so it gets the enterprise-license note
    instead of a Docker offer. See references/self_host.md.
    """
    if not _is_local(host):
        return
    if backend == "langsmith":
        result.info(
            "LangSmith self-host requires an enterprise license - point LANGSMITH_ENDPOINT "
            "at your licensed deployment, or use LangSmith Cloud with LANGSMITH_API_KEY."
        )
    else:
        result.info(
            f"{backend} is not reachable locally - run /observent to provision it with Docker, "
            "or start it yourself (see references/self_host.md)."
        )


def _probe_tcp(result: Result, host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            result.ok(f"TCP {host}:{port} reachable")
            return True
    except OSError as e:
        result.fail(f"TCP {host}:{port} unreachable: {e}")
        return False


def _probe_http(result: Result, url: str, method: str = "GET", timeout: float = 5.0) -> bool:
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result.ok(f"HTTP {method} {url} -> {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        # Some endpoints return 4xx for unauth-but-reachable; treat as reachable.
        if 400 <= e.code < 500:
            result.ok(f"HTTP {method} {url} -> {e.code} (reachable)")
            return True
        result.fail(f"HTTP {method} {url} -> {e.code}")
        return False
    except (urllib.error.URLError, OSError) as e:
        result.fail(f"HTTP {method} {url} unreachable: {e}")
        return False


def _probe_http_retry(
    result: Result,
    url: str,
    *,
    method: str = "GET",
    attempts: int = 7,
    base_delay: float = 2.0,
    max_delay: float = 45.0,
    timeout: float = 5.0,
) -> bool:
    """Like ``_probe_http`` but retries with exponential backoff (bounded ~2 min).

    For a backend whose endpoint may not accept traffic immediately after
    ``docker compose up --wait`` returns. SigNoz is the motivating case: its
    ingester serves OTLP only after an opamp-driven collector restart that can lag
    ``--wait`` by ~2 minutes, so a single immediate probe fails with
    ``RemoteDisconnected`` even though the stack is fine. Records only the final
    outcome to ``result`` (no per-attempt spam), plus one INFO while it waits.
    """
    delay = base_delay
    last_err = ""
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result.ok(f"HTTP {method} {url} -> {resp.status} (attempt {attempt}/{attempts})")
                return True
        except urllib.error.HTTPError as e:
            # A 4xx means the receiver is up (reachable-but-unauth); good enough.
            if 400 <= e.code < 500:
                result.ok(f"HTTP {method} {url} -> {e.code} (reachable, attempt {attempt}/{attempts})")
                return True
            last_err = f"HTTP {e.code}"
        except (urllib.error.URLError, OSError) as e:
            last_err = str(e)
        if attempt < attempts:
            wait = min(delay, max_delay)
            if attempt == 1:
                result.info(
                    f"{url} not ready yet — retrying with backoff "
                    f"(up to {attempts} attempts; SigNoz's OTLP receiver can lag `--wait` ~2 min)"
                )
            time.sleep(wait)
            delay *= 2
    result.fail(f"HTTP {method} {url} unreachable after {attempts} attempts: {last_err}")
    return False


def check_phoenix(smoke: bool, *, fanout: bool = False) -> Result:
    r = Result("phoenix")
    if _is_installed("phoenix"):
        r.ok("arize-phoenix installed")
    elif fanout:
        # Multi-backend fan-out (Phoenix + >=1 other backend) uses a manual
        # TracerProvider + OTLPSpanExporter per references/matrix.md § Multi-Backend
        # Fan-Out — that path never imports arize-phoenix. Don't fail on its
        # absence; the correct check here is reachability + a real synthetic-span
        # POST (below), needing only the OTLP HTTP exporter.
        r.info(
            "arize-phoenix not installed — multi-backend fan-out uses a manual "
            "TracerProvider (matrix.md § Multi-Backend Fan-Out); package not required"
        )
        if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
            r.fail(
                "opentelemetry-exporter-otlp-proto-http not installed "
                "(pip install 'opentelemetry-exporter-otlp-proto-http>=1.25')"
            )
    else:
        r.fail("arize-phoenix not installed (pip install 'arize-phoenix>=5.0')")

    api_key = os.environ.get("PHOENIX_API_KEY")
    endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")

    if api_key:
        r.info("PHOENIX_API_KEY set -> cloud mode")
        endpoint = endpoint or "https://app.phoenix.arize.com"
        _probe_http(r, endpoint, method="GET")
    else:
        r.info("PHOENIX_API_KEY not set -> local mode (px.launch_app() or phoenix-server)")
        endpoint = endpoint or "http://localhost:6006"
        parsed = urlparse(endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6006
        if not _probe_tcp(r, host, port):
            _provision_hint(r, "phoenix", host)

    if smoke and r.passed:
        _emit_smoke_span(
            r,
            endpoint=f"{endpoint.rstrip('/')}/v1/traces",
            headers=_phoenix_headers(api_key),
            convention=BACKEND_CONVENTION["phoenix"],
        )
    return r


def check_langfuse(smoke: bool, *, fanout: bool = False) -> Result:
    r = Result("langfuse")
    if _is_installed("langfuse"):
        r.ok("langfuse installed")
    elif fanout:
        # Multi-backend fan-out uses a manual TracerProvider + OTLPSpanExporter
        # (matrix.md § Langfuse OTLP path) — that path never imports langfuse.
        r.info(
            "langfuse not installed — multi-backend fan-out uses a manual "
            "TracerProvider + OTLP exporter (matrix.md § Langfuse); package not required"
        )
        if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
            r.fail(
                "opentelemetry-exporter-otlp-proto-http not installed "
                "(pip install 'opentelemetry-exporter-otlp-proto-http>=1.25')"
            )
    else:
        r.fail("langfuse not installed (pip install 'langfuse>=3.0')")

    pk = _check_env(r, "LANGFUSE_PUBLIC_KEY")
    sk = _check_env(r, "LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
    r.info(f"LANGFUSE_HOST = {host}")

    host_name = urlparse(host).hostname
    if _is_local(host_name):
        # First boot pulls images + runs Postgres/ClickHouse migrations + compiles
        # Next.js; langfuse-web has no upstream healthcheck so `--wait` can't block
        # on it (self_host.md § Langfuse). Retry with backoff right before a smoke
        # span POST; a plain reachability check stays a single fast probe.
        health = f"{host.rstrip('/')}/api/public/health"
        reachable = (
            _probe_http_retry(r, health, method="GET")
            if smoke
            else _probe_http(r, health, method="GET")
        )
        if not reachable:
            _provision_hint(r, "langfuse", host_name)

    if pk and sk and _is_installed("langfuse"):
        try:
            from langfuse import Langfuse  # type: ignore[import-not-found,unused-ignore]

            client = Langfuse(public_key=pk, secret_key=sk, host=host)
            if hasattr(client, "auth_check"):
                ok = client.auth_check()
                if ok:
                    r.ok("Langfuse auth_check() passed")
                else:
                    r.fail("Langfuse auth_check() returned False")
            else:
                _probe_http(r, f"{host.rstrip('/')}/api/public/health", method="GET")
        except Exception as e:  # noqa: BLE001
            r.fail(f"Langfuse client init failed: {e}")
    elif fanout and pk and sk and not _is_installed("langfuse"):
        # No SDK to auth_check() with — fall back to a plain reachability probe of
        # the OTLP-path health endpoint so fan-out still gets a real auth/reach signal.
        _probe_http(r, f"{host.rstrip('/')}/api/public/health", method="GET")

    if smoke and r.passed:
        import base64

        auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()
        _emit_smoke_span(
            r,
            endpoint=f"{host.rstrip('/')}/api/public/otel/v1/traces",
            headers={"Authorization": f"Basic {auth}"},
            convention=BACKEND_CONVENTION["langfuse"],
        )
    return r


def check_signoz(smoke: bool) -> Result:
    r = Result("signoz")
    if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
        r.fail(
            "opentelemetry-exporter-otlp-proto-http not installed "
            "(pip install 'opentelemetry-exporter-otlp-proto-http>=1.25')"
        )
    endpoint = os.environ.get("SIGNOZ_ENDPOINT", "http://localhost:4318/v1/traces")
    r.info(f"SIGNOZ_ENDPOINT = {endpoint}")

    parsed = urlparse(endpoint)
    is_cloud = parsed.hostname and parsed.hostname.endswith("signoz.cloud")
    if is_cloud:
        _check_env(r, "SIGNOZ_INGESTION_KEY")
    else:
        r.info("Self-hosted SigNoz (no ingestion key required)")

    # Probe the OTLP endpoint root. When we're about to emit a smoke span (i.e.
    # right after provisioning), retry with backoff: SigNoz's ingester serves OTLP
    # only after an opamp-driven collector restart that can lag `--wait` by ~2 min,
    # so an immediate probe/POST hits a transient RemoteDisconnected window. A plain
    # (no-smoke) reachability check stays a single fast probe.
    root = f"{parsed.scheme}://{parsed.netloc}"
    reachable = _probe_http_retry(r, root, method="GET") if smoke else _probe_http(r, root, method="GET")
    if not reachable:
        _provision_hint(r, "signoz", parsed.hostname)

    if smoke and r.passed:
        headers = {}
        key = os.environ.get("SIGNOZ_INGESTION_KEY")
        if key:
            headers["signoz-access-token"] = key
        _emit_smoke_span(
            r,
            endpoint=endpoint,
            headers=headers,
            convention=BACKEND_CONVENTION["signoz"],
        )
    return r


def check_elastic_apm(smoke: bool) -> Result:
    r = Result("elastic-apm")
    if not _is_installed("elasticapm"):
        r.fail("elastic-apm not installed (pip install 'elastic-apm>=6.20')")
    else:
        r.ok("elastic-apm installed")

    server_url = os.environ.get("ELASTIC_APM_SERVER_URL", "http://localhost:8200")
    r.info(f"ELASTIC_APM_SERVER_URL = {server_url}")

    secret_token = os.environ.get("ELASTIC_APM_SECRET_TOKEN")
    api_key = os.environ.get("ELASTIC_APM_API_KEY")
    if secret_token:
        r.ok("ELASTIC_APM_SECRET_TOKEN set (Bearer auth)")
    elif api_key:
        r.ok("ELASTIC_APM_API_KEY set (ApiKey auth)")
    else:
        r.info("No auth set — assuming self-host without secret token")

    if not _probe_http(r, server_url.rstrip("/"), method="GET"):
        _provision_hint(r, "elastic-apm", urlparse(server_url).hostname)

    if smoke and r.passed:
        _emit_elastic_apm_smoke(
            r,
            server_url=server_url,
            secret_token=secret_token,
            api_key=api_key,
        )
    return r


def _emit_elastic_apm_smoke(
    r: Result,
    *,
    server_url: str,
    secret_token: str | None,
    api_key: str | None,
) -> None:
    """Emit one synthetic transaction via the native elasticapm.Client.

    Uses the native agent (the slash-command default) rather than OTLP, so the
    smoke test exercises the same code path the generated app will use. The
    transaction carries gen_ai.* attributes — Elastic's OTel bridge promotes
    them so they appear consistently in the Kibana APM UI.
    """
    if not _is_installed("elasticapm"):
        r.warn("Skipping smoke test: elastic-apm not installed")
        return
    try:
        import elasticapm  # type: ignore[import-not-found,unused-ignore]
    except ImportError as e:
        r.warn(f"Skipping smoke test: {e}")
        return

    client_kwargs: dict[str, str] = {
        "service_name": "observent-smoke-test",
        "server_url": server_url,
    }
    if secret_token:
        client_kwargs["secret_token"] = secret_token
    if api_key:
        client_kwargs["api_key"] = api_key

    try:
        client = elasticapm.Client(**client_kwargs)
        client.begin_transaction("smoke")  # type: ignore[no-untyped-call,unused-ignore]
        elasticapm.label(  # type: ignore[no-untyped-call,unused-ignore]
            gen_ai_operation_name="chat",
            gen_ai_provider_name="anthropic",
            gen_ai_request_model="claude-sonnet-4-6",
            gen_ai_usage_input_tokens=4,
            gen_ai_usage_output_tokens=2,
        )
        client.end_transaction("observent.smoke", "success")  # type: ignore[no-untyped-call,unused-ignore]
        client.close()  # type: ignore[no-untyped-call,unused-ignore]
    except Exception as e:  # noqa: BLE001
        r.fail(f"Elastic APM client init / transaction failed: {e}")
        return

    r.ok(f"Synthetic transaction (otel-genai via native agent) sent to {server_url}")
    r.info("Verify the transaction appears in Kibana APM (Services → observent-smoke-test) within ~10s.")


def check_langsmith(smoke: bool) -> Result:
    r = Result("langsmith")
    if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
        r.fail(
            "opentelemetry-exporter-otlp-proto-http not installed "
            "(pip install 'opentelemetry-exporter-otlp-proto-http>=1.25')"
        )

    base = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").rstrip("/")
    endpoint = f"{base}/otel/v1/traces"
    r.info(f"LANGSMITH_ENDPOINT = {base}")
    r.info(f"OTLP traces endpoint = {endpoint}")

    api_key = _check_env(r, "LANGSMITH_API_KEY")
    project = os.environ.get("LANGSMITH_PROJECT")
    if project:
        r.ok(f"LANGSMITH_PROJECT = {project}")
    else:
        r.info("LANGSMITH_PROJECT not set (traces land in the 'default' project)")

    parsed = urlparse(endpoint)
    root = f"{parsed.scheme}://{parsed.netloc}"
    if not _probe_http(r, root, method="GET"):
        _provision_hint(r, "langsmith", parsed.hostname)

    if smoke and r.passed and api_key:
        headers = {"x-api-key": api_key}
        if project:
            headers["Langsmith-Project"] = project
        _emit_smoke_span(
            r,
            endpoint=endpoint,
            headers=headers,
            convention=BACKEND_CONVENTION["langsmith"],
        )
    return r


def check_opik(smoke: bool) -> Result:
    r = Result("opik")
    if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
        r.fail(
            "opentelemetry-exporter-otlp-proto-http not installed "
            "(pip install 'opentelemetry-exporter-otlp-proto-http>=1.25')"
        )

    base = os.environ.get("OPIK_URL_OVERRIDE", "https://www.comet.com/opik/api").rstrip("/")
    endpoint = f"{base}/v1/private/otel/v1/traces"
    r.info(f"OPIK_URL_OVERRIDE = {base}")
    r.info(f"OTLP traces endpoint = {endpoint}")

    parsed = urlparse(endpoint)
    is_cloud = bool(parsed.hostname and parsed.hostname.endswith("comet.com"))

    headers: dict[str, str] = {}
    api_key: str | None = None
    if is_cloud:
        # Opik Cloud requires an API key + workspace; project routing is optional.
        api_key = _check_env(r, "OPIK_API_KEY")
        workspace = _check_env(r, "OPIK_WORKSPACE")
        if api_key:
            headers["Authorization"] = api_key
        if workspace:
            headers["Comet-Workspace"] = workspace
        project = os.environ.get("OPIK_PROJECT_NAME")
        if project:
            r.ok(f"OPIK_PROJECT_NAME = {project}")
            headers["projectName"] = project
        else:
            r.info("OPIK_PROJECT_NAME not set (traces land in the 'Default Project')")
    else:
        r.info("Self-hosted Opik (no auth required)")

    root = f"{parsed.scheme}://{parsed.netloc}"
    if not _probe_http(r, root, method="GET"):
        _provision_hint(r, "opik", parsed.hostname)

    if smoke and r.passed and (not is_cloud or api_key):
        _emit_smoke_span(
            r,
            endpoint=endpoint,
            headers=headers,
            convention=BACKEND_CONVENTION["opik"],
        )
    return r


def check_jaeger(smoke: bool) -> Result:
    r = Result("jaeger")
    if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
        r.fail(
            "opentelemetry-exporter-otlp-proto-http not installed "
            "(pip install 'opentelemetry-exporter-otlp-proto-http>=1.25')"
        )
    endpoint = os.environ.get("JAEGER_ENDPOINT", "http://localhost:4318/v1/traces")
    r.info(f"JAEGER_ENDPOINT = {endpoint}")
    r.info("Jaeger ingests OTLP directly (v2, or v1 with COLLECTOR_OTLP_ENABLED=true); no auth.")

    # Probe the OTLP endpoint root (Jaeger's OTLP receiver, default :4318).
    parsed = urlparse(endpoint)
    root = f"{parsed.scheme}://{parsed.netloc}"
    if not _probe_http(r, root, method="GET"):
        _provision_hint(r, "jaeger", parsed.hostname)

    if smoke and r.passed:
        _emit_smoke_span(
            r,
            endpoint=endpoint,
            headers={},
            convention=BACKEND_CONVENTION["jaeger"],
        )
    return r


def _phoenix_headers(api_key: str | None) -> dict[str, str]:
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    return {}


def _set_oi_attrs(span) -> None:  # type: ignore[no-untyped-def]
    """OpenInference attribute keys (Phoenix-native)."""
    span.set_attribute("openinference.span.kind", "LLM")
    span.set_attribute("llm.model_name", "claude-sonnet-4-6")
    span.set_attribute("llm.provider", "anthropic")
    span.set_attribute("input.value", '{"prompt": "smoke test"}')
    span.set_attribute("input.mime_type", "application/json")
    span.set_attribute("output.value", '{"completion": "ok"}')
    span.set_attribute("output.mime_type", "application/json")
    span.set_attribute("llm.token_count.prompt", 4)
    span.set_attribute("llm.token_count.completion", 2)
    span.set_attribute("llm.token_count.total", 6)


def _set_otel_genai_attrs(span) -> None:  # type: ignore[no-untyped-def]
    """OTel-GenAI attribute keys (Langfuse / SigNoz)."""
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.provider.name", "anthropic")
    span.set_attribute("gen_ai.request.model", "claude-sonnet-4-6")
    span.set_attribute("gen_ai.response.model", "claude-sonnet-4-6")
    span.set_attribute("gen_ai.usage.input_tokens", 4)
    span.set_attribute("gen_ai.usage.output_tokens", 2)
    span.set_attribute("gen_ai.response.finish_reasons", ["stop"])


def _emit_smoke_span(
    r: Result,
    *,
    endpoint: str,
    headers: dict[str, str],
    convention: str,
) -> None:
    """Emit one synthetic LLM span via OTLP HTTP and report ingestion.

    The span carries attribute keys matching the backend's preferred convention:
      - "oi"        -> OpenInference keys (openinference.span.kind, llm.token_count.*, ...)
      - "otel-genai" -> OTel-GenAI keys (gen_ai.operation.name, gen_ai.usage.*, ...)
      - "both"      -> union (only used when explicitly requested)
    """
    if not _is_installed("opentelemetry.exporter.otlp.proto.http"):
        r.warn("Skipping smoke test: opentelemetry-exporter-otlp-proto-http not installed")
        return
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
        )
    except ImportError as e:
        r.warn(f"Skipping smoke test: {e}")
        return

    provider = TracerProvider(resource=Resource.create({"service.name": "observent-smoke-test"}))
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    tracer = provider.get_tracer("observent.smoke_test")

    with tracer.start_as_current_span("smoke-test-llm-call") as span:
        if convention in ("oi", "both"):
            _set_oi_attrs(span)
        if convention in ("otel-genai", "both"):
            _set_otel_genai_attrs(span)

    provider.shutdown()
    r.ok(f"Synthetic LLM span ({convention}) exported to {endpoint}")
    r.info("Verify the span appears in your backend UI within ~10s.")


CHECKS: dict[str, Callable[[bool], Result]] = {
    "phoenix": check_phoenix,
    "langfuse": check_langfuse,
    "signoz": check_signoz,
    "elastic-apm": check_elastic_apm,
    "langsmith": check_langsmith,
    "opik": check_opik,
    "jaeger": check_jaeger,
}


def _parse_backends(value: str) -> list[str]:
    """Parse comma-separated backend list. Dedupes, preserves order, validates."""
    valid = {*CHECKS.keys(), "all"}
    tokens = [t.strip() for t in value.split(",") if t.strip()]
    if not tokens:
        raise argparse.ArgumentTypeError("backend argument cannot be empty")
    unknown = [t for t in tokens if t not in valid]
    if unknown:
        raise argparse.ArgumentTypeError(
            f"unknown backend(s): {', '.join(unknown)} "
            f"(valid: {', '.join(sorted(valid))})"
        )
    if "all" in tokens:
        return list(CHECKS.keys())
    seen: set[str] = set()
    deduped: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def main() -> int:
    _load_dotenv_if_available()
    parser = argparse.ArgumentParser(description="Validate observent observability setup.")
    parser.add_argument(
        "backend",
        type=_parse_backends,
        help="Backend or comma-separated list (phoenix, langfuse, signoz, elastic-apm, "
        'langsmith, opik, jaeger, all). e.g. "phoenix" or "phoenix,jaeger".',
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Emit one synthetic span per backend (LLM span via OTLP for "
        "phoenix/langfuse/signoz/langsmith/opik/jaeger; transaction via native elasticapm.Client "
        "for elastic-apm).",
    )
    args = parser.parse_args()

    backends: list[str] = args.backend
    # A multi-backend invocation means the generated stack is the manual
    # fan-out TracerProvider, not phoenix.otel.register(); Phoenix's package
    # check relaxes accordingly (gap: arize-phoenix wrongly required in fan-out).
    fanout = len(backends) > 1
    overall_pass = True
    for backend in backends:
        print(f"\n=== {backend} ===")
        if backend == "phoenix":
            result = check_phoenix(args.smoke_test, fanout=fanout)
        elif backend == "langfuse":
            result = check_langfuse(args.smoke_test, fanout=fanout)
        else:
            result = CHECKS[backend](args.smoke_test)
        for msg in result.messages:
            print(msg)
        if not result.passed:
            overall_pass = False

    print("\n=== Summary ===")
    print(f"  Resolved convention: {resolve_convention(backends)}")
    print(f"  {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
