# Emotion Detector submission guide

This repository contains the implementation, actual terminal logs and browser screenshots. Open a code file and copy its full contents into the corresponding code field. Paste successful terminal output only after the indicated check has actually passed.

The 21 isolated fixture tests passed and `server.py` scored 10.00/10 in Pylint. The real Watson service returned HTTP 502, so the five required live tests did not pass. The code is now in a public GitHub repository, https://github.com/KhuramWalayat/emotion-detector. The remaining requirement, the five live tests, needs a reachable lab service.

| Field | What to submit | File | Current status |
|---|---|---|---|
| 1 | Public README URL | `README.md` | Published: https://github.com/KhuramWalayat/emotion-detector/blob/main/README.md |
| 2.1 | Application function code | `EmotionDetection/emotion_detection.py` | Code ready; copy the full file below. |
| 2.2 | Successful import and real test output | `evidence/02_03_live_detector.txt` | Import passed; real call failed with HTTP 502. Rerun in the lab. |
| 3.1 | Correctly formatted detector code | `EmotionDetection/emotion_detection.py` | Code ready; includes all five scores and dominant_emotion. |
| 3.2 | Accurate real output format | `evidence/02_03_live_detector.txt` | Pending a successful real Watson call. Fixture tests verify parsing only. |
| 4.1 | Public __init__.py URL | `EmotionDetection/__init__.py` | Publish first; copy the actual GitHub file-page URL. |
| 4.2 | Valid package terminal output | `evidence/04_package_validation.txt` | Ready: actual import and blank-input validation succeeded. |
| 5.1 | Required unit-test code | `test_emotion_detection.py` | Code ready: five required statements call the real service. |
| 5.2 | All required tests passed output | `evidence/05_required_live_tests.txt` | Pending: all five encountered HTTP 502. The separate 21 fixture tests passed. |
| 6.1 | Flask deployment code | `server.py` | Code ready; copy the complete file below. |
| 6.2 | Deployment screenshot | `evidence/6b_deployment_test.png` | Captured actual running interface with text entered; no real inference result yet. |
| 7.1 | HTTP 400 detector handling code | `EmotionDetection/emotion_detection.py` | Code ready: returns six None values for status 400. |
| 7.2 | Blank-input server handling code | `server.py` | Code ready: returns the required message with HTTP 400. |
| 7.3 | Error handling screenshot | `evidence/7c_error_handling_interface.png` | Ready: actual browser request returned HTTP 400 and the required message. |
| 8.1 | Server code after static analysis | `server.py` | Code ready, with module and function docstrings. |
| 8.2 | Perfect static-analysis terminal output | `evidence/08_pylint_server.txt` | Ready: actual Pylint result is 10.00/10, exit code 0. |

## Finish the live checks in your lab

Upload or extract the project files into your lab working directory, open a terminal there, and run:

```bash
python -m pip install -r requirements-dev.txt
python collect_evidence.py --live
```

After Watson is reachable, `evidence/02_03_live_detector.txt` must show the six-field dictionary and exit code 0. `evidence/05_required_live_tests.txt` must show five tests and `OK`. If either still reports HTTP 502, the service is still unavailable from that environment. Use a compatible endpoint supplied by the course if one is provided.

To generate the deployment screenshot with a genuine analysis result, run:

```bash
python server.py
```

Open the port-5000 application preview, enter `I am glad this happened`, and select **Analyze emotion**. When the scores and dominant emotion appear, capture the page and save it as `6b_deployment_test.png`. The existing file captures the deployed interface before analysis; `6c_service_unavailable.png` separately records the real service outage.

For the error screenshot, clear the text and select **Analyze emotion**. The page must show `Invalid text! Please try again!`. A genuine screenshot named `7c_error_handling_interface.png` is already included.

## Obtain your public GitHub links

Connect the GitHub integration to let the project be published to your account, or create a public repository yourself and upload the extracted project contents. Keep `EmotionDetection/__init__.py` and the other directory paths intact. Do not upload a virtual environment or Python cache files.

Open your repository's `README.md` on GitHub and copy its page URL for Task 1. Then open `EmotionDetection/__init__.py` and copy its page URL for Task 4. The following are templates only; replace both placeholders and the branch if needed. They are not existing links:

