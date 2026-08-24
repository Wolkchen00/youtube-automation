"""Current Kie Veo generate/poll contract fixtures, with no network calls."""

import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from core import kie_api  # noqa: E402


def response(payload):
    return SimpleNamespace(json=lambda: payload, status_code=200)


class VeoGenerateContractTests(unittest.TestCase):
    def generate_and_payload(self, **kwargs):
        post = mock.Mock(return_value=response({
            "code": 200, "data": {"taskId": "veo-task"},
        }))
        with mock.patch.object(kie_api.requests, "post", post), \
             mock.patch.object(
                 kie_api, "poll_veo_task",
                 return_value="https://cdn.example.test/result.mp4",
             ):
            result = kie_api.generate_veo_video("contract prompt", **kwargs)
        self.assertEqual(result, "https://cdn.example.test/result.mp4")
        self.assertEqual(post.call_count, 1)
        return post.call_args.kwargs["json"]

    def test_text_to_video_payload_has_no_image_urls(self):
        payload = self.generate_and_payload(
            model="veo3_fast", generation_type="TEXT_2_VIDEO",
            duration=4, aspect_ratio="9:16", resolution="720p",
        )
        self.assertEqual(payload, {
            "model": "veo3_fast", "prompt": "contract prompt",
            "aspectRatio": "9:16", "generationType": "TEXT_2_VIDEO",
            "duration": 4, "resolution": "720p",
        })

    def test_first_and_last_payload_preserves_image_order(self):
        urls = [
            "https://images.example.test/first.png",
            "https://images.example.test/last.png",
        ]
        payload = self.generate_and_payload(
            model="veo3", generation_type="FIRST_AND_LAST_FRAMES_2_VIDEO",
            image_urls=urls, duration=6, aspect_ratio="16:9", resolution="1080p",
        )
        self.assertEqual(payload["imageUrls"], urls)
        self.assertEqual(payload["generationType"], "FIRST_AND_LAST_FRAMES_2_VIDEO")
        self.assertEqual(payload["duration"], 6)
        self.assertNotIn("image_url", payload)

    def test_reference_payload_preserves_three_image_order_and_fixed_8s(self):
        urls = [
            "https://images.example.test/object.png",
            "https://images.example.test/room.png",
            "https://images.example.test/style.png",
        ]
        payload = self.generate_and_payload(
            model="veo3_lite", generation_type="REFERENCE_2_VIDEO",
            image_urls=urls, duration=8,
        )
        self.assertEqual(payload["imageUrls"], urls)
        self.assertEqual(payload["generationType"], "REFERENCE_2_VIDEO")
        self.assertEqual(payload["duration"], 8)

    def test_mode_constraints_fail_before_http(self):
        with mock.patch.object(kie_api.requests, "post") as post:
            with self.assertRaises(kie_api.VeoContractError):
                kie_api.generate_veo_video(
                    "bad", generation_type="TEXT_2_VIDEO",
                    image_urls=["https://images.example.test/not-allowed.png"],
                    duration=6,
                )
            with self.assertRaises(kie_api.VeoContractError):
                kie_api.generate_veo_video(
                    "bad", generation_type="REFERENCE_2_VIDEO",
                    image_urls=["https://images.example.test/ref.png"],
                    duration=6,
                )
        post.assert_not_called()


class VeoPollContractTests(unittest.TestCase):
    def poll(self, payload):
        with mock.patch.object(kie_api.time, "sleep"), \
             mock.patch.object(kie_api.requests, "get", return_value=response(payload)):
            return kie_api.poll_veo_task("veo-task", max_attempts=1)

    def test_success_reads_data_response_result_urls(self):
        self.assertEqual(self.poll({
            "code": 200,
            "data": {
                "successFlag": 1,
                "response": {
                    "resultUrls": ["https://cdn.example.test/veo.mp4"],
                    "creditsConsumed": 60,
                },
            },
        }), "https://cdn.example.test/veo.mp4")

    def test_success_without_optional_credits_is_valid(self):
        self.assertEqual(self.poll({
            "code": 200,
            "data": {
                "successFlag": 1,
                "response": {"resultUrls": ["https://cdn.example.test/veo.mp4"]},
            },
        }), "https://cdn.example.test/veo.mp4")

    def test_pending_and_both_failure_flags_return_none(self):
        self.assertIsNone(self.poll({"code": 200, "data": {"successFlag": 0}}))
        for flag in (2, 3):
            with self.subTest(flag=flag):
                self.assertIsNone(self.poll({
                    "code": 200,
                    "data": {"successFlag": flag, "errorMessage": "fixture failure"},
                }))


class VeoDurationGuardTests(unittest.TestCase):
    def test_flf_guard_rejects_mocked_8s_file_when_6s_requested(self):
        with mock.patch.object(kie_api.ffmpeg_tools, "get_video_duration", return_value=8.0):
            with self.assertRaisesRegex(
                kie_api.VeoDurationError, "requested=6s, measured=8s"
            ):
                kie_api.assert_veo_flf_duration("mocked.mp4", requested_duration=6)

    def test_flf_guard_returns_measured_duration_inside_tolerance(self):
        with mock.patch.object(kie_api.ffmpeg_tools, "get_video_duration", return_value=6.2):
            self.assertEqual(
                kie_api.assert_veo_flf_duration("mocked.mp4", requested_duration=6),
                6.2,
            )


if __name__ == "__main__":
    unittest.main()
