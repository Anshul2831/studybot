import telebot
import json
from datetime import datetime

TOKEN = "8521138410:AAE7MSG_UGSTbSf9ZHp32BtQaFJcHJxD7d0"  # yahan apna Telegram bot token daalna hai
bot = telebot.TeleBot(TOKEN)

# ---------- Data Handling ----------
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ---------- Helper ----------
def ensure_user(user_id):
    if str(user_id) not in data:
        data[str(user_id)] = {
            "flowers": 0,
            "streak": 0,
            "longest_streak": 0,
            "last_active": None,
            "tdl": []
        }

# ---------- Commands ----------
@bot.message_handler(commands=['start'])
def start(msg):
    ensure_user(msg.from_user.id)
    bot.reply_to(msg, "✅ Study Bot activated. Type 'add <topic>' to add a task.")

@bot.message_handler(commands=['help'])
def help_cmd(msg):
    bot.reply_to(msg,
        "Commands:\n"
        "/start – activate bot\n"
        "/help – list commands\n"
        "Normal texts: add <topic>, done <topic>"
    )

# ---------- Text messages ----------
@bot.message_handler(func=lambda m: True)
def handle_text(msg):
    user_id = str(msg.from_user.id)
    ensure_user(user_id)

    text = msg.text.lower()

    # add topic
    if text.startswith("add "):
        topic = text[4:].strip()
        data[user_id]["tdl"].append({"task": topic, "done": False})
        save_data()
        bot.reply_to(msg, f"📝 Added: {topic}")

    # mark done
    elif text.startswith("done "):
        topic = text[5:].strip()
        for t in data[user_id]["tdl"]:
            if t["task"] == topic and not t["done"]:
                t["done"] = True
                data[user_id]["flowers"] += 5
                save_data()
                bot.reply_to(msg, f"✅ Completed {topic}! (+5 flowers)")
                break
        else:
            bot.reply_to(msg, "Topic not found.")

    else:
        bot.reply_to(msg, "Use 'add <topic>' or 'done <topic>'")

bot.polling()
