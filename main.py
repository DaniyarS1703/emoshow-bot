import threading
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_TOKEN = "7377508266:AAHv1EKkXgP3AjVbcJHnaf505N-37HELKQw"
API_KEY        = "77777"
WEBHOOK_URL    = "https://emoshow-bot.onrender.com"
PORT           = 10000

app = Flask(__name__)
CORS(app)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

latest_command = {
    "text":      "Поздравляем с праздником! EMO",
    "color":     "black",
    "bg":        "white",
    "size":      "70",
    "direction": "left",
    "speed":     "3"
}
waiting_text = {}

CATEGORIES = ["bg", "color", "size", "speed", "screensaver", "text"]
CATEGORY_TITLES = {
    "bg": "Цвет фона",
    "color": "Цвет текста",
    "size": "Размер",
    "speed": "Скорость",
    "screensaver": "🖼️ Заставка",
    "text": "ТЕКСТ"
}

def menu_inline_keyboard(active="bg"):
    """
    Возвращает список кнопок: сначала активная (жирная), потом значения, потом все остальные категории.
    """
    kb = InlineKeyboardMarkup(row_width=3)
    # Сначала активная категория
    active_title = f"■ {CATEGORY_TITLES[active].upper()} ■"
    callback = "edit_text" if active == "text" else f"show_{active}"
    kb.add(InlineKeyboardButton(active_title, callback_data=callback))
    # Значения для выбранной категории
    if active == "bg":
        for row in bg_color_keyboard(latest_command["bg"]).keyboard:
            kb.keyboard.append(row)
        for row in direction_keyboard(latest_command["direction"]).keyboard:
            kb.keyboard.append(row)
    elif active == "color":
        for row in text_color_keyboard(latest_command["color"]).keyboard:
            kb.keyboard.append(row)
    elif active == "size":
        for row in size_keyboard(latest_command["size"]).keyboard:
            kb.keyboard.append(row)
    elif active == "speed":
        for row in speed_keyboard(latest_command["speed"]).keyboard:
            kb.keyboard.append(row)
    elif active == "screensaver":
        # Специальное поведение — никаких значений (заставка активируется сразу)
        pass
    elif active == "text":
        # Просто выделена жирно
        pass
    # Затем остальные категории
    for cat in CATEGORIES:
        if cat == active:
            continue
        title = CATEGORY_TITLES[cat]
        text = title
        callback = "edit_text" if cat == "text" else f"show_{cat}"
        kb.add(InlineKeyboardButton(text, callback_data=callback))
    return kb

def bg_color_keyboard(current_bg):
    colors = [
        ("⬜", "white"),    ("⬛", "black"),    ("🟥", "red"),
        ("🟦", "blue"),     ("🟩", "green"),   ("🟨", "yellow"),
        ("🟧", "orange"),   ("🟪", "purple"),  ("🟫", "brown"),
        ("🩷", "#FF00FF"),  ("🩵", "lightblue"),("🟫", "darkbrown"),
        ("🌈", "raduga"),   ("🟠", "disco"),   ("💫", "luchi"),
        ("✨", "ogni"),     ("🎉", "drkids")
    ]
    kb = InlineKeyboardMarkup(row_width=3)
    btns = []
    for emoji, val in colors:
        text = f"{emoji}✅" if val == current_bg else emoji
        btns.append(InlineKeyboardButton(text, callback_data=f"setbg:{val}"))
    for i in range(0, len(btns), 3):
        kb.row(*btns[i:i+3])
    return kb

def text_color_keyboard(current_color):
    colors = [
        ("⚪", "white"),    ("⚫", "black"),    ("🔴", "red"),
        ("🔵", "blue"),     ("🟢", "green"),   ("🟡", "yellow"),
        ("🟠", "orange"),   ("🟣", "purple"),  ("🟤", "brown"),
        ("🩷", "#FF00FF"),  ("🩵", "lightblue"),("🟫", "darkbrown")
    ]
    kb = InlineKeyboardMarkup(row_width=3)
    btns = []
    for emoji, val in colors:
        text = f"{emoji}✅" if val == current_color else emoji
        btns.append(InlineKeyboardButton(text, callback_data=f"setcolor:{val}"))
    for i in range(0, len(btns), 3):
        kb.row(*btns[i:i+3])
    return kb

def size_keyboard(current_size):
    sizes = [("70", "70"), ("80", "80"), ("90", "90"),
             ("100", "100"), ("110", "110"), ("120", "120")]
    kb = InlineKeyboardMarkup(row_width=3)
    btns = []
    for name, val in sizes:
        text = f"{name}✅" if val == current_size else name
        btns.append(InlineKeyboardButton(text, callback_data=f"setsize:{val}"))
    for i in range(0, len(btns), 3):
        kb.row(*btns[i:i+3])
    return kb

