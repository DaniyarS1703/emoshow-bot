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
    "size":      "60",
    "direction": "left",
    "speed":     "3"
}
waiting_text = {}

# --- Категории для меню ---
CATEGORIES = ["bg", "color", "size", "speed", "text"]
CATEGORY_TITLES = {
    "bg": "Цвет фона",
    "color": "Цвет текста",
    "size": "Размер",
    "speed": "Скорость",
    "text": "Текст"
}

def menu_inline_keyboard(active="bg"):
    kb = InlineKeyboardMarkup(row_width=3)
    for cat in CATEGORIES:
        title = CATEGORY_TITLES[cat]
        if cat == active:
            text = f"■ {title.upper()} ■"
        else:
            text = title
        kb.add(InlineKeyboardButton(text, callback_data=f"show_{cat}"))
    return kb

def bg_color_keyboard(current_bg):
    colors = [
        ("⬜", "white"), ("⬛", "black"), ("🟥", "red"),
        ("🟦", "blue"), ("🟩", "green"), ("🟨", "yellow"),
        ("🟧", "orange"), ("🟪", "purple"), ("🟫", "brown")
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
        ("⚪", "white"), ("⚫", "black"), ("🔴", "red"),
        ("🔵", "blue"), ("🟢", "green"), ("🟡", "yellow"),
        ("🟠", "orange"), ("🟣", "purple"), ("🟤", "brown")
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
    sizes = [("60", "60"), ("80", "80"), ("100", "100"), ("120", "120")]
    kb = InlineKeyboardMarkup(row_width=2)
    for name, val in sizes:
        text = f"{name}✅" if val == current_size else name
        kb.add(InlineKeyboardButton(text, callback_data=f"setsize:{val}"))
    return kb

def speed_keyboard(current_speed):
    speeds = [("🐢1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("⚡️5", "5")]
    kb = InlineKeyboardMarkup(row_width=3)
    for name, val in speeds:
        text = f"{name}✅" if val == current_speed else name
        kb.add(InlineKeyboardButton(text, callback_data=f"setspeed:{val}"))
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

def settings_keyboard(category):
    # "Шапка" меню
    kb = menu_inline_keyboard(active=category)
    # Далее — блок опций по выбранной категории
    if category == "bg":
        for row in bg_color_keyboard(latest_command["bg"]).keyboard:
            kb.keyboard.append(row)
    elif category == "color":
        for row in text_color_keyboard(latest_command["color"]).keyboard:
            kb.keyboard.append(row)
    elif category == "size":
        for row in size_keyboard(latest_command["size"]).keyboard:
            kb.keyboard.append(row)
    elif category == "speed":
        for row in speed_keyboard(latest_command["speed"]).keyboard:
            kb.keyboard.append(row)
    elif category == "text":
        kb.add(InlineKeyboardButton("✏️ Изменить текст", callback_data="edit_text"))
    # Кнопки смены режима
    if category in ["bg", "color", "size", "speed"]:
        for row in direction_keyboard(latest_command["direction"]).keyboard:
            kb.keyboard.append(row)
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
        reply_markup=settings_keyboard("bg")
    )

@bot.callback_query_handler(lambda c: c.data.startswith("show_"))
def menu_nav_callback(c):
    cat = c.data[5:]
    kb = settings_keyboard(cat)
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(lambda c: c.data.startswith("setbg:"))
def cb_set_bg(c):
    latest_command["bg"] = c.data.split(":",1)[1]
    kb = settings_keyboard("bg")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Фон обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setcolor:"))
def cb_set_color(c):
    latest_command["color"] = c.data.split(":",1)[1]
    kb = settings_keyboard("color")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Цвет текста обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setsize:"))
def cb_set_size(c):
    latest_command["size"] = c.data.split(":",1)[1]
    kb = settings_keyboard("size")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Размер шрифта обновлён!")

@bot.callback_query_handler(lambda c: c.data.startswith("setspeed:"))
def cb_set_speed(c):
    latest_command["speed"] = c.data.split(":",1)[1]
    kb = settings_keyboard("speed")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Скорость обновлена!")

@bot.callback_query_handler(lambda c: c.data.startswith("setdirection:"))
def cb_set_direction(c):
    latest_command["direction"] = c.data.split(":",1)[1]
    kb = settings_keyboard("bg")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id, "Режим обновлён!")

@bot.callback_query_handler(lambda c: c.data == "edit_text")
def cb_edit_text(c):
    waiting_text[c.from_user.id] = True
    bot.answer_callback_query(c.id, "Введите новый текст")
    bot.send_message(
        c.message.chat.id,
        "Отправьте новый текст для бегущей строки (можно использовать переносы строк):"
    )

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