```text
https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY/blob/main/README.md
https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY/blob/main/EmotionDetection/__init__.py
```

## Detector code — Tasks 2.1, 3.1 and 7.1

Copy the same complete final implementation into each field requiring detector code.

```python
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
```

## Package initializer — Task 4.1

Publish this file and submit its GitHub URL, rather than the code alone.

```python
"""Watson NLP emotion detection package."""

from . import emotion_detection
from .emotion_detection import EmotionServiceError, emotion_detector

__all__ = ["emotion_detection", "emotion_detector", "EmotionServiceError"]
```

## Required unit tests — Task 5.1

```python
"""Required five live Watson tests; these need a reachable NLP service."""

import unittest

from EmotionDetection.emotion_detection import emotion_detector


class TestEmotionDetection(unittest.TestCase):
    """Validate the five statements specified in the course project."""

    def test_joy(self):
        """Recognize the expected joy statement."""
        self.assertEqual(
            emotion_detector("I am glad this happened")["dominant_emotion"], "joy"
        )

    def test_anger(self):
        """Recognize the expected anger statement."""
        self.assertEqual(
            emotion_detector("I am really mad about this")["dominant_emotion"], "anger"
        )

    def test_disgust(self):
        """Recognize the expected disgust statement."""
        result = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result["dominant_emotion"], "disgust")

    def test_sadness(self):
        """Recognize the expected sadness statement."""
        self.assertEqual(
            emotion_detector("I am so sad about this")["dominant_emotion"], "sadness"
        )

    def test_fear(self):
        """Recognize the expected fear statement."""
        result = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result["dominant_emotion"], "fear")


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## Flask server — Tasks 6.1, 7.2 and 8.1

```python
"""Serve the Emotion Detector interface and Watson-backed Flask endpoint."""

import os

from flask import Flask, Response, render_template, request

from EmotionDetection import EmotionServiceError, emotion_detector


APP = Flask(__name__)
INVALID_TEXT_MESSAGE = "Invalid text! Please try again!"


@APP.route("/")
def index():
    """Render the application's text-entry interface."""
    return render_template("index.html")


@APP.route("/emotionDetector", methods=["GET"])
def emotion_detector_route():
    """Return the required formatted result or a useful input/service error."""
    text_to_analyse = request.args.get("textToAnalyze", "")
    if not text_to_analyse.strip():
        return Response(INVALID_TEXT_MESSAGE, status=400, mimetype="text/plain")

    try:
        result = emotion_detector(text_to_analyse)
    except EmotionServiceError as error:
        APP.logger.warning("Emotion detection request failed: %s", error)
        return Response(
            "Emotion detection service is temporarily unavailable. Please try again.",
            status=503,
            mimetype="text/plain",
        )

    if result["dominant_emotion"] is None:
        return Response(INVALID_TEXT_MESSAGE, status=400, mimetype="text/plain")

    message = (
        "For the given statement, the system response is "
        f"'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, "
        f"'joy': {result['joy']}, "
        f"'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )
    return Response(message, mimetype="text/plain")


if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
```

## Package validation output — Task 4.2

This output validates the real package without requiring the unavailable NLP service.

```text
Captured: 2026-10-04T19:13:22.681137+00:00
$ /workspace/scratch/ca7f41d71a1d/emotion-runtime/bin/python -c 'from EmotionDetection import emotion_detection, emotion_detector; print('"'"'Package import: OK'"'"'); print('"'"'Module:'"'"', emotion_detection.__name__); print('"'"'Blank-input result:'"'"', emotion_detector('"'"''"'"'))'
Package import: OK
Module: EmotionDetection.emotion_detection
Blank-input result: {'anger': None, 'disgust': None, 'fear': None, 'joy': None, 'sadness': None, 'dominant_emotion': None}

Exit code: 0
```

## Static-analysis output — Task 8.2

```text
Captured: 2026-10-04T19:13:25.986614+00:00
$ /workspace/scratch/ca7f41d71a1d/emotion-runtime/bin/python -m pylint --persistent=n server.py

------------------------------------
Your code has been rated at 10.00/10


Exit code: 0
```

The local test output in `evidence/05_isolated_unit_tests.txt` is useful development evidence, but it cannot establish that the five real Watson predictions passed. Use the live-test log only after rerunning it successfully.
