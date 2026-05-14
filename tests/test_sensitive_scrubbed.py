import unittest
from unittest.mock import patch

from hello import app


class SensitiveScrubbedEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("hello.sentry_sdk.flush")
    @patch("hello.sentry_sdk.capture_exception")
    def test_sensitive_scrubbed_returns_handled_error_response(self, mock_capture_exception, mock_flush):
        mock_capture_exception.return_value = "event-123"

        response = self.client.post("/api/sensitive/scrubbed", json={"any": "payload"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {
            "error": "sensitive data error",
            "sentry_event_id": "event-123",
        })
        mock_capture_exception.assert_called_once()
        mock_flush.assert_called_once_with(timeout=5)

    @patch("hello.sentry_sdk.flush")
    @patch("hello.sentry_sdk.capture_exception")
    def test_sensitive_scrubbed_handles_missing_event_id(self, mock_capture_exception, mock_flush):
        mock_capture_exception.return_value = None

        response = self.client.post("/api/sensitive/scrubbed", json={"any": "payload"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {
            "error": "sensitive data error",
            "sentry_event_id": "",
        })
        mock_capture_exception.assert_called_once()
        mock_flush.assert_called_once_with(timeout=5)


if __name__ == "__main__":
    unittest.main()
