import telebot
import requests
import base64
import os

# =========================
# 🔑 ENV VARIABLES (Railway/GitHub)
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")  # HuggingFace free token

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# =========================
# 🤖 TEXT AI (Groq)
# =========================
def ai_reply(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """
You are a smart friendly AI.
You understand Bangla, English, Hindi, Nepali.
Reply naturally in the user's language.
"""

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    r = requests.post(url, headers=headers, json=data, timeout=60)
    res = r.json()

    if "choices" not in res:
        return "⚠️ AI এখন কাজ করছে না, পরে চেষ্টা করো।"

    return res["choices"][0]["message"]["content"]

# =========================
# 🖼️ IMAGE AI (HuggingFace - FREE)
# =========================
def image_reply(image_bytes):
    api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    r = requests.post(api_url, headers=headers, data=image_bytes, timeout=60)
    res = r.json()

    if isinstance(res, dict) and res.get("error"):
        return "⚠️ ছবি বুঝতে সমস্যা হচ্ছে, পরে চেষ্টা করো।"

    if isinstance(res, list) and "generated_text" in res[0]:
        caption = res[0]["generated_text"]
        return f"🖼️ আমি ছবিতে দেখছি: {caption}\n\n👉 মনে হচ্ছে এটা কোনো খাবার/বস্তু/দৃশ্য। চাইলে বিস্তারিত জিজ্ঞেস করো 🙂"

    return "⚠️ ছবি বুঝতে পারলাম না।"

# =========================
# 📌 START
# =========================
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m,
        "🤖 হ্যালো! আমি Vision AI Bot.\n\n"
        "✍️ লেখা পাঠালে — AI উত্তর দিবে\n"
        "📷 ছবি পাঠালে — এটা কী দেখা যাচ্ছে বলবো\n\n"
        "আমি Bangla, English, Hindi, Nepali বুঝি 🙂"
    )

# =========================
# 💬 TEXT HANDLER
# =========================
@bot.message_handler(func=lambda m: m.text is not None)
def chat(m):
    bot.send_chat_action(m.chat.id, 'typing')
    reply = ai_reply(m.text)
    bot.reply_to(m, reply)

# =========================
# 📷 PHOTO HANDLER
# =========================
@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.send_chat_action(m.chat.id, 'typing')
    file_id = m.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    reply = image_reply(file)
    bot.reply_to(m, reply)

# =========================
print("🤖 Vision AI Bot running...")
bot.infinity_polling()
