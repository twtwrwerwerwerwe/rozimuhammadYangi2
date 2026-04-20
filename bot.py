import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8745151362:AAGRDdmYKFGBaP6MieXdNwZ4E9LZPcGy30Y"
GROUP_ID = -1003888459573 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users = {}

# 📞 kontakt tugma
contact_btn = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
    resize_keyboard=True
)

# 🏠 menu
menu_btn = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚖 E’lon berish")]],
    resize_keyboard=True
)

# ⏭ skip
skip_btn = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭ O‘tkazib yuborish")]],
    resize_keyboard=True
)

# 🔄 states
class Form(StatesGroup):
    phone = State()
    elon = State()
    location = State()

# vaqtincha e’lon saqlash
temp_data = {}

# 🚀 START
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id in users:
        await message.answer("🏠 Bosh menyu:", reply_markup=menu_btn)
    else:
        await message.answer(
            "🚖 Salom Rishton–Bag‘dod–Toshkent taxi botiga xush kelibsiz!\n\n"
            "📲 Iltimos raqamingizni yuboring:\n\n"
            "📞 Asosiy shofyor: +998908311144",
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

# 🚖 e’lon boshlash
@dp.message(F.text == "🚖 E’lon berish")
async def elon_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in users:
        await message.answer("❗ Avval raqamingizni yuboring /start")
        return

    await message.answer(
        "✍️ Iltimos habaringizni yozing:",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Form.elon)

# 📝 e’lon matni
@dp.message(Form.elon)
async def get_elon(message: types.Message, state: FSMContext):
    temp_data[message.from_user.id] = {"text": message.text}

    await message.answer(
        "📍 Lokatsiya yuboring yoki o‘tkazib yuboring:",
        reply_markup=skip_btn
    )

    await state.set_state(Form.location)

# 📍 lokatsiya bilan
@dp.message(Form.location, F.location)
async def get_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = temp_data.get(user_id)

    text = data["text"]
    phone = users[user_id]

    lat = message.location.latitude
    lon = message.location.longitude

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{user_id}")]
        ]
    )

    msg = await bot.send_message(
        GROUP_ID,
        f"🚖 YANGI E’LON\n\n📍 {text}\n\n📞 {phone}"
    )

    await bot.send_location(GROUP_ID, lat, lon)

    await bot.send_message(GROUP_ID, "👇", reply_markup=kb)

    await message.answer(
        "✅ E’loningiz yuborildi!\n\n⏳ Javobni kuting.\n\n🚖 Yana e’lon berishingiz mumkin:",
        reply_markup=menu_btn
    )

    await state.clear()

# ⏭ skip
@dp.message(Form.location, F.text == "⏭ O‘tkazib yuborish")
async def skip_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = temp_data.get(user_id)

    text = data["text"]
    phone = users[user_id]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{user_id}")]
        ]
    )

    await bot.send_message(
        GROUP_ID,
        f"🚖 YANGI E’LON\n\n📍 {text}\n\n📞 {phone}",
        reply_markup=kb
    )

    await message.answer(
        "✅ E’loningiz yuborildi!\n\n⏳ Javobni kuting.\n\n🚖 Yana e’lon berishingiz mumkin:",
        reply_markup=menu_btn
    )

    await state.clear()

# ✅ qabul qilish
@dp.callback_query(F.data.startswith("accept_"))
async def accept_order(callback: types.CallbackQuery):
    driver = callback.from_user
    user_id = int(callback.data.split("_")[1])

    phone = users.get(user_id)

    name = driver.username if driver.username else driver.full_name

    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ Qabul qilindi: @{name}"
    )

    # yo‘lovchiga habar
    try:
        await bot.send_message(
            user_id,
            f"🚖 Sizning e’loningizni @{name} qabul qildi!\n\n📞 Bog‘laning: {phone}"
        )
    except:
        pass

    await callback.answer("Qabul qilindi!")

# ▶️ run
async def main():
    print("Bot ishga tushdi 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())