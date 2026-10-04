"""Validate Flask routes with isolated NLP fixtures."""

import unittest
from unittest.mock import patch

from EmotionDetection import EmotionServiceError
from server import APP


class TestEmotionServer(unittest.TestCase):
    """Check HTTP behavior, parameter handling and rendered responses."""

    def setUp(self):
        APP.config.update(TESTING=True)
        self.client = APP.test_client()
        self.patcher = patch("server.emotion_detector")
        self.detector = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.detector.return_value = {
            "anger": 0.1, "disgust": 0.02, "fear": 0.03,
            "joy": 0.8, "sadness": 0.05, "dominant_emotion": "joy",
        }

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Emotion Detector", response.data)
        self.assertIn(b'textToAnalyze', response.data)

    def test_static_assets(self):
        for path in ["/static/style.css", "/static/mywebscript.js"]:
            with self.subTest(path=path):
                with self.client.get(path) as response:
                    self.assertEqual(response.status_code, 200)

    def test_formatted_success_response(self):
        response = self.client.get(
            "/emotionDetector", query_string={"textToAnalyze": "I am glad this happened"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertIn(b"'anger': 0.1", response.data)
        self.assertIn(b"The dominant emotion is joy.", response.data)

    def test_empty_and_whitespace_inputs(self):
        for text in ["", " \t\n"]:
            with self.subTest(text=text):
                response = self.client.get(
                    "/emotionDetector", query_string={"textToAnalyze": text}
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.get_data(as_text=True),
                                 "Invalid text! Please try again!")
        self.detector.assert_not_called()

    def test_missing_parameter(self):
        self.assertEqual(self.client.get("/emotionDetector").status_code, 400)
        self.detector.assert_not_called()

    def test_watson_rejected_input(self):
        self.detector.return_value["dominant_emotion"] = None
        response = self.client.get("/emotionDetector?textToAnalyze=test")
        self.assertEqual(response.status_code, 400)

    def test_service_failure(self):
        self.detector.side_effect = EmotionServiceError("Service unavailable")
        response = self.client.get("/emotionDetector?textToAnalyze=test")
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"temporarily unavailable", response.data)

    def test_url_encoded_input(self):
        text = "Joy + fear & café?"
        self.client.get("/emotionDetector", query_string={"textToAnalyze": text})
        self.detector.assert_called_once_with(text)

    def test_post_is_not_supported(self):
        self.assertEqual(self.client.post("/emotionDetector").status_code, 405)
