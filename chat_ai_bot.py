import telebot
import requests
import base64
import os

# =========================
# ENV VARIABLES (Railway)
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# =========================
# 🔤 TEXT AI
# =========================
def ask_ai_text(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are a friendly multilingual AI. Understand Bangla, English, Hindi, Nepali. Reply naturally in the user's language."},
            {"role": "user", "content": text}
        ],
        "max_tokens": 500
    }

    r = requests.post(url, headers=headers, json=data, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

# =========================
# 🖼️ IMAGE AI
# =========================
def ask_ai_image(image_path, caption="Describe this image"):
    with open(image_path, "rb") as img:
        b64 = base64.b64encode(img.read()).decode()

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "এই ছবিটা কী, কিসের জন্য, কী করতে হবে — Bangla, English, Hindi, Nepali বুঝে উত্তর দাও।"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    }
                ]
            }
        ],
        "max_tokens": 700
    }

    r = requests.post(url, headers=headers, json=data, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

# =========================
# 📌 COMMAND
# =========================
@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m,
        "🤖 হ্যালো! আমি Vision AI Bot.\n\n"
        "✍️ লেখা পাঠাও\n"
        "🖼️ ছবি পাঠাও — আমি বলবো এটা কী, কিসের জন্য, কী করতে হবে।\n\n"
        "আমি Bangla, English, Hindi, Nepali বুঝি 🙂"
    )

# =========================
# 💬 TEXT HANDLER
# =========================
@bot.message_handler(content_types=["text"])
def text_chat(m):
    try:
        bot.send_chat_action(m.chat.id, "typing")
        reply = ask_ai_text(m.text)
        bot.reply_to(m, reply)
    except Exception as e:
        print("TEXT ERROR:", e)
        bot.reply_to(m, "⚠️ AI এখন কাজ করছে না, পরে আবার চেষ্টা করো।")

# =========================
# 🖼️ PHOTO HANDLER
# =========================
@bot.message_handler(content_types=["photo"])
def photo_chat(m):
    try:
        bot.send_chat_action(m.chat.id, "typing")

        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = "image.jpg"
        with open(file_name, "wb") as f:
            f.write(downloaded_file)

        caption = m.caption if m.caption else "Describe this image"
        reply = ask_ai_image(file_name, caption)

        bot.reply_to(m, reply)
        os.remove(file_name)

    except Exception as e:
        print("IMAGE ERROR:", e)
        bot.reply_to(m, "⚠️ ছবি বুঝতে সমস্যা হচ্ছে, পরে আবার পাঠাও।")

# =========================
print("🤖 Vision AI Bot Running...")
bot.infinity_polling()
