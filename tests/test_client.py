"""Test response parsing and error handling using explicit HTTP fixtures."""

import unittest
from unittest.mock import Mock, patch

import requests

from EmotionDetection.emotion_detection import (
    EMOTIONS, MODEL_ID, REQUEST_TIMEOUT, WATSON_EMOTION_URL,
    EmotionServiceError, emotion_detector,
)


class TestEmotionClient(unittest.TestCase):
    """Exercise client behavior without claiming to run the NLP model."""

    def setUp(self):
        self.patcher = patch("EmotionDetection.emotion_detection.requests.post")
        self.post = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.response = Mock(status_code=200)
        self.post.return_value = self.response
        self.scores = dict(zip(EMOTIONS, [0.1, 0.02, 0.03, 0.8, 0.05]))
        self.response.json.return_value = {
            "emotionPredictions": [{"emotion": self.scores}]
        }

    def test_format_and_dominant_emotion(self):
        result = emotion_detector("An English statement.")
        self.assertEqual(set(result), {*EMOTIONS, "dominant_emotion"})
        self.assertEqual(result["dominant_emotion"], "joy")
        self.assertEqual(result["anger"], 0.1)
        self.assertTrue(all(isinstance(result[name], float) for name in EMOTIONS))

    def test_each_emotion_can_be_dominant(self):
        for expected in EMOTIONS:
            with self.subTest(expected=expected):
                scores = dict.fromkeys(EMOTIONS, 0.01)
                scores[expected] = 0.96
                self.response.json.return_value = {
                    "emotionPredictions": [{"emotion": scores}]
                }
                self.assertEqual(
                    emotion_detector("A statement")["dominant_emotion"], expected
                )

    def test_request_contract(self):
        emotion_detector("Text + punctuation & unicode: café.")
        self.post.assert_called_once_with(
            WATSON_EMOTION_URL,
            json={"raw_document": {"text": "Text + punctuation & unicode: café."}},
            headers={"grpc-metadata-mm-model-id": MODEL_ID},
            timeout=REQUEST_TIMEOUT,
        )

    def test_blank_inputs_return_none_without_network(self):
        for text in ["", " \t\n", None, 42]:
            with self.subTest(text=text):
                result = emotion_detector(text)
                self.assertEqual(set(result), {*EMOTIONS, "dominant_emotion"})
                self.assertTrue(all(value is None for value in result.values()))
        self.post.assert_not_called()

    def test_status_400_returns_none(self):
        self.response.status_code = 400
        result = emotion_detector("Rejected by Watson")
        self.assertTrue(all(value is None for value in result.values()))
        self.response.json.assert_not_called()

    def test_http_failure_is_reported(self):
        self.response.status_code = 502
        self.response.raise_for_status.side_effect = requests.HTTPError("502")
        with self.assertRaises(EmotionServiceError):
            emotion_detector("A statement")

    def test_timeout_is_reported(self):
        self.post.side_effect = requests.Timeout("Timed out")
        with self.assertRaises(EmotionServiceError):
            emotion_detector("A statement")

    def test_invalid_json_is_reported(self):
        self.response.json.side_effect = ValueError("Not JSON")
        with self.assertRaises(EmotionServiceError):
            emotion_detector("A statement")

    def test_missing_prediction_is_reported(self):
        self.response.json.return_value = {"emotionPredictions": []}
        with self.assertRaises(EmotionServiceError):
            emotion_detector("A statement")

    def test_missing_score_is_reported(self):
        del self.scores["fear"]
        with self.assertRaises(EmotionServiceError):
            emotion_detector("A statement")

    def test_invalid_scores_are_reported(self):
        for value in [float("nan"), float("inf"), -0.1, 1.1, "invalid"]:
            with self.subTest(value=value):
                self.scores["joy"] = value
                with self.assertRaises(EmotionServiceError):
                    emotion_detector("A statement")

    def test_tied_scores_are_deterministic(self):
        self.response.json.return_value = {
            "emotionPredictions": [{"emotion": dict.fromkeys(EMOTIONS, 0.2)}]
        }
        self.assertEqual(emotion_detector("A statement")["dominant_emotion"], "anger")
