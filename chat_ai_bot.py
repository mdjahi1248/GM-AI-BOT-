import os
import telebot
import requests
import base64

# =========================
# 🔐 LOAD KEYS FROM ENV
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    print("❌ ERROR: TELEGRAM_TOKEN or OPENAI_API_KEY not set")
    exit()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# =========================
# 🤖 TEXT + IMAGE AI
# =========================
def openai_vision_chat(user_text=None, image_b64=None):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    content = []

    if user_text:
        content.append({
            "type": "text",
            "text": user_text
        })

    if image_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_b64}"
            }
        })

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Automatically detect the user's language and reply in the same language. You can understand images and explain what it is, what it is used for, and what the user should do."
            },
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 500
    }

    r = requests.post(url, headers=headers, json=data, timeout=60)
    res = r.json()

    if "choices" not in res:
        print("OPENAI ERROR:", res)
        return "⚠️ AI এখন কাজ করছে না, পরে আবার চেষ্টা করুন।"

    return res["choices"][0]["message"]["content"]

# =========================
# 📌 START
# =========================
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m,
        "🤖 হ্যালো! আমি Vision AI Bot.\n\n"
        "তুমি লেখা পাঠাতে পারো ✍️\n"
        "অথবা ছবি পাঠাও 📷 — আমি বলে দেব এটা কী, কিসের জন্য, কী করতে হবে।\n\n"
        "আমি English, বাংলা, Hindi, Nepali সব ভাষা বুঝি 🙂"
    )

# =========================
# 💬 TEXT HANDLER
# =========================
@bot.message_handler(content_types=['text'])
def text_chat(m):
    try:
        bot.send_chat_action(m.chat.id, 'typing')
        reply = openai_vision_chat(user_text=m.text)
        bot.reply_to(m, reply)
    except Exception as e:
        print("TEXT ERROR:", e)
        bot.reply_to(m, "⚠️ এখন সমস্যা হচ্ছে, পরে আবার চেষ্টা করো।")

# =========================
# 🖼 PHOTO HANDLER
# =========================
@bot.message_handler(content_types=['photo'])
def photo_handler(m):
    try:
        bot.send_chat_action(m.chat.id, 'typing')

        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        b64_image = base64.b64encode(downloaded_file).decode()

        prompt = "এই ছবিটা কী, কিসের জন্য ব্যবহার হয়, আর আমি কী করতে পারি সহজ ভাষায় বলো।"
        reply = openai_vision_chat(user_text=prompt, image_b64=b64_image)

        bot.reply_to(m, reply)

    except Exception as e:
        print("PHOTO ERROR:", e)
        bot.reply_to(m, "⚠️ ছবি বুঝতে সমস্যা হচ্ছে, পরে আবার চেষ্টা করো।")

# =========================
print("🤖 Vision AI Bot running...")
bot.infinity_polling()
