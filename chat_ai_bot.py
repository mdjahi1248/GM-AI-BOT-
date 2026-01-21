import telebot
import requests
import os

# ====== TOKENS FROM ENV (Railway Variables) ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ====== AI FUNCTION (TEXT + IMAGE) ======
def ask_ai(text=None, image_url=None):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    content = []
    if text:
        content.append({"type": "text", "text": text})
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are a friendly Vision AI assistant. You can understand images and text. Explain clearly in Bangla, English, Hindi or Nepali automatically."},
            {"role": "user", "content": content}
        ],
        "max_tokens": 500
    }

    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    res = r.json()
    return res["choices"][0]["message"]["content"]

# ====== START ======
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m,
        "🤖 হ্যালো! আমি Vision AI Bot.\n\n"
        "✍️ লেখা পাঠাও\n"
        "📸 অথবা ছবি পাঠাও — আমি বলবো এটা কী, কিসের জন্য, কী করতে হবে।\n\n"
        "আমি Bangla, English, Hindi, Nepali সব বুঝি 🙂"
    )

# ====== TEXT ======
@bot.message_handler(content_types=['text'])
def text_handler(m):
    try:
        reply = ask_ai(text=m.text)
        bot.reply_to(m, reply)
    except Exception as e:
        print(e)
        bot.reply_to(m, "⚠️ AI কাজ করছে না, পরে আবার চেষ্টা করো।")

# ====== IMAGE ======
@bot.message_handler(content_types=['photo'])
def photo_handler(m):
    try:
        file_id = m.photo[-1].file_id
        file_info = bot.get_file(file_id)
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"

        bot.reply_to(m, "🧠 ছবি দেখছি...")

        caption = m.caption if m.caption else "এই ছবিতে কী আছে? বিস্তারিত বলো।"
        reply = ask_ai(text=caption, image_url=image_url)

        bot.reply_to(m, reply)
    except Exception as e:
        print(e)
        bot.reply_to(m, "⚠️ ছবি বুঝতে পারছি না, পরে আবার চেষ্টা করো।")

print("🤖 Vision AI Bot Running...")
bot.infinity_polling()
