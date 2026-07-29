# observent — Local Self-Host Provisioning

This file is the **canonical reference** for standing up a backend locally with Docker when
the user has chosen a self-host backend that isn't already running. The observent skill reads
the templates here in Phase 2 and emits them as lifecycle tasks (a `write_file` for a vendored
compose file, and/or a `run_command` that runs `docker compose ... up -d --wait`) — see
`SKILL.md` Phase 1 § 1.6 and Phase 3 § 3.1.

Provisioning is **only ever offered** when **all** of these hold:

1. The backend's resolved endpoint `mode` is `self-host` (cloud is never provisioned).
2. The endpoint is unreachable at probe time (`detection.backends_reachable.<backend> == false`).
3. Docker + Compose are available (`detection.docker_available && detection.docker_compose_available`).
4. The backend is one of **Phoenix · Langfuse · SigNoz · Elastic APM · Opik · Jaeger** (see LangSmith note below).

`docker compose up` runs **only after** the user approves the `confirm` task — provisioning is
never silent.

---

## Provisioning method per backend

Three methods, chosen per backend by what the upstream stack needs:

| Backend | Method | Why |
|---|---|---|
| Phoenix | `vendored-compose` | Single container, no external config files — fully self-contained. |
| Jaeger | `vendored-compose` | Single all-in-one container, OTLP enabled inline via env — fully self-contained. |
| Elastic APM | `vendored-compose` | ES + Kibana + APM Server; config passed inline via `-E` flags / env. |
| Langfuse | `upstream-clone` | v3 stack is 6 coupled services with generated secrets; upstream compose is the supported path. |
| SigNoz | `vendor-cli-generated` | Upstream deprecated its `docker-compose` manifests (2026); self-host now flows through the **Foundry** CLI, which *generates* a plain compose file we then run ourselves. |
| Opik | `upstream-clone` | Multi-service stack (backend, frontend, ClickHouse, MySQL, Redis, MinIO) wired via compose profiles; upstream compose is the supported path. |

- **`vendored-compose`** → the skill writes `docker-compose.observent-<backend>.yml` into the
  user's project root (a `write_file` task), then runs
  `docker compose -f docker-compose.observent-<backend>.yml up -d --wait` (a `run_command` task).
- **`upstream-clone`** → the skill runs a single `run_command` that shallow-clones the pinned
  upstream repo into `.observent/vendor/<backend>/` and brings it up. No compose file is written
  into the project root.
