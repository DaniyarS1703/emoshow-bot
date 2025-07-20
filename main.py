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
menu_state = {}  # user_id: category

# Основные категории меню
CATEGORIES = [
    ("bg",      "Цвет фона"),
    ("color",   "Цвет текста"),
    ("size",    "Размер шрифта"),
    ("speed",   "Скорость"),
    ("text",    "ТЕКСТ"),
    ("fixed",   "Закрепить"),
    ("scroll",  "Бегущая строка"),
    ("pingpong","Пинг-понг"),
]

def get_active_category(user_id):
    return menu_state.get(user_id, "bg")

def set_active_category(user_id, cat):
    menu_state[user_id] = cat

def panel_keyboard(user_id):
    active = get_active_category(user_id)
    panel = []
    for code, title in CATEGORIES:
        if code == active:
            panel.append(InlineKeyboardButton(f"■ {title} ■", callback_data=f"cat:{code}"))
        else:
            panel.append(InlineKeyboardButton(title, callback_data=f"cat:{code}"))
    # Кнопки по 3 в ряд
    kb = []
    for i in range(0, len(panel), 3):
        kb.append(panel[i:i+3])
    return kb

def make_keyboard(user_id):
    active = get_active_category(user_id)
    kb = InlineKeyboardMarkup(row_width=3)
    # 1. Выбор значений текущей категории
    if active == "bg":
        current_bg = latest_command.get("bg", "white")
        colors = [
            ("⬜", "white"),   ("⬛", "black"),   ("🟥", "red"),
            ("🟦", "blue"),    ("🟩", "green"),  ("🟨", "yellow"),
            ("🟧", "orange"),  ("🟪", "purple"), ("🟫", "brown"),
            ("🩷", "#FF00FF"), ("🩵", "#00FFFF"), ("🩶", "#CCCCCC"),
        ]
        btns = []
        for emoji, val in colors:
            label = emoji + (" ✔" if str(val).lower() == str(current_bg).lower() else "")
            btns.append(InlineKeyboardButton(label, callback_data=f"setbg:{val}"))
        for i in range(0, len(btns), 3):
            kb.add(*btns[i:i+3])
        # Анимированные
        anim = [
            ("🟠 Диско", "disco"),
            ("🌈 Радуга", "raduga"),
            ("🟪 Лучи", "luchi"),
            ("🟣 Огоньки", "ogni"),
        ]
        btns2 = []
        for name, val in anim:
            label = name + (" ✔" if str(current_bg).lower() == val else "")
            btns2.append(InlineKeyboardButton(label, callback_data=f"setbg:{val}"))
        for i in range(0, len(btns2), 3):
            kb.add(*btns2[i:i+3])
    elif active == "color":
        current_color = latest_command.get("color", "black")
        colors = [
            ("⬜", "white"),   ("⬛", "black"),   ("🟥", "red"),
            ("🟦", "blue"),    ("🟩", "green"),  ("🟨", "yellow"),
            ("🟧", "orange"),  ("🟪", "purple"), ("🟫", "brown"),
            ("🩷", "#FF00FF"), ("🩵", "#00FFFF"), ("🩶", "#CCCCCC"),
        ]
        btns = []
        for emoji, val in colors:
            label = emoji + (" ✔" if str(val).lower() == str(current_color).lower() else "")
            btns.append(InlineKeyboardButton(label, callback_data=f"setcolor:{val}"))
        for i in range(0, len(btns), 3):
            kb.add(*btns[i:i+3])
    elif active == "size":
        current_size = str(latest_command.get("size", "70"))
        sizes = ["70","80","90","100","110","120"]
        btns = []
        for size in sizes:
            label = size + (" ✔" if size == current_size else "")
            btns.append(InlineKeyboardButton(label, callback_data=f"setsize:{size}"))
        for i in range(0, len(btns), 3):
            kb.add(*btns[i:i+3])
    elif active == "speed":
        current_speed = str(latest_command.get("speed", "3"))
        btns = []
        for val in range(1, 10):
            label = f"{val}" if val != 1 and val != 9 else ("🐢1" if val == 1 else "⚡️9")
            label += " ✔" if str(val) == current_speed else ""
            btns.append(InlineKeyboardButton(label, callback_data=f"setspeed:{val}"))
        for i in range(0, len(btns), 3):
            kb.add(*btns[i:i+3])
    elif active == "text":
        kb.add(InlineKeyboardButton("Изменить текст", callback_data="edit_text"))
    # ничего не выводим для fixed/scroll/pingpong — только панель

    # 2. Панель категорий внизу
    for row in panel_keyboard(user_id):
        kb.add(*row)
    return kb

@bot.message_handler(commands=['start'])
def on_start(msg):
    set_active_category(msg.from_user.id, "bg")
    bot.send_message(
        msg.chat.id,
        "Добро пожаловать! Выберите настройку:",
        reply_markup=make_keyboard(msg.from_user.id)
    )

