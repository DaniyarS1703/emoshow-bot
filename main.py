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

# Пары для меню по две в строке:
CATEGORY_PAIRS = [
    ("bg", "color"),
    ("speed", "size"),
    ("screensaver", "text")
]

CATEGORY_TITLES = {
    "bg": "Цвет фона",
    "color": "Цвет текста",
    "size": "Размер текста",
    "speed": "Скорость",
    "screensaver": "🖼️ Заставка",
    "text": "ТЕКСТ"
}

# Отдельно режимы (три кнопки снизу)
DIRECTION_MODES = [
    ("fixed", "📌 Закрепить"),
    ("left", "▶️ Бегущая строка"),
    ("pingpong", "🏓 Пинг-понг")
]

def build_categories_keyboard(active="bg"):
    kb = InlineKeyboardMarkup(row_width=2)
    # Формируем пары
    for pair in CATEGORY_PAIRS:
        row = []
        for cat in pair:
            title = CATEGORY_TITLES[cat]
            if cat == active:
                text = f"■ {title.upper()} ■"
            else:
                text = title
            callback = "edit_text" if cat == "text" else f"show_{cat}"
            row.append(InlineKeyboardButton(text, callback_data=callback))
        kb.row(*row)
        # Сразу после выбранной категории — значения
        if active in pair:
            # Значения для активной категории
            for val_row in get_values_keyboard(active).keyboard:
                kb.keyboard.append(val_row)
    # Добавляем три режима по одной кнопке
    for key, label in DIRECTION_MODES:
        checked = "✅" if latest_command["direction"] == key else ""
        kb.add(InlineKeyboardButton(f"{label}{checked}", callback_data=f"setdirection:{key}"))
    return kb

def get_values_keyboard(category):
    if category == "bg":
        return bg_color_keyboard(latest_command["bg"])
    elif category == "color":
        return text_color_keyboard(latest_command["color"])
    elif category == "size":
        return size_keyboard(latest_command["size"])
    elif category == "speed":
        return speed_keyboard(latest_command["speed"])
    # Заставка и ТЕКСТ — без значений
    else:
        return InlineKeyboardMarkup()

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
        reply_markup=build_categories_keyboard("bg")
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
        kb = build_categories_keyboard(cat)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
        bot.answer_callback_query(c.id, "Заставка активирована!")
    else:
        kb = build_categories_keyboard(cat)
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
    kb = build_categories_keyboard("bg")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Фон обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setcolor:"))
def cb_set_color(c):
    latest_command["color"] = c.data.split(":",1)[1]
    kb = build_categories_keyboard("color")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Цвет текста обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setsize:"))
def cb_set_size(c):
    latest_command["size"] = c.data.split(":",1)[1]
    kb = build_categories_keyboard("size")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Размер шрифта обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setspeed:"))
def cb_set_speed(c):
    latest_command["speed"] = c.data.split(":",1)[1]
    kb = build_categories_keyboard("speed")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Скорость обновлена!")

@bot.callback_query_handler(lambda c: c.data.startswith("setdirection:"))
def cb_set_direction(c):
    latest_command["direction"] = c.data.split(":",1)[1]
    kb = build_categories_keyboard("bg")
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
