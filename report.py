from openpyxl import Workbook
import json
import os


def create_excel_report():
    wb = Workbook()
    ws = wb.active
    ws.title = "История обработки"

    ws.append([
        "Дата и время",
        "Имя файла",
        "Количество багажа",
        "Путь к изображению"
    ])

    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)

        for item in history:
            ws.append([
                item["timestamp"],
                item["filename"],
                item["count"],
                item["result_image"]
            ])

    wb.save("history.xlsx")