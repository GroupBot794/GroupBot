import telebot
from flask import Flask
import threading
import requests
import os
import time

API_TOKEN = os.getenv("API_TOKEN", "YOUR_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "-1002725702609"))
API_URL = os.getenv("API_URL", "http://103.20.103.139:3080/api/hit?key=ditmehtddtrantuananh")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

def analyze_md5_hitclub(md5_str):
    if len(md5_str) != 32:
        return {"error": "MD5 không hợp lệ"}
    hex_12 = md5_str[:8] + md5_str[-4:]
    dec = int(hex_12, 16)
    ratio = dec / 281474976710656  # 16^12
    percent = round(ratio * 100, 2)
    result = "Xỉu" if ratio < 0.5 else "Tài"
    return {
        "hex": hex_12,
        "dec": dec,
        "ratio": ratio,
        "percent": percent,
        "result": result
    }

def format_hitclub_message(prev_session, prev_dice, prev_result, current_session, current_md5):
    dice_emoji = {1:"🎲 1", 2:"🎲 2", 3:"🎲 3", 4:"🎲 4", 5:"🎲 5", 6:"🎲 6"}
    dice_str = ' '.join([dice_emoji.get(d, str(d)) for d in prev_dice])
    total = sum(prev_dice)
    analysis = analyze_md5_hitclub(current_md5)
    percent_tai = analysis['percent']
    percent_xiu = round(100 - percent_tai, 2)
    priority = "Tài" if percent_tai >= 50 else "Xỉu"
    icon_priority = "🔵" if priority == "Tài" else "🔴"
    dec_formatted = f"{analysis['dec']:,}"

    return f"""🎯 𝗕𝗢𝗧 𝗣𝗛Â𝗡 𝗧Í𝗖𝗛 𝗛𝗜𝗧𝗖𝗟𝗨𝗕
━━━━━━━━━━━━━━━━━━━━━━
🔙 𝗣𝗵𝗶𝗲̂𝗻 𝗧𝗿𝘂̛𝗼̛́𝗰: #{prev_session}
🎲 𝗫𝘂́𝗰 𝘅ắ𝗰: {dice_str}
➕ 𝗧𝗼̂̉𝗻𝗴: {total}
🏁 𝗞𝗲̂́𝘁 𝗾𝘂𝗮̉: {'🔵' if prev_result == 'Tài' else '🔴'} {prev_result}
━━━━━━━━━━━━━━━━━━━━━━
📌 𝗣𝗵𝗶𝗲̂𝗻 𝗛𝗶𝗲̣̂𝗻 𝗧𝗮̣𝗶: #{current_session}
🔐 𝗠𝗮̃ 𝗠𝗗𝟱: `{current_md5}`
🧮 𝗛𝗲𝘅 𝟭𝟮: `{analysis['hex']}`
📉 𝗧𝗵𝗮̣̂𝗽 𝗽𝗵â𝗻: {dec_formatted}
📊 𝗧ỉ 𝗟ệ:
┣ 📈 Tài: {percent_tai}%
┣ 📉 Xỉu: {percent_xiu}%
┗ 🎯 Ưu tiên: {icon_priority} {priority}
━━━━━━━━━━━━━━━━━━━━━━
⏳ 𝗖𝗵𝗼̛̀ 𝗽𝗵𝗶𝗲̂𝗻 𝘁𝗶𝗲̂́𝗽 𝘁𝗵𝗲𝗼...
"""

last_session = 0

def auto_fetch_and_send():
    global last_session
    while True:
        try:
            res = requests.get(API_URL)
            data = res.json()
            if data["current_session"] != last_session:
                msg = format_hitclub_message(
                    data["current_session"],
                    data["current_dice"],
                    data["current_result"],
                    data["next_session"],
                    data["current_md5"]
                )
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                last_session = data["current_session"]
        except Exception as e:
            print(f"Lỗi: {e}")
        time.sleep(5)

@bot.message_handler(commands=["test", "check"])
def handle_test(message):
    if str(message.chat.id) == str(CHAT_ID):
        try:
            res = requests.get(API_URL)
            data = res.json()
            msg = format_hitclub_message(
                data["current_session"],
                data["current_dice"],
                data["current_result"],
                data["next_session"],
                data["current_md5"]
            )
            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(CHAT_ID, f"Lỗi khi gọi API: {e}")

@app.route("/")
def home():
    return "✅ Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=auto_fetch_and_send).start()
    run_bot()