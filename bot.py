import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# 🔑 TOKEN (yangisini qo'ying!)
BOT_TOKEN = "8745151362:AAGRDdmYKFGBaP6MieXdNwZ4E9LZPcGy30Y"
GROUP_ID = -1003888459573 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 👤 oddiy saqlash (DB o‘rniga)
users = {}

# 📞 kontakt tugma
contact_btn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True
)

# 🏠 menu
menu_btn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚖 E’lon berish")]
    ],
    resize_keyboard=True
)

# 🔄 states
class Form(StatesGroup):
    phone = State()
    elon = State()

# 🚀 START
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id in users:
        await message.answer("🏠 Bosh menyu:", reply_markup=menu_btn)
    else:
        await message.answer(
            "🚖 Salom Rishton–Bag‘dod–Toshkent taxi botiga xush kelibsiz!\n\n"
            "📲 Iltimos raqamingizni yuboring:",
            "📞 Asosiy shopirga aloqaga chiqsangiz ham bo'ladi +998908311144",
            reply_markup=contact_btn
        )
        await state.set_state(Form.phone)

# 📞 contact olish
@dp.message(Form.phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number

    if not phone.startswith("+"):
        phone = "+" + phone

    users[user_id] = phone

    await message.answer(
        "✅ Raqamingiz saqlandi!\n\n🚖 Endi e’lon berishingiz mumkin:",
        reply_markup=menu_btn
    )
    await state.clear()

# 🚖 e’lon tugmasi
@dp.message(F.text == "🚖 E’lon berish")
async def elon_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in users:
        await message.answer("❗ Avval raqamingizni yuboring /start")
        return

    # 🔥 MUHIM: tugma yo‘qoladi
    await message.answer(
        "✍️ Iltimos habaringizni yozing:",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Form.elon)

# 📨 e’lon yuborish
@dp.message(Form.elon)
async def send_elon(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    phone = users.get(user_id)

    final_text = (
        "🚖 *YANGI E’LON*\n\n"
        f"📍 {text}\n\n"
        f"📞 Telefon: {phone}\n\n"
        "🟢 Tezda bog‘laning!"
    )

    await bot.send_message(
        chat_id=GROUP_ID,
        text=final_text,
        parse_mode="Markdown"
    )

    await message.answer(
        "✅ E’loningiz yuborildi!\n\n"
        "⏳ Javobni kuting.\n\n"
        "🚖 Yana e’lon berishingiz mumkin:",
        reply_markup=menu_btn
    )

    await state.clear()

# ▶️ run
async def main():
    print("Bot ishga tushdi 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())