"use strict";

const form = document.getElementById("emotionForm");
const textInput = document.getElementById("textToAnalyze");
const button = document.getElementById("analyseButton");
const resultPanel = document.getElementById("resultPanel");
const resultStatus = document.getElementById("resultStatus");
const result = document.getElementById("system_response");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    button.disabled = true;
    resultPanel.dataset.state = "loading";
    resultStatus.textContent = "Analyzing";
    result.textContent = "Reading the emotion in your words…";

    try {
        const parameters = new URLSearchParams({textToAnalyze: textInput.value});
        const response = await fetch(`/emotionDetector?${parameters.toString()}`);
        const message = await response.text();
        result.textContent = message;
        resultPanel.dataset.state = response.ok ? "success" : "error";
        resultStatus.textContent = response.ok
            ? "Analysis complete"
            : response.status === 400 ? "Check your input" : "Service unavailable";
    } catch (error) {
        resultPanel.dataset.state = "error";
        resultStatus.textContent = "Connection unavailable";
        result.textContent = "Unable to reach the application. Please try again.";
    } finally {
        button.disabled = false;
    }
});
