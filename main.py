import json
import logging
import asyncio
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import CommandStart

TOKEN = "7736731524:AAFggiyBAEbp2g_9uNmU7JQXz9rvdvk_GAo"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Завантаження товарів
with open("data.json", encoding="utf-8") as f:
    products = json.load(f)

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📦 Всі товари")
    kb.button(text="🔍 Пошук за номером")
    return kb.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Вітаю! Я бот для продажу автозапчастин.\nОберіть опцію нижче 👇",
        reply_markup=main_menu()
    )

@dp.message(F.text == "📦 Всі товари")
async def show_all_products(message: Message):
    for product in products:
        caption = (
            f"<b>{product['name']}</b>\n"
            f"💬 {product['description']}\n"
            f"💰 {product['price']}"
        )
        btn = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Зв'язатися", url="https://t.me/olegka_la")]
            ]
        )
        await message.answer_photo(photo=product["photo"], caption=caption, reply_markup=btn)

@dp.message(F.text == "🔍 Пошук за номером")
async def ask_for_part_number(message: Message):
    await message.answer("🔎 Введіть номер запчастини або його частину:")

@dp.message()
async def search_by_number(message: Message):
    query = message.text.lower()
    results = []

    for product in products:
        part_numbers = product.get("part_numbers") or [product.get("part_number")]
        if part_numbers:
            if any(query in pn.lower() for pn in part_numbers if pn):
                results.append(product)

    if not results:
        await message.answer("🚫 Нічого не знайдено.")
        return

    for product in results:
        caption = (
            f"<b>{product['name']}</b>\n"
            f"💬 {product['description']}\n"
            f"💰 {product['price']}"
        )
        btn = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Зв'язатися", url="https://t.me/olegka_la")]
            ]
        )
        await message.answer_photo(photo=product["photo"], caption=caption, reply_markup=btn)

# Replit http-сервер
async def on_startup(app):
    logging.info("Starting bot polling...")
    asyncio.create_task(dp.start_polling(bot))

async def handle_root(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle_root)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import os
    port = int(os.environ.get("PORT", 3000))
    web.run_app(app, host="0.0.0.0", port=port)
