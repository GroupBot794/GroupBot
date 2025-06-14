import requests
import time
from flask import Flask
from threading import Thread
import telebot
import os

# LẤY TOKEN VÀ CHAT_ID TỪ BIẾN MÔI TRƯỜNG
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

API_URL = "http://103.20.103.139:3001/api/b52?key=ditmehtddtrantuananh"

bot = telebot.TeleBot(BOT_TOKEN)

# Flask giữ cho Railway không tắt
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Tài Xỉu đang chạy..."

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Thuật toán phân tích MD5 chi tiết
def analyze_md5_detailed(md5_hash: str):
    digit_values = [int(c, 16) for c in md5_hash if c.isdigit()]
    letter_values = [ord(c) for c in md5_hash if c.isalpha()]
    if not digit_values and not letter_values:
        return "Xỉu", 0.0, 100.0
    elif not digit_values:
        return "Xỉu", 0.0, 100.0
    elif not letter_values:
        return "Tài", 100.0, 0.0

    digit_sum = sum(digit_values)
    letter_sum = sum(letter_values)
    xor_digit = 0
    for d in digit_values: xor_digit ^= d
    xor_letter = 0
    for l in letter_values: xor_letter ^= l
    squared_digit = sum(x**2 for x in digit_values) % 100
    squared_letter = sum(x**2 for x in letter_values) % 100
    hex_blocks = [int(md5_hash[i:i+4], 16) for i in range(0, len(md5_hash), 4)]
    hex_weighted = sum((i+1)*v for i, v in enumerate(hex_blocks)) % 100
    even = sum(1 for x in digit_values if x % 2 == 0)
    odd = len(digit_values) - even

    score = (
        (digit_sum * 2) + letter_sum +
        (xor_digit * 3) + xor_letter +
        (squared_digit * 2) + squared_letter +
        hex_weighted + (even * 5) - (odd * 3)
    ) % 100

    result = "Tài" if score % 2 == 0 else "Xỉu"
    return result, float(score), 100.0 - float(score)

# Gửi kết quả tự động
def auto_send():
    last_session = None
    while True:
        try:
            res = requests.get(API_URL)
            data = res.json()
            session = data.get("current_session")
            md5 = data.get("current_md5", "")
            result = data.get("current_result", "")
            pattern = data.get("used_pattern", "")

            if session != last_session:
                last_session = session
                pred, pt, px = analyze_md5_detailed(md5)
                next_pred = "TÀI" if pattern[-1:] == "X" else "XỈU"

                msg = (
                    f"<b>🎯 PHIÊN:</b> <code>{session}</code>\n"
                    f"<b>🔢 MD5:</b> <code>{md5}</code>\n"
                    f"<b>🏁 API:</b> <b>{result.upper()}</b>\n\n"
                    f"<b>🧠 PHÂN TÍCH:</b> <b>{pred}</b>\n"
                    f"📊 Tài: <b>{pt:.1f}%</b> | Xỉu: <b>{px:.1f}%</b>\n"
                    f"<b>📈 PATTERN:</b> <code>{pattern}</code>\n"
                    f"<b>🔮 DỰ ĐOÁN SAU:</b> <b>{next_pred}</b>\n"
                    f"<b>👑 ADMIN:</b> <b>ExTaiXiu - MR DANEl</b>\n"
                    f"<i>🤖 Auto update mỗi 5 giây</i>"
                )
                bot.send_message(CHAT_ID, msg, parse_mode="HTML")
            time.sleep(5)
        except Exception as e:
            print("Lỗi:", e)
            time.sleep(10)

# Khởi chạy bot + Flask
if __name__ == '__main__':
    Thread(target=run_flask).start()
    Thread(target=auto_send).start()