def speed_keyboard(current_speed):
    speeds = [
        ("🐢1", "1"), ("2", "2"), ("3", "3"),
        ("4", "4"), ("5", "5"), ("6", "6"),
        ("7", "7"), ("8", "8"), ("⚡️9", "9")
    ]
    kb = InlineKeyboardMarkup(row_width=3)
    btns = []
    for name, val in speeds:
        text = f"{name}✅" if val == current_speed else name
        btns.append(InlineKeyboardButton(text, callback_data=f"setspeed:{val}"))
    for i in range(0, len(btns), 3):
        kb.row(*btns[i:i+3])
    return kb

def direction_keyboard(current_direction):
    options = [
        ("📌 Закрепить", "fixed"),
        ("▶️ Бегущая строка", "left"),
        ("🏓 Пинг-понг", "pingpong")
    ]
    kb = InlineKeyboardMarkup(row_width=3)
    for title, value in options:
        text = f"{title}✅" if value == current_direction else title
        kb.add(InlineKeyboardButton(text, callback_data=f"setdirection:{value}"))
    return kb

@bot.message_handler(commands=['start'])
def on_start(msg):
    bot.send_message(
        msg.chat.id,
        "Добро пожаловать! Настройте бегущую строку через меню.",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню"))
    )

@bot.message_handler(func=lambda m: m.text == "Меню")
def show_main_menu(msg):
    bot.send_message(
        msg.chat.id,
        "Настройте отображение бегущей строки:",
        reply_markup=menu_inline_keyboard("bg")
    )

@bot.callback_query_handler(lambda c: c.data.startswith("show_"))
def menu_nav_callback(c):
    cat = c.data[5:]
    if cat == "screensaver":
        # При выборе заставки — сразу применяем!
        latest_command["bg"] = "green"
        latest_command["color"] = "black"
        latest_command["direction"] = "left"
        latest_command["text"] = (
            "ПОЗДРАВЬ СВОИХ ДРУЗЕЙ И РОДНЫХ. ОТПРАВЛЯЙ СВОЙ ТЕКСТ В СООБЩЕНИИ\n"
            "ЗА ЛАЙКИ И РЕПОСТЫ СПАСИБО!"
        )
        kb = menu_inline_keyboard(cat)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
        bot.answer_callback_query(c.id, "Заставка активирована!")
    else:
        kb = menu_inline_keyboard(cat)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
        bot.answer_callback_query(c.id)

@bot.callback_query_handler(lambda c: c.data == "edit_text")
def cb_edit_text(c):
    waiting_text[c.from_user.id] = True
    bot.answer_callback_query(c.id, "Введите новый текст")
    bot.send_message(
        c.message.chat.id,
        "Отправьте новый текст для бегущей строки (можно использовать переносы строк):"
    )

@bot.callback_query_handler(lambda c: c.data.startswith("setbg:"))
def cb_set_bg(c):
    latest_command["bg"] = c.data.split(":",1)[1]
    kb = menu_inline_keyboard("bg")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Фон обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setcolor:"))
def cb_set_color(c):
    latest_command["color"] = c.data.split(":",1)[1]
    kb = menu_inline_keyboard("color")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Цвет текста обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setsize:"))
def cb_set_size(c):
    latest_command["size"] = c.data.split(":",1)[1]
    kb = menu_inline_keyboard("size")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Размер шрифта обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setspeed:"))
def cb_set_speed(c):
    latest_command["speed"] = c.data.split(":",1)[1]
    kb = menu_inline_keyboard("speed")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Скорость обновлена!")

@bot.callback_query_handler(lambda c: c.data.startswith("setdirection:"))
def cb_set_direction(c):
    latest_command["direction"] = c.data.split(":",1)[1]
    kb = menu_inline_keyboard("bg")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Режим обновлён!")

@bot.message_handler(func=lambda m: waiting_text.get(m.from_user.id, False))
def handle_new_text(m):
    latest_command["text"] = m.text
    waiting_text[m.from_user.id] = False
    bot.reply_to(
        m,
        "Текст обновлён! Переносы строк учтены.",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню"))
    )

@bot.message_handler(func=lambda m: True)
def fallback(m):
    txt = m.text.strip()
    up = txt.upper()
    if up.startswith("ТЕКСТ:"):
        latest_command["text"] = txt[6:].strip()
        bot.reply_to(m, "Текст обновлён!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню")))
    elif up.startswith("ФОН:"):
        latest_command["bg"] = txt[4:].strip()
        bot.reply_to(m, "Фон обновлён!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню")))
    elif up.startswith("ЦВЕТ:"):
        latest_command["color"] = txt[5:].strip()
        bot.reply_to(m, "Цвет текста обновлён!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню")))
    elif up.startswith("РАЗМЕР:"):
        try:
            latest_command["size"] = str(int(txt[7:].strip()))
            bot.reply_to(m, "Размер шрифта обновлён!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню")))
        except:
            bot.reply_to(m, "Ошибка: размер должен быть числом.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню")))
    else:
        bot.reply_to(
            m,
            "Используйте кнопку «Меню» или команды:\n"
            "ТЕКСТ: ..., ФОН: ..., ЦВЕТ: ..., РАЗМЕР: ...",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню"))
        )

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
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host='0.0.0.0', port=PORT)
