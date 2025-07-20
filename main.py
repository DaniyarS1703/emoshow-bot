import threading
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telebot.apihelper import ApiTelegramException

# ——————————————————————
# Configuration
# ——————————————————————
TELEGRAM_TOKEN = "7377508266:AAHv1EKkXgP3AjVbcJHnaf505N-37HELKQw"
API_KEY        = "77777"
WEBHOOK_URL    = "https://emoshow-bot.onrender.com"
PORT           = 10000

# ——————————————————————
# App & Bot Initialization
# ——————————————————————
app = Flask(__name__)
CORS(app)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ——————————————————————
# Shared State
# ——————————————————————
latest_command = {
    "text":      "Поздравляем с праздником! EMO",
    "color":     "black",
    "bg":        "white",
    "size":      "60",
    "direction": "left",
    "speed":     "3"
}
waiting_text = {}

# ——————————————————————
# Keyboards
# ——————————————————————
def menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Меню"))
    return kb

def bg_keyboard():
    colors = [("⬜","white"),("⬛","black"),("🟥","red"),
              ("🟦","blue"),("🟩","green"),("🟨","yellow")]
    kb = InlineKeyboardMarkup(row_width=3)
    for emoji, val in colors:
        kb.add(InlineKeyboardButton(emoji, callback_data=f"setbg:{val}"))
    kb.add(
        InlineKeyboardButton("Цвет текста", callback_data="show_text"),
        InlineKeyboardButton("Размер шрифта", callback_data="show_size"),
    )
    kb.add(InlineKeyboardButton("Изменить текст", callback_data="edit_text"))
    kb.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_dir")
    )
    return kb

def text_keyboard():
    colors = [("⬜","white"),("⬛","black"),("🟥","red"),
              ("🟦","blue"),("🟩","green"),("🟨","yellow")]
    kb = InlineKeyboardMarkup(row_width=3)
    for emoji, val in colors:
        kb.add(InlineKeyboardButton(emoji, callback_data=f"setcolor:{val}"))
    kb.add(
        InlineKeyboardButton("Цвет фона", callback_data="show_bg"),
        InlineKeyboardButton("Размер шрифта", callback_data="show_size")
    )
    kb.add(InlineKeyboardButton("Изменить текст", callback_data="edit_text"))
    return kb

def size_keyboard():
    sizes = [("60","60"),("80","80"),("100","100"),("120","120")]
    kb = InlineKeyboardMarkup(row_width=2)
    for name, val in sizes:
        kb.add(InlineKeyboardButton(name, callback_data=f"setsize:{val}"))
    kb.add(
        InlineKeyboardButton("Цвет фона", callback_data="show_bg"),
        InlineKeyboardButton("Цвет текста", callback_data="show_text")
    )
    return kb

def speed_keyboard():
    speeds = [("🐢1","1"),("2","2"),("3","3"),("4","4"),("⚡️5","5")]
    kb = InlineKeyboardMarkup(row_width=3)
    for name, val in speeds:
        kb.add(InlineKeyboardButton(name, callback_data=f"setspeed:{val}"))
    return kb

def dir_keyboard():
    dirs = [("⬅️","left"),("➡️","right")]
    kb = InlineKeyboardMarkup(row_width=2)
    for name, val in dirs:
        kb.add(InlineKeyboardButton(name, callback_data=f"setdir:{val}"))
    return kb

def safe_edit(chat_id, msg_id, markup):
    try:
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup)
    except ApiTelegramException as e:
        if "message is not modified" in str(e):
            return
        raise

# ——————————————————————
# Bot Handlers
# ——————————————————————
@bot.message_handler(commands=['start'])
def on_start(msg):
    bot.send_message(
        msg.chat.id,
        "Добро пожаловать! Чтобы открыть меню управления, нажмите «Меню».",
        reply_markup=menu_keyboard()
    )

@bot.message_handler(func=lambda m: m.text and "Меню" in m.text)
def show_menu(msg):
    bot.send_message(msg.chat.id, "Выберите настройку:", reply_markup=bg_keyboard())

@bot.callback_query_handler(lambda c: c.data == "show_text")
def cb_show_text(c):
    bot.answer_callback_query(c.id)
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Выберите цвет текста:", reply_markup=text_keyboard())

