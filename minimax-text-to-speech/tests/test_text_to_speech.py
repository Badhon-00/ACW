import importlib.util
import json
import pathlib
import types
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).parents[1] / "scripts" / "text_to_speech.py"
SPEC = importlib.util.spec_from_file_location("text_to_speech", MODULE_PATH)
tts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tts)


def synthesis_args(**overrides):
    values = {
        "model": "speech-2.8-hd",
        "text": "Hello",
        "voice_id": "English_expressive_narrator",
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0.0,
        "audio_format": "mp3",
        "sample_rate": 32000,
        "bitrate": 128000,
        "channel": 1,
        "language_boost": "auto",
        "pronunciation_dict": '{"tone": ["Omg/Oh my god"]}',
        "voice_modify": '{"pitch": 0, "intensity": 0, "timbre": 0}',
        "output_format": "hex",
        "stream": True,
        "subtitle_enable": True,
    }
    values.update(overrides)
    return types.SimpleNamespace(**values)


class ConfigurationTests(unittest.TestCase):
    def test_regions_models_and_formats_match_supported_matrix(self):
        self.assertEqual(
            tts.REGIONS,
            {
                "global": "https://api.minimax.io/v1",
                "cn": "https://api.minimaxi.com/v1",
            },
        )
        self.assertEqual(
            tts.WS_REGIONS,
            {
                "global": "wss://api.minimax.io/ws/v1/t2a_v2",
                "cn": "wss://api.minimaxi.com/ws/v1/t2a_v2",
            },
        )
        self.assertEqual(tts.DEFAULT_MODEL, "speech-2.8-hd")
        self.assertEqual(
            tts.MODELS,
            [
                "speech-2.8-hd",
                "speech-2.8-turbo",
                "speech-2.6-hd",
                "speech-2.6-turbo",
                "speech-02-hd",
                "speech-02-turbo",
                "speech-01-hd",
                "speech-01-turbo",
            ],
        )
        self.assertEqual(tts.AUDIO_FORMATS, ["mp3", "wav", "flac", "pcm"])


class RequestTests(unittest.TestCase):
    def test_http_payload_includes_supported_request_fields(self):
        payload = tts.build_payload(synthesis_args())

        self.assertEqual(
            set(payload),
            {
                "model",
                "text",
                "stream",
                "language_boost",
                "output_format",
                "voice_setting",
                "pronunciation_dict",
                "audio_setting",
                "voice_modify",
                "subtitle_enable",
            },
        )

    def test_async_payload_omits_http_only_fields(self):
        payload = tts.build_payload(synthesis_args(), async_=True)

        self.assertEqual(
            set(payload),
            {
                "model",
                "text",
                "voice_setting",
                "audio_setting",
                "language_boost",
                "pronunciation_dict",
                "voice_modify",
            },
        )

    @mock.patch.object(tts, "_request")
    def test_async_query_uses_post_json(self, request):
        request.return_value = {"status": "Processing"}

        result = tts.query_task("task-123", "cn", "secret")

        self.assertEqual(result, {"status": "Processing"})
        request.assert_called_once_with(
            "https://api.minimaxi.com/v1/query/t2a_async_query_v2",
            "secret",
            method="POST",
            payload={"task_id": "task-123"},
        )

    @mock.patch("urllib.request.urlopen")
    def test_request_sends_bearer_authorization(self, urlopen):
        response = mock.MagicMock()
        response.read.return_value = json.dumps(
            {"data": {"audio": "00", "status": 2}, "base_resp": {"status_code": 0}}
        ).encode("utf-8")
        urlopen.return_value.__enter__.return_value = response

        result = tts._request(
            "https://api.minimax.io/v1/t2a_v2",
            "secret",
            method="POST",
            payload={"model": "speech-2.8-hd", "text": "Hello"},
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(result["data"]["audio"], "00")


if __name__ == "__main__":
    unittest.main()
