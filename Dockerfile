# 🐍 Python base image
FROM python:3.11-slim

# 📁 ish papkasi
WORKDIR /app

# 📦 requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 📂 kodni ko‘chirish
COPY . .

# ▶️ botni ishga tushirish
CMD ["python", "bot.py"]