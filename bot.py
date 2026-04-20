import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8745151362:AAGRDdmYKFGBaP6MieXdNwZ4E9LZPcGy30Y"
GROUP_ID = -1003888459573 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users = {}
temp_data = {}

# 📞 kontakt
contact_btn = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
    resize_keyboard=True
)

# 🏠 menu
menu_btn = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚖 E’lon berish")]],
    resize_keyboard=True
)

# 📍 lokatsiya tugmalar
location_btn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)],
        [KeyboardButton(text="⏭ O‘tkazib yuborish")]
    ],
    resize_keyboard=True
)

# 🔄 states
class Form(StatesGroup):
    phone = State()
    elon = State()
    location = State()

# 🔗 user link
def get_link(user: types.User):
    if user.username:
        return f"https://t.me/{user.username}"
    return f"tg://user?id={user.id}"

def get_name(user: types.User):
    return user.username if user.username else user.full_name

# 🚀 start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if message.from_user.id in users:
        await message.answer("🏠 Bosh menyu:", reply_markup=menu_btn)
    else:
        await message.answer(
            "🚖 Salom Rishton–Bag‘dod–Toshkent taxi botiga xush kelibsiz!\n\n"
            "📲 Iltimos raqamingizni yuboring:\n\n"
            "📞 Asosiy shofyor: +998908311144",
            reply_markup=contact_btn
        )
        await state.set_state(Form.phone)

# 📞 raqam olish
@dp.message(Form.phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    users[message.from_user.id] = phone

    await message.answer(
        "✅ Raqamingiz saqlandi!\n\n🚖 Endi e’lon berishingiz mumkin:",
        reply_markup=menu_btn
    )
    await state.clear()

# 🚖 e’lon boshlash
@dp.message(F.text == "🚖 E’lon berish")
async def elon_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in users:
        await message.answer("❗ Avval /start bosing")
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
        reply_markup=location_btn
    )
    await state.set_state(Form.location)

# 📍 lokatsiya bilan yuborish
@dp.message(Form.location, F.location)
async def send_with_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = temp_data[user_id]["text"]
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
        f"🚖 YANGI E’LON\n\n📍 {text}\n\n📞 {phone}",
        reply_markup=kb
    )

    await bot.send_location(GROUP_ID, lat, lon)

    await message.answer(
        "✅ E’loningiz taxilar guruhiga yuborildi!\n\n"
        "⏳ Iltimos shofyor qabul qilishini kuting.",
        reply_markup=menu_btn
    )

    await state.clear()

# ⏭ skip
@dp.message(Form.location, F.text == "⏭ O‘tkazib yuborish")
async def skip_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = temp_data[user_id]["text"]
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
        "✅ E’loningiz taxilar guruhiga yuborildi!\n\n"
        "⏳ Iltimos shofyor qabul qilishini kuting.",
        reply_markup=menu_btn
    )

    await state.clear()

# ✅ qabul qilish
@dp.callback_query(F.data.startswith("accept_"))
async def accept_order(callback: types.CallbackQuery):
    driver = callback.from_user
    user_id = int(callback.data.split("_")[1])

    driver_name = get_name(driver)
    driver_link = get_link(driver)
    driver_phone = users.get(driver.id, "Noma’lum")

    # guruhda edit
    await callback.message.edit_text(
        callback.message.text +
        f"\n\n✅ Qabul qilindi: {driver_name}\n"
        f"🔗 {driver_link}\n\n❗ Iltimos bezovta qilmang"
    )

    # userga xabar
    try:
        await bot.send_message(
            user_id,
            f"🚖 Sizning e’loningizni {driver_name} qabul qildi!\n"
            f"🔗 {driver_link}\n\n📞 Shofyor raqami: {driver_phone}"
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