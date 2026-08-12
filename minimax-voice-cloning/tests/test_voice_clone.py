import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "voice_clone.py"
SPEC = importlib.util.spec_from_file_location("voice_clone", SCRIPT_PATH)
voice_clone = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(voice_clone)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class VoiceCloneTests(unittest.TestCase):
    def test_regional_endpoints_cover_upload_and_clone(self):
        self.assertEqual(
            voice_clone.REGIONS["global"]["clone"],
            "https://api.minimax.io/v1/voice_clone",
        )
        self.assertEqual(
            voice_clone.REGIONS["cn"]["clone"],
            "https://api.minimaxi.com/v1/voice_clone",
        )
        self.assertTrue(voice_clone.REGIONS["global"]["upload"].endswith("/v1/files/upload"))
        self.assertTrue(voice_clone.REGIONS["cn"]["upload"].endswith("/v1/files/upload"))

    def test_multipart_contains_required_purpose_and_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            path.write_bytes(b"audio-bytes")
            body = voice_clone.build_multipart(path, "test-boundary")

        self.assertIn(b'name="purpose"', body)
        self.assertIn(b"voice_clone", body)
        self.assertIn(b'name="file"; filename="sample.wav"', body)
        self.assertIn(b"audio-bytes", body)

    def test_clone_payload_has_only_required_fields(self):
        self.assertEqual(
            voice_clone.build_clone_payload(123, "approved-voice", "speech-2.8-hd"),
            {
                "file_id": 123,
                "voice_id": "approved-voice",
                "model": "speech-2.8-hd",
            },
        )

    @mock.patch.object(voice_clone.urllib.request, "urlopen")
    def test_upload_reads_file_id_and_uses_bearer_auth(self, urlopen):
        urlopen.return_value = FakeResponse(
            {"file": {"file_id": 987}, "base_resp": {"status_code": 0}}
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.mp3"
            path.write_bytes(b"audio-bytes")
            file_id = voice_clone.upload_audio(path, "global", "test-key")

        self.assertEqual(file_id, 987)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertIn(b"voice_clone", request.data)

    @mock.patch.object(voice_clone.urllib.request, "urlopen")
    def test_clone_posts_required_json_and_checks_response(self, urlopen):
        urlopen.return_value = FakeResponse({"base_resp": {"status_code": 0}})
        response = voice_clone.clone_voice(
            123, "approved-voice", "speech-2.6-hd", "cn", "test-key"
        )

        self.assertEqual(response["base_resp"]["status_code"], 0)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.minimaxi.com/v1/voice_clone")
        self.assertEqual(
            json.loads(request.data),
            {
                "file_id": 123,
                "voice_id": "approved-voice",
                "model": "speech-2.6-hd",
            },
        )

    def test_nonzero_api_status_raises(self):
        with self.assertRaisesRegex(RuntimeError, "API error 1004"):
            voice_clone.check_response(
                {"base_resp": {"status_code": 1004, "status_msg": "invalid file"}}
            )

    def test_missing_api_status_raises(self):
        with self.assertRaisesRegex(RuntimeError, "base_resp.status_code"):
            voice_clone.check_response({})


if __name__ == "__main__":
    unittest.main()
