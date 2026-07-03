import os
import uuid
import time
from flask import Flask, request, jsonify
from paddleocr import PaddleOCR

os.environ["FLAGS_use_mkldnn"] = "0"

app = Flask(__name__)

ocr = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False)
VERSION = "1.0.0"


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
        return jsonify({
            "success": False,
            "error": "image required"
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "empty filename"
        }), 400

    temp_path = f"temp_{uuid.uuid4().hex}.png"
    file.save(temp_path)

    try:
        result = ocr.ocr(temp_path, cls=False)

        texts = []
        confidences = []

        for line in result:
            if line:
                for item in line:
                    text_value = item[1][0]
                    confidence_value = float(item[1][1])

                    texts.append(text_value)
                    confidences.append(confidence_value)

        text = "".join(texts).replace(" ", "").strip()
        confidence = sum(confidences) / len(confidences) if confidences else 0

        elapsed_ms = int((time.time() - start_time) * 1000)

        return jsonify({
            "success": True,
            "text": text,
            "confidence": round(confidence, 4),
            "elapsedMs": elapsed_ms,
            "version": VERSION
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "version": VERSION
        }), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)