- **`vendor-cli-generated`** → the upstream stack ships **no** ready compose file; instead a vendor
  CLI materializes one. Four ordered steps: (1) `run_command` installs the pinned vendor CLI
  (checksum-verified GitHub-releases installer); (2) `write_file` writes the CLI's declarative
  config; (3) `run_command` runs the CLI's `forge`-equivalent to **generate a plain
  `compose.yaml`**; (4) `run_command` runs `docker compose -f <generated> up -d --wait` on it —
  identical to `vendored-compose` from step 4 on. We deliberately generate-then-run-ourselves
  rather than hand the CLI ongoing control of the stack. Because the installer downloads a binary,
  the Phase 3 `confirm` diff **must** surface the CLI install as its own line (what it installs,
  from where, why it's trustworthy) — see `SKILL.md` Phase 1 § 1.5 / Phase 3 and
  `spec_schema.md § tasks.json` `installs_cli`.

Every `up` uses `--wait` so the command blocks until container healthchecks pass; the final
`validate` task then runs against a live endpoint (**but see the SigNoz readiness caveat below** —
for SigNoz, `--wait` going green does not mean the OTLP receiver is accepting spans yet).

---

## Arize Phoenix — `vendored-compose`

UI + OTLP HTTP on `6006`, OTLP gRPC published on host `4327` (→ container `4317`). No auth, no
database (in-memory by default).

`docker-compose.observent-phoenix.yml`:
```yaml
services:
  phoenix:
    image: arizephoenix/phoenix:version-17.15.0
    container_name: observent-phoenix
    ports:
      - "6006:6006"   # UI + OTLP HTTP (/v1/traces) — observent always uses this
      # Host gRPC remapped 4327 -> 4317 to avoid colliding with a co-hosted SigNoz
      # (and Jaeger), which also bind host 4317. observent exports over HTTP (6006),
      # so the non-default host gRPC port is harmless. See § Port-conflict matrix.
      - "4327:4317"   # OTLP gRPC (host 4327)
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:6006').status==200 else sys.exit(1)"]
      interval: 5s
      timeout: 5s
      retries: 12
```

- Up: `docker compose -f docker-compose.observent-phoenix.yml up -d --wait`
- UI: `http://localhost:6006` · OTLP: `http://localhost:6006/v1/traces`
- Down: `docker compose -f docker-compose.observent-phoenix.yml down`
- **No-Docker alternative:** `px.launch_app()` in-process (see `matrix.md § Arize Phoenix`). Offer
  this if `detection.docker_available == false`.

---

## Jaeger — `vendored-compose`

Single all-in-one container. Jaeger v2 ships OTLP receivers on `4317`/`4318` enabled by default; the
explicit `COLLECTOR_OTLP_ENABLED=true` below is harmless on v2 and required if you pin a v1 image.
UI on `16686`, OTLP HTTP on `4318`. No auth, in-memory storage (local dev only).

`docker-compose.observent-jaeger.yml`:
```yaml
services:
  jaeger:
    image: jaegertracing/jaeger:2.19.0
    container_name: observent-jaeger
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"   # UI
      - "4318:4318"     # OTLP HTTP (/v1/traces)
      - "4317:4317"     # OTLP gRPC
```

- **Readiness:** Jaeger's image is distroless (no shell/curl/python), so it carries **no**
  in-container `healthcheck:` — `docker compose up -d --wait` waits for the container to reach the
  *running* state (Jaeger starts in ~1s), and the downstream `validate` task then probes the OTLP
  endpoint. This is the one vendored stack without a healthcheck block, for that reason.
- Up: `docker compose -f docker-compose.observent-jaeger.yml up -d --wait`
- UI: `http://localhost:16686` · OTLP: `http://localhost:4318/v1/traces` (set `JAEGER_ENDPOINT` to it)
- No auth — leave it unset.
- **Note:** Jaeger's default `4318`/`4317` OTLP ports collide with a self-hosted SigNoz **and** with
  Phoenix's host gRPC (see § Port-conflict matrix for the full pairwise picture). If you run Jaeger
  alongside either, remap one stack's host ports in its compose file.
- Down: `docker compose -f docker-compose.observent-jaeger.yml down`

---

## Elastic APM — `vendored-compose`

ES + Kibana + APM Server, single-node, **security disabled** (local dev only). APM Server on
`8200`, Kibana on `5601`, Elasticsearch on `9200`.

`docker-compose.observent-elastic-apm.yml`:
```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.3
    container_name: observent-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
    ports:
      - "9200:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -q '\"status\":\"\\(green\\|yellow\\)\"'"]
      interval: 10s
      timeout: 10s
      retries: 12
  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.3
    container_name: observent-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
  apm-server:
    image: docker.elastic.co/apm/apm-server:8.15.3
    container_name: observent-apm-server
    ports:
      - "8200:8200"
    depends_on:
      elasticsearch:
        condition: service_healthy
    command: >
      apm-server -e
        -E apm-server.host=0.0.0.0:8200
        -E apm-server.rum.enabled=true
        -E output.elasticsearch.hosts=["http://elasticsearch:9200"]
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:8200/ > /dev/null"]
      interval: 10s
      timeout: 10s
      retries: 12
```

- Up: `docker compose -f docker-compose.observent-elastic-apm.yml up -d --wait`
- APM Server: `http://localhost:8200` (`ELASTIC_APM_SERVER_URL`) · Kibana APM UI: `http://localhost:5601/app/apm`
- No secret token needed (security off) — leave `ELASTIC_APM_SECRET_TOKEN` unset.
- Down (drop volumes): `docker compose -f docker-compose.observent-elastic-apm.yml down -v`

---

## Langfuse — `upstream-clone`

Langfuse v3 self-host is six coupled services (web, worker, postgres, clickhouse, redis, minio)
with generated secrets. Use the upstream compose, pinned to the `:3` major tag (upstream's
stability contract).

- Up:
  ```bash
  git clone --depth 1 -b main https://github.com/langfuse/langfuse.git .observent/vendor/langfuse \
    && docker compose -f .observent/vendor/langfuse/docker-compose.yml up -d --wait
  ```
- UI: `http://localhost:3000` · OTLP: `http://localhost:3000/api/public/otel/v1/traces`
- After first start, create a project in the UI and copy `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`
  into `.env`, with `LANGFUSE_HOST=http://localhost:3000`. Unlike the other stacks these keys can't
  be known ahead of time, so the `validate` task may report missing keys until the user fills them in.
- **⚠️ First-boot readiness.** `docker compose up -d --wait` can return before Langfuse is actually
  serving: first boot pulls six images, runs Postgres + ClickHouse migrations, and compiles the
  Next.js web app — several minutes. Worse, upstream's `langfuse-web` service ships **no
  `healthcheck:`** in its compose definition, so `--wait` can't block on it (it falls back to
  container-running state, not application-ready state). Expect the UI/OTLP endpoint to refuse
  connections or 5xx for a few minutes after `--wait` reports up. `validate_setup.py`'s
  `check_langfuse` handles this by probing `/api/public/health` with bounded retry/backoff under
  `--smoke-test` (don't treat the first failure as fatal) — poll
  `http://localhost:3000/api/public/health` manually if validating by hand.
- Down: `docker compose -f .observent/vendor/langfuse/docker-compose.yml down`

---

## SigNoz — `vendor-cli-generated`

> **Upstream change (2026).** SigNoz **deprecated** its `deploy/docker/docker-compose.yaml`
> manifests and the `deploy/install.sh` script — they no longer exist on `main` (cloning the repo
> and pointing `docker compose` at that path now fails with *path not found*). Self-host installs
> through the **Foundry** CLI (`foundryctl`) instead. Foundry *generates* a plain compose file,
> which is why SigNoz moved from `upstream-clone` to `vendor-cli-generated`. Ports are unchanged
> (UI `8080`, OTLP `4317`/`4318`), so `matrix.md`'s SigNoz endpoint table stays correct — only the
> provisioning mechanism changed.

Four steps (map to `plan.provision[]` fields — see `spec_schema.md § plan.provision[]`):

1. **Install the CLI** (`cli_install_command`) — a checksum-verified GitHub-releases installer that
   installs `foundryctl` to `~/.local/bin`. It detects the platform (incl. Windows/Git-Bash:
   `mingw*`/`cygwin*`/`msys*` → `windows` + `.exe`) and verifies the downloaded tarball's sha256
   against a published checksums file — no arbitrary remote exec beyond that. **Surface this as its
   own `confirm` line** (it installs a binary, a larger consent surface than `docker compose up`):
   ```bash
   curl -fsSL https://signoz.io/foundry.sh | bash
   ```
2. **Write the declarative config** (`cli_config_file`, content in the `<!-- plan:clicfg_signoz -->`
   anchor) — `casting.yaml`:
   ```yaml
   apiVersion: v1alpha1
   kind: Installation
   metadata:
     name: signoz
   spec:
     deployment:
       flavor: compose
       mode: docker
   ```
3. **Generate the compose file** (`generate_command`) — `forge` writes
   `pours/deployment/compose.yaml` (+ config) without touching Docker:
   ```bash
   foundryctl forge -f casting.yaml
   ```
   (We use `forge`, not `foundryctl cast`, so the CLI never gets ongoing control of the running
   stack — from here it's plain `docker compose`.)
4. **Bring it up** (`up_command`) on the generated file:
   ```bash
   docker compose -f pours/deployment/compose.yaml up -d --wait
   ```

- UI: `http://localhost:8080`
- OTLP: `http://localhost:4318/v1/traces` (HTTP) / `localhost:4317` (gRPC).
- No auth for self-host (leave `SIGNOZ_INGESTION_KEY` unset; set `SIGNOZ_ENDPOINT=http://localhost:4318/v1/traces`).
- Down: `docker compose -f pours/deployment/compose.yaml down`
- **Image pins:** Foundry pins image versions **inside the generated `compose.yaml`** — observent
  doesn't control or track them (see § Image Versions). Only the CLI/installer is pinned by us.
- **⚠️ OTLP-readiness caveat (opamp settle delay).** For SigNoz, `docker compose up --wait` returning
  all-`Healthy` does **not** mean the OTLP receiver is accepting spans. The ingester's container
  healthcheck (the health-check extension on `13133`) goes green while the collector is still running
  a **placeholder** pipeline; it then waits for its real config to arrive over **opamp** from the
  `signoz` control-plane container, does an internal *Restarting collector service*, and only then
  logs `Starting HTTP server ... endpoint [::]:4318`. That settle can take **~2 minutes** after
  `--wait` reports healthy — an immediate span POST fails with `RemoteDisconnected`. `validate_setup.py`
  handles this with a **bounded retry/backoff** on the SigNoz smoke span (don't treat the first
  `RemoteDisconnected` as a failure); `docker logs signoz-ingester-1` shows the restart if you want to
  confirm.

---

## Opik — `upstream-clone`

Opik's compose brings up a multi-service stack (backend, frontend, ClickHouse, MySQL, Redis, MinIO)
selected via the `opik` profile. Clone the repo at the pinned tag so the compose file matches the
pinned images, and pin `OPIK_VERSION` for the `ghcr.io/comet-ml/opik/*` images (the compose defaults
them to `latest`).

- Up:
  ```bash
  git clone --depth 1 -b 2.1.3 https://github.com/comet-ml/opik.git .observent/vendor/opik \
    && OPIK_VERSION=2.1.3 docker compose -f .observent/vendor/opik/deployment/docker-compose/docker-compose.yaml --profile opik up -d --wait
  ```
- UI: `http://localhost:5173` · OTLP: `http://localhost:5173/api/v1/private/otel/v1/traces`
- No auth for self-host (leave `OPIK_API_KEY` / `OPIK_WORKSPACE` unset; set `OPIK_URL_OVERRIDE=http://localhost:5173/api`).
- If port `5173` is taken, set `NGINX_PORT` (or `OPIK_PORT_OFFSET` to shift every Opik port) before `up`.
- Down: `docker compose -f .observent/vendor/opik/deployment/docker-compose/docker-compose.yaml --profile opik down`

---

## LangSmith — not provisioned

LangSmith has **no free OSS / Docker edition**. It is commercial and cloud-first; self-host is
an enterprise-licensed deployment. observent does **not** generate a local stack for it.

When LangSmith is selected with a non-cloud `LANGSMITH_ENDPOINT` that is unreachable, surface this
text instead of a provisioning offer:

> LangSmith self-host requires an enterprise license. Point `LANGSMITH_ENDPOINT` at your licensed
> deployment, or use LangSmith Cloud (`https://api.smith.langchain.com`, the default) with
> `LANGSMITH_API_KEY`. observent can't provision LangSmith locally.

---

## Image Versions

Canonical pin record for the provisioning stacks (analogous to `matrix.md § Verified Versions`).
These are exact image tags, not floors. Bump alongside the matrix's pip pins and update the
`Last verified` date.

| Backend | Image | Tag | Source |
|---|---|---|---|
| Phoenix | `arizephoenix/phoenix` | `version-17.15.0` | Docker Hub — https://hub.docker.com/r/arizephoenix/phoenix/tags |
| Elastic APM | `docker.elastic.co/elasticsearch/elasticsearch` | `8.15.3` | Elastic registry — https://www.docker.elastic.co |
| Elastic APM | `docker.elastic.co/kibana/kibana` | `8.15.3` | Elastic registry |
| Elastic APM | `docker.elastic.co/apm/apm-server` | `8.15.3` | Elastic registry |
| Langfuse | `langfuse/langfuse`, `langfuse/langfuse-worker` | `3` (major; upstream compose) | https://github.com/langfuse/langfuse |
| SigNoz | *(not tracked — `vendor-cli-generated`)* | resolved by Foundry at generation time | see note below |
| Opik | `ghcr.io/comet-ml/opik/opik-backend`, `opik-frontend`, `opik-python-backend` | `2.1.3` (`OPIK_VERSION`) | https://github.com/comet-ml/opik |
| Opik | `clickhouse/clickhouse-server` | `25.8.16.34-alpine` (upstream compose) | https://github.com/comet-ml/opik |
| Opik | `mysql` | `8.4.2` (upstream compose) | https://github.com/comet-ml/opik |
| Opik | `redis` | `7.2.4-alpine3.19` (upstream compose) | https://github.com/comet-ml/opik |
| Jaeger | `jaegertracing/jaeger` | `2.19.0` | Docker Hub — https://hub.docker.com/r/jaegertracing/jaeger/tags |

*Last verified: 2026-07-03.* Langfuse and Opik tags are governed by their upstream compose files
(`upstream-clone` method); the rows above record what those files pinned at verification time.

**SigNoz (`vendor-cli-generated`).** Image tags are **whatever Foundry resolves when it generates
`pours/deployment/compose.yaml`** — they live only in that generated file, not here, and observent
neither controls nor tracks them (to see them, read the generated compose after `forge`). The one
thing we *do* pin is the CLI/installer: the Foundry installer script is `https://signoz.io/foundry.sh`
(resolves the latest `foundryctl` GitHub-release tag, sha256-verified). If a reproducible
`foundryctl` version is needed, pin it via the installer's version flag / a pinned release tag rather
than tracking downstream image tags here.

> **TODO (re-verify on next bump):** the Opik/Langfuse `upstream-clone` compose paths were **not**
> re-verified in this pass. Before the next release, confirm both still resolve (upstream repos move
> compose files — this is exactly how the old SigNoz path broke); if either has drifted, migrate it
> the same way SigNoz moved here.

---

## Port-conflict & readiness notes

### Port-conflict matrix

Default **host** ports each self-hostable stack binds. The danger zone is OTLP `4317`/`4318`:
Phoenix, Jaeger, **and** SigNoz all want them, so any two of those three collide out of the box.

| Backend | UI | OTLP HTTP `4318` | OTLP gRPC `4317` | Other host ports |
|---|---|---|---|---|
| Phoenix | `6006` | — (HTTP OTLP shares `6006`) | `4327` → 4317 *(remapped by observent)* | — |
| Jaeger | `16686` | `4318` | `4317` | — |
| SigNoz | `8080` | `4318` | `4317` | — |
| Langfuse | `3000` | — | — | postgres/clickhouse/redis/minio (internal) |
| Opik | `5173` | — | — | mysql/clickhouse/redis/minio (internal) |
| Elastic APM | `5601` (Kibana) | — | — | `8200` (APM), `9200` (ES) |

Pairwise host-port collisions (all on `4317`/`4318`):

| Pair | Collides on | Resolution |
|---|---|---|
| Phoenix + SigNoz | `4317` (gRPC) | **Handled** — Phoenix's vendored compose already remaps host gRPC to `4327`. Phoenix HTTP OTLP is `6006`, SigNoz is `4318`; no HTTP clash. |
| Phoenix + Jaeger | `4317` (gRPC) | **Handled** by the same `4327` remap. |
| Jaeger + SigNoz | `4317` **and** `4318` | **Not** auto-handled — both bind `4318`. Remap one stack's host ports (e.g. Jaeger → `4328:4318`) and point that backend's `*_ENDPOINT` at the remapped port. |

- **Before writing any compose file**, Phase 1 § 1.5 checks for collisions **among the newly-selected
  backend set** (not only against already-running services) using this matrix, and remaps / warns
  accordingly — the Phoenix `4327` remap is the one baked-in case; the Jaeger + SigNoz pair still
  needs a per-run remap surfaced in the diff.

### Readiness

- **`--wait`:** every `up` uses `--wait`; vendored compose files carry `healthcheck:` blocks so
  `--wait` blocks until healthy. `upstream-clone` stacks generally ship their own healthchecks, with
  one exception: Langfuse's `langfuse-web` service has none (see below). Jaeger is the other
  exception — its distroless image can't self-healthcheck — `--wait` falls back to the container's
  *running* state and the final `validate` task probes its OTLP endpoint.
- **SigNoz opamp settle delay:** `--wait` reporting `Healthy` is **not** sufficient for SigNoz — its
  ingester serves OTLP only after an opamp-driven collector restart that can lag `--wait` by ~2 min.
  See § SigNoz for the full explanation; `validate_setup.py` retries the SigNoz smoke span with
  backoff rather than failing on the first `RemoteDisconnected`.
- **Langfuse first-boot delay:** `--wait` reporting up is **not** sufficient either — `langfuse-web`
  ships no `healthcheck:` and first boot runs Postgres + ClickHouse migrations plus a Next.js compile
  (several minutes). See § Langfuse; `validate_setup.py`'s `check_langfuse` retries
  `/api/public/health` with backoff under `--smoke-test`.
- **Stray port conflicts:** if a probe shows a port already in use by something *other* than the
  intended backend (e.g. `6006` taken but not Phoenix), warn the user and let them remap the host
  port in the compose file rather than forcing `up`.
- **Teardown:** each section lists its `down` command. The skill surfaces the matching `down` line in
  the Phase 4 § 4.3 summary so the user can stop the stack.
