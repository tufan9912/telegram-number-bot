import logging
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8959721194:AAHNBxsCMryDJpiWc1Bcu3UEnFTDwVnv80g"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "👋 স্বাগতম!\n\n"
        "আপনার নাম্বারের লিস্টটি একবারে কপি করে এখানে পেস্ট করে দিন।\n"
        "বট স্বয়ংক্রিয়ভাবে প্রতি ১ সেকেন্ডে একটি করে নাম্বার পাঠানো শুরু করবে।"
    )

@dp.message(lambda message: any(char.isdigit() for char in message.text) and not message.text.startswith('/'))
async def handle_continuous_numbers(message: types.Message):
    numbers = re.findall(r'\+?\d{10,15}', message.text)
    
    if not numbers:
        await message.reply("❌ আপনার দেওয়া টেক্সটে কোনো সঠিক নাম্বার পাওয়া যায়নি।")
        return

    await message.reply(f"🚀 **{len(numbers)}টি** নাম্বার পাওয়া গেছে। অনবরত পাঠানো শুরু হচ্ছে...", parse_mode=ParseMode.MARKDOWN)
    
    for count, num in enumerate(numbers, 1):
        try:
            await message.answer(f"`{num}`", parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(1.0)
            
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await asyncio.sleep(5)
            
    await message.answer("✅ আপনার লিস্টের সব নাম্বার পাঠানো শেষ হয়েছে।")

async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
