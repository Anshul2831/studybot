import telebot
from telebot import types
from datetime import datetime
import json
import os

BOT_TOKEN = "8521138410:AAE7MSG_UGSTbSf9ZHp32BtQaFJcHJxD7d0"
bot = telebot.TeleBot(BOT_TOKEN)

# -------- File paths --------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ATTEND_FILE = os.path.join(DATA_DIR, "attendance.json")
FLOWER_FILE = os.path.join(DATA_DIR, "flowers.json")
WARNING_FILE = os.path.join(DATA_DIR, "warnings.json")

# -------- Load data --------
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

attendance = load_json(ATTEND_FILE)
flowers = load_json(FLOWER_FILE)
warnings = load_json(WARNING_FILE)
doubts = {}

# -------- Attendance --------
@bot.message_handler(commands=['present'])
def mark_present(msg):
    uid = str(msg.from_user.id)
    name = msg.from_user.first_name
    today = str(datetime.now().date())
    if uid not in attendance:
        attendance[uid] = []
    if today in attendance[uid]:
        bot.reply_to(msg, f"{name}, you are already marked present today.")
    else:
        attendance[uid].append(today)
        save_json(ATTEND_FILE, attendance)
        bot.reply_to(msg, f"✅ Attendance marked for {name} on {today}")

@bot.message_handler(commands=['attendance'])
def show_attendance(msg):
    uid = str(msg.from_user.id)
    count = len(attendance.get(uid, []))
    bot.reply_to(msg, f"📅 You have attended {count} days.")

# -------- Flowers --------
@bot.message_handler(commands=['flowers'])
def show_flowers(msg):
    uid = str(msg.from_user.id)
    count = flowers.get(uid, 0)
    bot.reply_to(msg, f"🌸 You have {count} flowers.")

# -------- Doubts --------
@bot.message_handler(commands=['doubt'])
def register_doubt(msg):
    uid = str(msg.from_user.id)
    doubts[uid] = msg.text.replace("/doubt", "").strip() or "No details"
    bot.reply_to(msg, f"🧠 Doubt registered. Others can help using /helpdoubt @{msg.from_user.username}")

@bot.message_handler(commands=['helpdoubt'])
def help_doubt(msg):
    bot.reply_to(msg, "If you solve someone’s doubt, they can send /like @username to reward you with 2 🌸 flowers.")

@bot.message_handler(commands=['like'])
def give_flower(msg):
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /like @username")
        return
    username = parts[1].lstrip('@')
    try:
        user = msg.entities[1].user
        uid = str(user.id)
    except Exception:
        bot.reply_to(msg, "⚠️ Invalid username or user not found.")
        return
    flowers[uid] = flowers.get(uid, 0) + 2
    save_json(FLOWER_FILE, flowers)
    bot.reply_to(msg, f"🌼 +2 flowers awarded to {username}!")

# -------- Leaderboard --------
@bot.message_handler(commands=['leaderboard'])
def leaderboard(msg):
    if not flowers:
        bot.reply_to(msg, "No flower data yet.")
        return
    sorted_lb = sorted(flowers.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 Flower Leaderboard:\n"
    for i, (uid, fcount) in enumerate(sorted_lb[:10], 1):
        text += f"{i}. {fcount} flowers\n"
    bot.reply_to(msg, text)

# -------- Quiz --------
@bot.message_handler(commands=['quiz'])
def quiz(msg):
    q = "📘 What is 8 × 7?"
    markup = types.InlineKeyboardMarkup()
    for opt in ['54', '56', '64']:
        markup.add(types.InlineKeyboardButton(opt, callback_data=opt))
    bot.send_message(msg.chat.id, q, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == '56':
        bot.answer_callback_query(call.id, "✅ Correct!")
    else:
        bot.answer_callback_query(call.id, "❌ Wrong answer.")

# -------- Moderation --------
@bot.message_handler(commands=['warn'])
def warn_user(msg):
    if not msg.reply_to_message:
        bot.reply_to(msg, "Reply to a user to warn them.")
        return
    uid = str(msg.reply_to_message.from_user.id)
    warnings[uid] = warnings.get(uid, 0) + 1
    save_json(WARNING_FILE, warnings)
    bot.reply_to(msg, f"⚠️ User warned. Total warnings: {warnings[uid]}")

# -------- Reminder --------
@bot.message_handler(commands=['remind'])
def remind(msg):
    bot.reply_to(msg, "📔 Reminder feature demo active (custom scheduling coming soon).")

# -------- Help --------
@bot.message_handler(commands=['help'])
def help_msg(msg):
    text = (
        "🧭 StudyBot Commands:\n"
        "/present – Mark attendance\n"
        "/attendance – Show attendance days\n"
        "/flowers – View your flowers\n"
        "/doubt – Register a doubt\n"
        "/helpdoubt – Guide for helpers\n"
        "/like @user – Reward solver with 2 flowers\n"
        "/leaderboard – Show top performers\n"
        "/quiz – Quick question\n"
        "/warn – Warn a user\n"
        "/remind – Simple reminder"
    )
    bot.reply_to(msg, text)

# -------- Run bot --------
print("✅ StudyBot is running...")
bot.polling()
