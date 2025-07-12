import os
from flask import Flask, request, jsonify, send_from_directory
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask_cors import CORS

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "ТВОЙ_ТОКЕН_ОТ_BOTFATHER")
API_KEY = os.environ.get("API_KEY", "77777")

app = Flask(__name__)
CORS(app)  # Разрешаем CORS-запросы

bot = telebot.TeleBot(TELEGRAM_TOKEN)
latest_command = {
    "text": "Поздравляем с праздником! EMO",
    "color": "black",
    "bg": "white",
    "size": "60",
    "direction": "left",
    "speed": "3"
}
waiting_text = {}

# Цвета и клавиатуры

bg_colors = [
    ("⬜", "white"),
    ("⬛", "black"),
    ("🟥", "red"),
    ("🟦", "blue"),
    ("🟩", "green"),
    ("🟨", "yellow"),
    ("🟧", "orange"),
    ("🟪", "purple"),
    ("🟫", "brown")
]

text_colors = [
    ("⚪", "white"),
    ("⚫", "black"),
    ("🔴", "red"),
    ("🔵", "blue"),
    ("🟢", "green"),
    ("🟡", "yellow"),
    ("🟠", "orange"),
    ("🟣", "purple"),
    ("🟤", "brown")
]

sizes = [
    ("60", "60"),
    ("80", "80"),
    ("100", "100"),
    ("120", "120")
]

speed_options = [
    ("🐢 1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("⚡️ 6", "6")
]

direction_options = [
    ("⬅️", "left"),
    ("➡️", "right")
]

def menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🎨 Меню"))
    return markup

def bg_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(emoji, callback_data=f"setbg:{color}") for emoji, color in bg_colors]
    for i in range(0, 9, 3):
        markup.add(*buttons[i:i+3])
    markup.add(
        InlineKeyboardButton("Цвет текста", callback_data="show_text_colors"),
        InlineKeyboardButton("Размер шрифта", callback_data="show_sizes"),
    )
    markup.add(
        InlineKeyboardButton("Изменить текст", callback_data="edit_text"),
    )
    markup.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_direction")
    )
    return markup

def text_color_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(emoji, callback_data=f"setcolor:{color}") for emoji, color in text_colors]
    for i in range(0, 9, 3):
        markup.add(*buttons[i:i+3])
    markup.add(
        InlineKeyboardButton("Цвет фона", callback_data="show_bg"),
        InlineKeyboardButton("Размер шрифта", callback_data="show_sizes"),
    )
    markup.add(
        InlineKeyboardButton("Изменить текст", callback_data="edit_text"),
    )
    markup.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_direction")
    )
    return markup

def size_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(name, callback_data=f"setsize:{size}") for name, size in sizes]
    markup.add(*buttons)
    markup.add(
        InlineKeyboardButton("Цвет фона", callback_data="show_bg"),
        InlineKeyboardButton("Цвет текста", callback_data="show_text_colors"),
    )
    markup.add(
        InlineKeyboardButton("Изменить текст", callback_data="edit_text"),
    )
    markup.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_direction")
    )
    return markup

def speed_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(name, callback_data=f"setspeed:{value}") for name, value in speed_options]
    for i in range(0, 6, 3):
        markup.add(*buttons[i:i+3])
    return markup

def direction_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(name, callback_data=f"setdirection:{value}") for name, value in direction_options]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Управляй бегущей строкой кнопками 🎨 Меню ниже.", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "🎨 Меню")
def show_main_menu(message):
    bot.send_message(message.chat.id, "Выберите настройку:", reply_markup=bg_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setbg:"))
def callback_set_bg(call):
    color = call.data.split(":")[1]
    latest_command["bg"] = color
    bot.answer_callback_query(call.id, text=f"Фон сменён!")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"Фон сменён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setcolor:"))
def callback_set_color(call):
    color = call.data.split(":")[1]
    latest_command["color"] = color
    bot.answer_callback_query(call.id, text=f"Цвет текста: {color}")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"Цвет текста обновлён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setsize:"))
def callback_set_size(call):
    size = call.data.split(":")[1]
    latest_command["size"] = size
    bot.answer_callback_query(call.id, text=f"Размер шрифта: {size}")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"Размер шрифта: {size}", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "edit_text")
def callback_edit_text(call):
    waiting_text[call.from_user.id] = True
    bot.answer_callback_query(call.id, text="Введи новый текст")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "Отправь новый текст для бегущей строки:")

@bot.callback_query_handler(func=lambda call: call.data == "show_text_colors")
def show_text_colors(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=text_color_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_bg")
def show_bg_colors(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=bg_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_sizes")
def show_sizes(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=size_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_speed")
def show_speed(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=speed_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_direction")
def show_direction(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=direction_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setspeed:"))
def callback_set_speed(call):
    speed = call.data.split(":")[1]
    latest_command["speed"] = speed
    bot.answer_callback_query(call.id, text=f"Скорость: {speed}")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"Скорость движения: {speed}", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setdirection:"))
def callback_set_direction(call):
    direction = call.data.split(":")[1]
    latest_command["direction"] = direction
    bot.answer_callback_query(call.id, text=f"Направление: {('Влево' if direction=='left' else 'Вправо')}")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"Направление: {('⬅️ Влево' if direction=='left' else '➡️ Вправо')}", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    global latest_command
    if waiting_text.get(message.from_user.id, False):
        latest_command["text"] = message.text.strip()
        waiting_text[message.from_user.id] = False
        bot.reply_to(message, "Текст обновлён!")
    else:
        text = message.text.strip()
        if text.upper().startswith("ТЕКСТ:"):
            latest_command["text"] = text[6:].strip()
            bot.reply_to(message, "Текст обновлён!")
        elif text.upper().startswith("ЦВЕТ:"):
            latest_command["color"] = text[5:].strip()
            bot.reply_to(message, "Цвет текста обновлён!")
        elif text.upper().startswith("ФОН:"):
            latest_command["bg"] = text[4:].strip()
            bot.reply_to(message, "Цвет фона обновлён!")
        elif text.upper().startswith("РАЗМЕР:"):
            try:
                latest_command["size"] = str(int(text[7:].strip()))
                bot.reply_to(message, "Размер шрифта обновлён!")
            except Exception:
                bot.reply_to(message, "Ошибка: размер — только число.")
        else:
            bot.reply_to(message, "Используй кнопки 🎨 Меню ниже или команды:\nТЕКСТ: ...\nЦВЕТ: ...\nФОН: ...\nРАЗМЕР: ...")

@app.route('/api/latest', methods=['GET'])
def api_latest():
    apikey = request.args.get("apikey")
    if apikey != API_KEY:
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(latest_command)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    import threading
    threading.Thread(target=bot.polling, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
