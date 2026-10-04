"""Detect five emotions using the Watson NLP EmotionPredict service."""

import math
import os

import requests


WATSON_EMOTION_URL = os.environ.get(
    "WATSON_EMOTION_URL",
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict",
)
MODEL_ID = "emotion_aggregated-workflow_lang_en_stock"
EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")
REQUEST_TIMEOUT = 15


class EmotionServiceError(RuntimeError):
    """Report an unavailable service or an invalid Watson response."""


def _invalid_result():
    """Return the required null-valued result for rejected input."""
    return dict.fromkeys((*EMOTIONS, "dominant_emotion"))


def _format_result(payload):
    """Extract valid scores and choose the largest score deterministically."""
    emotion = payload["emotionPredictions"][0]["emotion"]
    scores = {name: float(emotion[name]) for name in EMOTIONS}
    if any(not math.isfinite(score) or not 0 <= score <= 1
           for score in scores.values()):
        raise ValueError("Emotion scores must be finite numbers between 0 and 1")
    scores["dominant_emotion"] = max(EMOTIONS, key=scores.__getitem__)
    return scores


def emotion_detector(text_to_analyse):
    """Return five emotion scores and the dominant emotion for English text.

    Blank input and an HTTP 400 response return all six fields set to None.
    Other HTTP, network and response-format errors raise EmotionServiceError.
    Tied scores select the first emotion in EMOTIONS.
    """
    if not isinstance(text_to_analyse, str) or not text_to_analyse.strip():
        return _invalid_result()

    payload = {"raw_document": {"text": text_to_analyse}}
    headers = {"grpc-metadata-mm-model-id": MODEL_ID}
    try:
        response = requests.post(
            WATSON_EMOTION_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 400:
            return _invalid_result()
        response.raise_for_status()
    except requests.RequestException as error:
        raise EmotionServiceError(f"Watson request failed: {error}") from error

    try:
        return _format_result(response.json())
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise EmotionServiceError("Watson returned an invalid emotion response") from error
