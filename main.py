from flask import Flask
from threading import Thread
import telebot
from telebot import types
import json
import random
import os

API_TOKEN = '7733569611:AAHPhutJQdFfnMAtl70yRLOaGl-uOnlVsKc'
ADMIN_ID = 7642384504  # Thay bằng Telegram ID của admin

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
DATA_FILE = "users.json"

# Tạo file dữ liệu nếu chưa có
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# Hàm đọc dữ liệu
def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Hàm ghi dữ liệu
def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Tạo mã chuyển khoản
def generate_transfer_code(user_id):
    return f"EX{user_id}{random.randint(100,999)}"

# Giao diện chính
def main_keyboard(user_id):
    data = read_data()
    user = data.get(str(user_id), {"xu": 0})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💹 Phân Tích", "💸 Mua Xu")
    markup.row("👤 Thông Tin User")
    if user_id == ADMIN_ID:
        markup.row("📢 Thông Báo All", "➕ Nạp Xu")
    return markup

# /start
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    data = read_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"xu": 0}
        write_data(data)

    name = message.from_user.first_name
    text = (
        "<b>🤖 Bot Phân Tích Tài Xỉu MD5</b>\n"
        "——————————————\n"
        "<b>Phiên Bản:</b> Premium\n"
        f"<b>Xin Chào User:</b> <code>{name}</code> Đến Với Bot Của Tôi\n"
        "<b>ADMIN:</b> <a href='https://t.me/ExTaiXiu2010'>t.me/ExTaiXiu2010</a>\n"
        "<b>Name:</b> ExTaiXiu\n"
        "<b>Bot Phân Tích Tỉ Lệ Cao</b>\n"
        "——————————————\n"
        "👉 Vui lòng chọn chức năng..."
    )
    bot.send_message(user_id, text, parse_mode="HTML", reply_markup=main_keyboard(user_id))

