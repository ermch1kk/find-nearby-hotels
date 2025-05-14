import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from hotels import GooglePlacesHotelFinder

load_dotenv()

bot = Bot(
    token=os.getenv("TELEGRAM_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

finder = GooglePlacesHotelFinder()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Отправь мне адрес или название улицы, и я найду отели поблизости.")

@dp.message()
async def handle_address(message: Message):
    await message.answer("🔍 Ищу отели поблизости...")
    
    hotels = finder.find_nearby_hotels(message.text, radius=2000, max_results=5)
    if not hotels:
        await message.answer("😔 Отели не найдены.")
        return

    response = f"<b>🏨 Найдено отелей: {len(hotels)}</b>\n"
    for i, hotel in enumerate(hotels, 1):
        response += (
            f"\n<b>{i}. {hotel['name']}</b>\n"
            f"📍 <i>{hotel['address']}</i>\n"
            f"⭐ Рейтинг: {hotel.get('rating', 'нет данных')}\n"
            f"💰 Цены: {'$' * hotel.get('price_level', 0) if hotel.get('price_level') else 'нет данных'}\n"
        )

    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())