import os
import uuid
import time
import re
import cv2
import numpy as np
from flask import Flask, request, jsonify
from paddleocr import PaddleOCR

os.environ["FLAGS_use_mkldnn"] = "0"

app = Flask(__name__)

VERSION = "2.0.0"
ocr = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False)


def clean_text(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", value or "").upper()


def extract_result(result):
    texts = []
    confidences = []

    for line in result:
        if line:
            for item in line:
                texts.append(item[1][0])
                confidences.append(float(item[1][1]))

    text = clean_text("".join(texts))
    confidence = sum(confidences) / len(confidences) if confidences else 0

    return text, round(confidence, 4)


def response_success(text, confidence, start_time):
    return jsonify({
        "success": True,
        "text": text,
        "confidence": confidence,
        "elapsedMs": int((time.time() - start_time) * 1000),
        "version": VERSION
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "version": VERSION
    })


@app.route("/predict", methods=["POST"])
def predict():
    start_time = time.time()

    if "image" not in request.files:
        return jsonify({"success": False, "error": "image required", "version": VERSION}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"success": False, "error": "empty filename", "version": VERSION}), 400

    temp_path = f"/tmp/captcha_{uuid.uuid4().hex}.png"
    file.save(temp_path)

    try:
        result = ocr.ocr(temp_path, cls=False)
        text, confidence = extract_result(result)
        return response_success(text, confidence, start_time)

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": VERSION}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/ocr", methods=["POST"])
def ocr_bytes():
    start_time = time.time()

    data = request.get_data()

    if not data:
        return jsonify({"success": False, "error": "image body required", "version": VERSION}), 400

    try:
        image_array = np.frombuffer(data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"success": False, "error": "invalid image", "version": VERSION}), 400

        result = ocr.ocr(image, cls=False)
        text, confidence = extract_result(result)

        return response_success(text, confidence, start_time)

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": VERSION}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)