# Phân tích MD5
@bot.message_handler(func=lambda m: m.text == "💹 Phân Tích")
def prompt_md5(message):
    bot.send_message(message.chat.id,
        "<b>📊 Phân Tích Tài Xỉu MD5 PREMIUM</b>\n"
        "——————————————\n"
        "Vui Lòng Nhập Mã MD5:\n"
        "Bot Sẽ Ra Kết Quả Tài/Xỉu\n"
        "Tỉ Lệ Cao 82-88%\n"
        "——————————————\n"
        "⏳ Đang Chờ Mã MD5....",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(message, analyze_md5_step)

def analyze_md5_hitclub(md5_str):
    if len(md5_str) != 32:
        return {"error": "MD5 không hợp lệ", "md5": md5_str}
    hex_12 = md5_str[:8] + md5_str[-4:]
    dec = int(hex_12, 16)
    ratio = dec / 281474976710656
    percent = round(ratio * 100, 2)
    result = "Xỉu" if ratio < 0.5 else "Tài"
    return {
        "md5": md5_str,
        "percent_tai": percent,
        "percent_xiu": round(100 - percent, 2),
        "result": result
    }

def analyze_md5_step(message):
    md5 = message.text.strip()
    user_id = str(message.from_user.id)
    data = read_data()
    if data[user_id]["xu"] <= 0:
        bot.send_message(message.chat.id, "❌ Bạn không đủ xu để phân tích. Vui lòng mua thêm xu.")
        return
    data[user_id]["xu"] -= 1
    write_data(data)
    result = analyze_md5_hitclub(md5)
    if "error" in result:
        bot.send_message(message.chat.id, f"❌ {result['error']}")
        return
    bot.send_message(message.chat.id,
        f"<b>🎯 Phân Tích Thành Công</b>\n"
        "——————————————\n"
        "<b>Thể Loại:</b> Tài Xỉu MD5\n"
        "<b>Phiên Bản:</b> Premium\n"
        f"<b>Mã:</b> <code>{result['md5']}</code>\n"
        "<b>Tỉ Lệ:</b>\n"
        f"┣ 📈 Tài: {result['percent_tai']}%\n"
        f"┣ 📉 Xỉu: {result['percent_xiu']}%\n"
        f"┗ 🎯 Kết quả: {'🔵 Tài' if result['result'] == 'Tài' else '🔴 Xỉu'}\n"
        "——————————————\n"
        "⏳ Chờ Mã MD5 Tiếp Theo....",
        parse_mode="HTML"
    )

# Mua Xu
@bot.message_handler(func=lambda m: m.text == "💸 Mua Xu")
def buy_xu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("10.000 = 10 xu", "20.000 = 22 xu")
    markup.row("50.000 = 58 xu", "80.000 = 90 xu")
    markup.row("100.000 = 115 xu", "⬅️ Quay Lại")
    bot.send_message(message.chat.id, "🎁 Chọn gói xu bạn muốn mua:", reply_markup=markup)

@bot.message_handler(func=lambda m: "xu" in m.text.lower() and "=" in m.text)
def xu_selected(message):
    xu = message.text
    user_id = message.from_user.id
    code = generate_transfer_code(user_id)
    msg = (
        f"<b>BẠN ĐÃ CHỌN GÓI XU:</b> {xu}\n"
        "——————————————\n"
        "<b>Ngân hàng:</b> MB Bank\n"
        "<b>STK:</b> 0868848709\n"
        "<b>Tên:</b> Nguyễn Hoàng Minh Nhật\n"
        f"<b>Nội dung:</b> {code}\n"
        "——————————————\n"
        "<b>Vui Lòng Chuyển Vào Tài Khoản Trên</b>\n"
        "⚠️ <i>Kiểm Tra: Tên, Ngân Hàng, Số Tiền và Nội Dung Chuyển Khoản</i>\n"
        "⚠️ <i>Sẽ Không Chịu Trách Nhiệm Nếu Có Sai Sót</i>\n"
        "——————————————\n"
        "<b>Thông Tin Hỗ Trợ:</b>\n"
        "📨 Telegram: @ExTaiXiu2010\n"
        "📞 Zalo: 0362319474"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Đã chuyển khoản", callback_data=f"da_chuyen:{xu}:{code}"))
    bot.send_message(user_id, msg, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("da_chuyen"))
def handle_chuyen(call):
    parts = call.data.split(":")
    xu, code = parts[1], parts[2]
    user = call.from_user
    bot.send_message(ADMIN_ID,
        f"💳 <b>Đã Gửi Thông Tin Mua Hàng</b>\n"
        f"Gói: {xu}\n"
        f"User: {user.first_name} - ID: {user.id}\n"
        f"Nội dung chuyển khoản: <code>{code}</code>",
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id, "Đã gửi thông tin đến admin.")

# Nạp Xu (ADMIN)
@bot.message_handler(func=lambda m: m.text == "➕ Nạp Xu" and m.from_user.id == ADMIN_ID)
def nap_xu_admin(message):
    bot.send_message(ADMIN_ID, "💬 Gửi ID người dùng và số xu muốn nạp (vd: 123456 50):")
    bot.register_next_step_handler(message, handle_nap)

def handle_nap(message):
    try:
        uid, amount = message.text.strip().split()
        uid, amount = str(uid), int(amount)
        data = read_data()
        if uid not in data:
            data[uid] = {"xu": 0}
        data[uid]["xu"] += amount
        write_data(data)
        bot.send_message(uid, f"🎉 <b>Thông Báo Mua Xu</b>\nAdmin đã gửi bạn {amount} xu.\n❤️ Cảm Ơn Bạn ĐÃ Ủng Hộ!", parse_mode="HTML")
        bot.send_message(ADMIN_ID, "✅ Đã nạp thành công.")
    except:
        bot.send_message(ADMIN_ID, "❌ Lỗi cú pháp. Gửi lại: <ID> <số xu>")

# Thông Tin User
@bot.message_handler(func=lambda m: m.text == "👤 Thông Tin User")
def info_user(message):
    user_id = str(message.from_user.id)
    data = read_data()
    xu = data.get(user_id, {}).get("xu", 0)
    bot.send_message(message.chat.id, f"🧾 ID: <code>{user_id}</code>\n💰 Xu: {xu}", parse_mode="HTML")

# Thông Báo All (Admin)
@bot.message_handler(func=lambda m: m.text == "📢 Thông Báo All" and m.from_user.id == ADMIN_ID)
def notify_all(message):
    bot.send_message(ADMIN_ID, "✉️ Gửi nội dung bằng lệnh: /tb <nội dung>")

@bot.message_handler(commands=["tb"])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text[4:]
    data = read_data()
    for uid in data:
        try:
            bot.send_message(uid, f"📢 <b>THÔNG BÁO</b>\n{text}", parse_mode="HTML")
        except:
            pass
    bot.send_message(ADMIN_ID, "✅ Đã gửi đến tất cả user.")

# Quay lại
@bot.message_handler(func=lambda m: m.text == "⬅️ Quay Lại")
def back_menu(message):
    bot.send_message(message.chat.id, "🔙 Quay lại menu chính:", reply_markup=main_keyboard(message.from_user.id))

# Flask cho Render
@app.route('/')
def index():
    return "Bot đang chạy..."

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def keep_alive():
    Thread(target=run).start()

# Bắt đầu bot
if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)