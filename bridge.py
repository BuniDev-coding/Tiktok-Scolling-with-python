from flask import Flask, request
from flask_cors import CORS
import pyautogui

app = Flask(__name__)
CORS(app)

@app.route('/scroll', methods=['POST'])
def scroll():
    direction = request.json.get('direction')
    if direction == 'up':
        pyautogui.press('down') # ปัดมือขึ้น = เลื่อนลง (คลิปถัดไป)
        print(">> NEXT")
    elif direction == 'down':
        pyautogui.press('up')   # ปัดมือลง = เลื่อนขึ้น (คลิปก่อนหน้า)
        print("<< PREV")
    return {"status": "ok"}

if __name__ == '__main__':
    print("Bridge Ready! (Waiting for Browser AI...)")
    app.run(port=5000)
