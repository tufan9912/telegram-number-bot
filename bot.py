import os
import time
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
from threading import Thread

# আপনার বটের টোকেন এখানে সফলভাবে যুক্ত আছে
BOT_TOKEN = "8534443499:AAGJloPwCkrkxG7VIuYK2vUNYqTg4cZqVxA"
TARGET_URL = "https://tempnumbers.blogspot.com/?m=1"

bot = telebot.TeleBot(BOT_TOKEN)

config = {
    "min_range": 0,
    "max_range": 100,
    "is_scanning": False,
    "last_count": 0,
    "admin_id": None
}

def fetch_numbers_count():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            numbers_found = soup.find_all(text=lambda text: text and '+' in text)
            if not numbers_found:
                numbers_found = soup.find_all('h3', class_='post-title')
            return len(numbers_found)
        return 0
    except Exception as e:
        return 0

def monitor_website():
    while True:
        if config["is_scanning"] and config["admin_id"]:
            current_count = fetch_numbers_count()
            config["last_count"] = current_count
            if config["min_range"] <= current_count <= config["max_range"]:
                bot.send_message(
                    config["admin_id"], 
                    f"🔔 **অ্যালার্ট! রেঞ্জের ভেতর নাম্বার পাওয়া গেছে!**\n\n"
                    f"📊 বর্তমান কাউন্ট: {current_count}\n"
                    f"🎯 আপনার সেট করা রেঞ্জ: {config['min_range']} - {config['max_range']}\n"
                    f"🌐 লিংক: {TARGET_URL}"
                )
        time.sleep(30)

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_status = types.KeyboardButton("📊 বর্তমান স্ট্যাটাস")
    btn_set_range = types.KeyboardButton("⚙️ রেঞ্জ সেট করুন")
    btn_start_scan = types.KeyboardButton("▶️ স্ক্যান শুরু")
    btn_stop_scan = types.KeyboardButton("🛑 স্ক্যান বন্ধ")
    markup.add(btn_status, btn_set_range, btn_start_scan, btn_stop_scan)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    config["admin_id"] = message.chat.id
    welcome_text = (
        "🔥 **TempNumbers Tracker Bot-এ স্বাগতম!**\n\n"
        "আমি এই সাইটটি মনিটর করব: https://tempnumbers.blogspot.com/?m=1\n\n"
        "নিচের মেনু ব্যবহার করে আপনার ম্যানুয়াল রেঞ্জ সেট করুন এবং স্ক্যানার অন করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.chat.id != config["admin_id"]:
        return
    if message.text == "📊 বর্তমান স্ট্যাটাস":
        current = fetch_numbers_count()
        status = "রানিং 🟢" if config["is_scanning"] else "বন্ধ 🔴"
        bot.reply_to(
            message,
            f"📈 **লাইভ আপডেট:**\n\n"
            f"🔹 সাইটে বর্তমান নাম্বার কাউন্ট: {current}\n"
            f"🔹 সেট করা রেঞ্জ: {config['min_range']} থেকে {config['max_range']}\n"
            f"🔹 স্ক্যানার স্ট্যাটাস: {status}",
            parse_mode="Markdown"
        )
    elif message.text == "⚙️ রেঞ্জ সেট করুন":
        msg = bot.reply_to(
            message, 
            "🔢 আপনার ম্যানুয়াল রেঞ্জ ফরম্যাট ইনপুট দিন।\n"
            "উদাহরণ: `10-50`",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_range_step)
    elif message.text == "▶️ স্ক্যান শুরু":
        config["is_scanning"] = True
        bot.reply_to(message, "🚀 ব্যাকগ্রাউন্ড স্ক্যানার চালু হয়েছে!")
    elif message.text == "🛑 স্ক্যান বন্ধ":
        config["is_scanning"] = False
        bot.reply_to(message, "🛑 স্ক্যানার সফলভাবে বন্ধ করা হয়েছে।")

def process_range_step(message):
    try:
        text = message.text
        low, high = map(int, text.split('-'))
        config["min_range"] = low
        config["max_range"] = high
        bot.reply_to(
            message, 
            f"✅ **\nরেঞ্জ সফলভাবে সেট হয়েছে!**\n"
            f"মিনিমাম: {low} | ম্যাক্সিমাম: {high}", 
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception:
        bot.reply_to(message, "❌ ভুল ফরম্যাট! দয়া করে এভাবে লিখুন: `10-50`", reply_markup=main_keyboard(), parse_mode="Markdown")

if __name__ == "__main__":
    monitor_thread = Thread(target=monitor_website)
    monitor_thread.daemon = True
    monitor_thread.start()
    bot.infinity_polling()
