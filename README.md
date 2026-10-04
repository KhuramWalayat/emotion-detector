# Emotion Detector

An AI-based web application that analyzes English text with the Watson NLP
EmotionPredict service. It returns scores for anger, disgust, fear, joy and
sadness, together with the emotion having the largest score. A Flask application
provides a browser interface and the `/emotionDetector` endpoint.

This project extends the IBM Skills Network starter repository:
https://github.com/ibm-developer-skills-network/oaqjp-final-project-emb-ai
The original Apache-2.0 license is preserved in `LICENSE`.

## Run the application

Use Python 3.10 or later. From this project's directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python server.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.
Open http://127.0.0.1:5000. In a hosted Skills Network lab, use its application
preview for port 5000. The interface uses local CSS and JavaScript.

## Use the package

```python
from EmotionDetection.emotion_detection import emotion_detector

result = emotion_detector("I am glad this happened")
print(result)
```

The result contains `anger`, `disgust`, `fear`, `joy`, `sadness` and
`dominant_emotion`. All five scores come from Watson; this application does not
generate substitute model scores. Ties select the first emotion in the order
anger, disgust, fear, joy, sadness.

Blank input and a Watson HTTP 400 response produce all six fields set to `None`.
The web interface displays `Invalid text! Please try again!` with HTTP 400.
Network failures, other HTTP errors and malformed Watson responses raise
`EmotionServiceError`; the Flask endpoint handles these with HTTP 503.

The model ID is `emotion_aggregated-workflow_lang_en_stock`. The default endpoint
is `https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict`.
If your lab supplies a different compatible endpoint, set `WATSON_EMOTION_URL`
before starting Python. The request timeout is 15 seconds.

## Verification

Run the isolated client and Flask tests:

```bash
python -m unittest discover -s tests -v
```

These 21 tests use explicit response fixtures to check request construction,
score formatting, dominant-emotion selection, invalid input, HTTP errors,
timeouts, invalid payloads and Flask behavior. They do not run the NLP model.

Run the five course-required tests against the real Watson service:

```bash
python test_emotion_detection.py
```

Check static analysis:

```bash
python -m pylint server.py
```

Collect fresh terminal evidence automatically:

```bash
python collect_evidence.py --live
```

The collector saves unmodified command output and exit status in `evidence/`.
It exits with an error if any check fails. Omit `--live` for local checks only.
Package lint permits the course-required name `EmotionDetection` explicitly;
`server.py` receives its score without that naming option or disabled warnings.

## Evidence in this bundle

Local verification passed all 21 isolated tests. Pylint rated `server.py` at
10.00/10. Package imports and blank-input validation also succeeded.

The real Watson endpoint returned HTTP 502 during verification on 4 October
2026. The live detector call and all five required live tests therefore failed
with service errors. Their actual output is saved separately from the passing
fixture tests. No successful live inference is claimed.

`SUBMISSION_GUIDE.md` maps every rubric field to the source, output or screenshot
to use. The deployment screenshot shows the locally running interface; it must
be retaken with a successful real analysis once Watson is reachable. The blank
input screenshot validates genuine Flask error handling without a mock service.

Create a public repository under your own GitHub account before supplying the
README and `EmotionDetection/__init__.py` URLs. This bundle has not been
published to a user-owned GitHub repository.

## Files

```text
EmotionDetection/
    __init__.py
    emotion_detection.py
server.py
test_emotion_detection.py
tests/
    test_client.py
    test_server.py
templates/index.html
static/mywebscript.js
static/style.css
collect_evidence.py
requirements.txt
requirements-dev.txt
evidence/
SUBMISSION_GUIDE.md
LICENSE
```