@bot.callback_query_handler(lambda c: c.data == "show_size")
def cb_show_size(c):
    bot.answer_callback_query(c.id)
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Выберите размер шрифта:", reply_markup=size_keyboard())

@bot.callback_query_handler(lambda c: c.data == "show_speed")
def cb_show_speed(c):
    bot.answer_callback_query(c.id)
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Выберите скорость:", reply_markup=speed_keyboard())

@bot.callback_query_handler(lambda c: c.data == "show_dir")
def cb_show_dir(c):
    bot.answer_callback_query(c.id)
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Выберите направление:", reply_markup=dir_keyboard())

@bot.callback_query_handler(lambda c: c.data == "show_bg")
def cb_show_bg(c):
    bot.answer_callback_query(c.id)
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Выберите цвет фона:", reply_markup=bg_keyboard())

@bot.callback_query_handler(lambda c: c.data.startswith("setbg:"))
def cb_bg(c):
    latest_command["bg"] = c.data.split(":",1)[1]
    bot.answer_callback_query(c.id, "Фон установлен")
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Фон обновлён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(lambda c: c.data.startswith("setcolor:"))
def cb_color(c):
    latest_command["color"] = c.data.split(":",1)[1]
    bot.answer_callback_query(c.id, "Цвет текста установлен")
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Цвет текста обновлён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(lambda c: c.data.startswith("setsize:"))
def cb_size(c):
    latest_command["size"] = c.data.split(":",1)[1]
    bot.answer_callback_query(c.id, "Размер установлен")
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Размер шрифта обновлён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(lambda c: c.data.startswith("setspeed:"))
def cb_speed(c):
    latest_command["speed"] = c.data.split(":",1)[1]
    bot.answer_callback_query(c.id, "Скорость установлена")
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Скорость обновлена!", reply_markup=menu_keyboard())

@bot.callback_query_handler(lambda c: c.data.startswith("setdir:"))
def cb_dir(c):
    latest_command["direction"] = c.data.split(":",1)[1]
    bot.answer_callback_query(c.id, "Направление установлено")
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Направление обновлено!", reply_markup=menu_keyboard())

@bot.callback_query_handler(lambda c: c.data == "edit_text")
def cb_edit_text(c):
    waiting_text[c.from_user.id] = True
    bot.answer_callback_query(c.id, "Напиши новый текст")
    safe_edit(c.message.chat.id, c.message.message_id, None)
    bot.send_message(c.message.chat.id, "Отправь новый текст:")

@bot.message_handler(func=lambda m: waiting_text.get(m.from_user.id, False))
def handle_text(m):
    latest_command["text"] = m.text
    waiting_text[m.from_user.id] = False
    bot.reply_to(m, "Текст обновлён!", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda m: True)
def fallback(m):
    txt = m.text.strip()
    up = txt.upper()
    if up.startswith("ТЕКСТ:"):
        latest_command["text"] = txt[6:].strip()
        bot.reply_to(m, "Текст обновлён!")
    elif up.startswith("ФОН:"):
        latest_command["bg"] = txt[4:].strip()
        bot.reply_to(m, "Фон обновлён!")
    elif up.startswith("ЦВЕТ:"):
        latest_command["color"] = txt[5:].strip()
        bot.reply_to(m, "Цвет текста обновлён!")
    elif up.startswith("РАЗМЕР:"):
        try:
            latest_command["size"] = str(int(txt[7:].strip()))
            bot.reply_to(m, "Размер шрифта обновлён!")
        except:
            bot.reply_to(m, "Ошибка: размер должен быть числом")
    else:
        bot.reply_to(
            m,
            "Используй «Меню» или команды:\n"
            "ТЕКСТ: ..., ФОН: ..., ЦВЕТ: ..., РАЗМЕР: ..."
        )

# ——————————————————————
# HTTP Endpoints
# ——————————————————————
@app.route('/')
def root():
    return redirect("https://daniyars1703.github.io/emoshow-bot/")

@app.route('/api/latest', methods=['GET'])
def api_latest():
    if request.args.get('apikey') != API_KEY:
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(latest_command)

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# ——————————————————————
# Startup
# ——————————————————————
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host='0.0.0.0', port=PORT)