@bot.message_handler(func=lambda m: m.text == "Меню")
def show_menu(msg):
    set_active_category(msg.from_user.id, "bg")
    bot.send_message(
        msg.chat.id,
        "Меню настроек:",
        reply_markup=make_keyboard(msg.from_user.id)
    )

@bot.callback_query_handler(lambda c: c.data.startswith("cat:"))
def change_category(c):
    cat = c.data.split(":")[1]
    set_active_category(c.from_user.id, cat)
    bot.answer_callback_query(c.id)
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=make_keyboard(c.from_user.id))

@bot.callback_query_handler(lambda c: c.data.startswith("setbg:"))
def cb_set_bg(c):
    bg = c.data.split(":",1)[1]
    latest_command["bg"] = bg
    set_active_category(c.from_user.id, "bg")
    bot.answer_callback_query(c.id, f"Фон обновлён")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=make_keyboard(c.from_user.id))

@bot.callback_query_handler(lambda c: c.data.startswith("setcolor:"))
def cb_set_color(c):
    latest_command["color"] = c.data.split(":",1)[1]
    set_active_category(c.from_user.id, "color")
    bot.answer_callback_query(c.id, "Цвет текста обновлён!")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=make_keyboard(c.from_user.id))

@bot.callback_query_handler(lambda c: c.data.startswith("setsize:"))
def cb_set_size(c):
    latest_command["size"] = c.data.split(":",1)[1]
    set_active_category(c.from_user.id, "size")
    bot.answer_callback_query(c.id, "Размер шрифта обновлён!")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=make_keyboard(c.from_user.id))

@bot.callback_query_handler(lambda c: c.data.startswith("setspeed:"))
def cb_set_speed(c):
    latest_command["speed"] = c.data.split(":",1)[1]
    set_active_category(c.from_user.id, "speed")
    bot.answer_callback_query(c.id, "Скорость обновлена!")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=make_keyboard(c.from_user.id))

@bot.callback_query_handler(lambda c: c.data == "edit_text")
def cb_edit_text(c):
    waiting_text[c.from_user.id] = True
    bot.answer_callback_query(c.id, "Введите новый текст")
    bot.send_message(
        c.message.chat.id,
        "Отправьте новый текст для бегущей строки (можно использовать переносы строк):"
    )

@bot.callback_query_handler(lambda c: c.data in ["set_fixed", "set_scroll", "set_pingpong"])
def cb_set_mode(c):
    mode = c.data.replace("set_", "")
    if mode == "fixed":
        latest_command["direction"] = "fixed"
    elif mode == "scroll":
        latest_command["direction"] = "left"
    elif mode == "pingpong":
        latest_command["direction"] = "pingpong"
    set_active_category(c.from_user.id, mode)
    bot.answer_callback_query(c.id, "Режим обновлён!")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=make_keyboard(c.from_user.id))

@bot.message_handler(func=lambda m: waiting_text.get(m.from_user.id, False))
def handle_new_text(m):
    latest_command["text"] = m.text
    waiting_text[m.from_user.id] = False
    set_active_category(m.from_user.id, "text")
    bot.reply_to(
        m,
        "Текст обновлён! Переносы строк учтены.",
        reply_markup=make_keyboard(m.from_user.id)
    )

@bot.message_handler(func=lambda m: True)
def fallback(m):
    txt = m.text.strip()
    up = txt.upper()
    user_id = m.from_user.id
    if up.startswith("ТЕКСТ:"):
        latest_command["text"] = txt[6:].strip()
        set_active_category(user_id, "text")
        bot.reply_to(m, "Текст обновлён!", reply_markup=make_keyboard(user_id))
    elif up.startswith("ФОН:"):
        latest_command["bg"] = txt[4:].strip()
        set_active_category(user_id, "bg")
        bot.reply_to(m, "Фон обновлён!", reply_markup=make_keyboard(user_id))
    elif up.startswith("ЦВЕТ:"):
        latest_command["color"] = txt[5:].strip()
        set_active_category(user_id, "color")
        bot.reply_to(m, "Цвет текста обновлён!", reply_markup=make_keyboard(user_id))
    elif up.startswith("РАЗМЕР:"):
        try:
            latest_command["size"] = str(int(txt[7:].strip()))
            set_active_category(user_id, "size")
            bot.reply_to(m, "Размер шрифта обновлён!", reply_markup=make_keyboard(user_id))
        except:
            bot.reply_to(m, "Ошибка: размер должен быть числом.", reply_markup=make_keyboard(user_id))
    else:
        bot.reply_to(
            m,
            "Используйте меню ниже или команды:\n"
            "ТЕКСТ: ..., ФОН: ..., ЦВЕТ: ..., РАЗМЕР: ...",
            reply_markup=make_keyboard(user_id)
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
