from flask import Flask, render_template, request, jsonify, send_file
from ultralytics import YOLO
from report import create_excel_report

import os
import cv2
import json
import time
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "static/results"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER

model = YOLO("yolov8n.pt")

BAGGAGE_CLASSES = ["suitcase", "backpack", "handbag"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "Файл не найден"})

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Файл не выбран"})

    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(upload_path)

    img = cv2.imread(upload_path)

    start_time = time.time()
    results = model(img)
    processing_time = round(time.time() - start_time, 3)

    baggage_count = 0

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        if class_name in BAGGAGE_CLASSES:
            baggage_count += 1

    output_img = results[0].plot()

    result_filename = "result.jpg"
    result_path = os.path.join(app.config["RESULT_FOLDER"], result_filename)
    cv2.imwrite(result_path, output_img)

    history_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": file.filename,
        "count": baggage_count,
        "processing_time": processing_time,
        "model": "YOLOv8n",
        "result_image": "/" + result_path
    }

    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history.append(history_record)

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    return jsonify({
        "message": "Обработка завершена",
        "count": baggage_count,
        "processing_time": processing_time,
        "model": "YOLOv8n",
        "result_image": "/" + result_path
    })


@app.route("/export")
def export_excel():
    create_excel_report()
    return send_file(
        "history.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)