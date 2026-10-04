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
