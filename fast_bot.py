import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# রেন্ডারের ফেক পোর্টের জন্য ব্যাকগ্রাউন্ড সার্ভার সেটিংস
async def handle(request):
    return web.Response(text="Bot is running perfectly!")

async def start_background_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # রেন্ডার ফ্রি প্ল্যানে $PORT$ এনভায়রনমেন্ট ভ্যারিয়েবল ব্যবহার করে, সেটি রিড করা হচ্ছে
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Fake Web Server started on port {port}")

# --- টেলিগ্রাম বট কনফিগারেশন ---
TOKEN = os.environ.get("BOT_TOKEN") # আপনার বটের টোকেন এনভায়রনমেন্টে সেট করা থাকতে হবে
if not TOKEN:
    # যদি ভ্যারিয়েবলে না থাকে তবে এখানে আপনার আসল টোকেনটি বসিয়ে দিতে পারেন
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ১. /start কমান্ড
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 হ্যালো ভাই!\n"
        "আমি আপনার নাম্বার বুট। আপনার নাম্বারের লিস্টটি পাঠিয়ে দিন, আমি ঝড়ের গতিতে কাজ শুরু করে দেব।\n\n"
        "সহযোগিতার জন্য টাইপ করুন: /help"
    )

# ২. /help কমান্ড
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ **সাহায্য মেনু:**\n"
        "১. আপনার নাম্বারগুলো একটি লিস্ট আকারে বটের চ্যাটে পাঠান।\n"
        "২. বট স্বয়ংক্রিয়ভাবে একটির পর একটি নম্বর প্রসেস করে আপনাকে আপডেট দেবে।\n"
        "৩. কোনো সমস্যা হলে বা বট রিস্টার্ট করতে /start চাপুন।"
    )

# ৩. নাম্বার প্রসেস করার মেইন লজিক (যা এখন অনেক ফাস্ট কাজ করবে)
@dp.message()
async def process_numbers(message: Message):
    text = message.text.strip()
    if not text:
        return

    # লাইন ব্রেক বা স্পেস দিয়ে নাম্বারগুলো আলাদা করা হচ্ছে
    numbers = [num.strip() for num in text.splitlines() if num.strip()]
    total_numbers = len(numbers)

    if total_numbers == 0:
        return

    await message.answer(f"🚀 {total_numbers}টি নাম্বার পাওয়া গেছে। অনবরত পাঠানো শুরু হচ্ছে...")

    # একেকটি নাম্বার প্রসেস করার লুপ
    for num in numbers:
        # এখানে আপনার মূল কাজের লজিক থাকবে (যেমন API রিকোয়েস্ট বা মেসেজ ফরওয়ার্ড)
        # উদাহরণস্বরূপ ইউজারকে নাম্বারটি ব্যাক পাঠানো হচ্ছে:
        await message.answer(f"{num}")
        
        # 'টিকটিক করে আস্তে আসার' সমস্যা দূর করতে ডিলে টাইম কমিয়ে মাত্র ০.৫ সেকেন্ড করা হয়েছে
        # টেলিগ্রামের স্প্যাম ফিল্টার এড়াতে ন্যূনতম একটু গ্যাপ রাখা নিরাপদ
        await asyncio.sleep(0.5) 

    await message.answer("✅ আপনার লিস্টের সব নাম্বার পাঠানো শেষ হয়েছে।")

# মেইন রান ফাংশন যা বট এবং ফেক সার্ভার একসাথে চালাবে
async def main():
    # ব্যাকগ্রাউন্ডে ফেক ওয়েব সার্ভার চালু করা হচ্ছে যাতে রেন্ডার টাইম আউট না করে
    await start_background_server()
    
    # টেলিগ্রাম বট পোলিং চালু
    print("Bot polling started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
