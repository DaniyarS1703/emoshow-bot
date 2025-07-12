import os
from flask import Flask, request, jsonify
import telebot

# ====== НАСТРОЙКИ ======
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "ТВОЙ_ТОКЕН_ОТ_BOTFATHER")
API_KEY = os.environ.get("API_KEY", "секретный_ключ_для_apk")  # придумаешь любой текст, например: mysecret123

# ====== СЕРВЕР И БОТ ======
app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
latest_command = {"text": "Поздравляем с праздником! EMO", "color": "black", "bg": "white", "size": "60"}

# ====== РАБОТА С КОМАНДАМИ ======
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    global latest_command
    text = message.text.strip()

    if text.upper().startswith("ТЕКСТ:"):
        latest_command["text"] = text[6:].strip()
    elif text.upper().startswith("ЦВЕТ:"):
        latest_command["color"] = text[5:].strip()
    elif text.upper().startswith("ФОН:"):
        latest_command["bg"] = text[4:].strip()
    elif text.upper().startswith("РАЗМЕР:"):
        try:
            latest_command["size"] = str(int(text[7:].strip()))
        except Exception:
            pass
    else:
        bot.reply_to(message, "Доступные команды:\nТЕКСТ: ...\nЦВЕТ: ...\nФОН: ...\nРАЗМЕР: ...")

@bot.message_handler(commands=['status'])
def get_status(message):
    bot.reply_to(message, f"Текущий текст: {latest_command['text']}")

# ====== АПИ ДЛЯ ПРИЛОЖЕНИЯ ======
@app.route('/api/latest', methods=['GET'])
def api_latest():
    apikey = request.args.get("apikey")
    if apikey != API_KEY:
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(latest_command)

@app.route('/')
def index():
    return "EMOSHOW Bot server running!"

# ====== СТАРТ ======
if __name__ == '__main__':
    import threading
    threading.Thread(target=bot.polling, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
