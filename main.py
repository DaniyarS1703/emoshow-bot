import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "7377508266:AAHv1EKkXgP3AjVbcJHnaf505N-37HELKQw")
API_KEY = os.environ.get("API_KEY", "77777")

app = Flask(__name__)
CORS(app)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

latest_command = {
    "text": "Поздравляем с праздником! EMO",
    "color": "black",
    "bg": "white",
    "size": "100",
    "direction": "left",
    "speed": "3"
}
waiting_text = {}

# Цвета и настройки клавиатуры
bg_colors = [
    ("⬜", "white"), ("⬛", "black"), ("🟥", "red"), ("🟦", "blue"),
    ("🟩", "green"), ("🟨", "yellow"), ("🟧", "orange"), ("🟪", "purple"), ("🟫", "brown")
]
text_colors = [
    ("⚪", "white"), ("⚫", "black"), ("🔴", "red"), ("🔵", "blue"),
    ("🟢", "green"), ("🟡", "yellow"), ("🟠", "orange"), ("🟣", "purple"), ("🟤", "brown")
]
sizes = [
    ("100", "100"),
    ("120", "120"),
    ("140", "140"),
    ("160", "160"),
    ("180", "180"),
    ("200", "200"),
    ("220", "220"),
    ("240", "240"),
]
speed_options = [
    ("🐢 1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"),
    ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("⚡️ 10", "10")
]
direction_options = [("⬅️", "left"), ("🖥️ Экран", "bounce")]

def safe_edit_reply_markup(chat_id, message_id, reply_markup):
    try:
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except ApiTelegramException as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

def menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🎨 Меню"))
    return markup

def bg_keyboard():
    current_bg = latest_command.get("bg", "white")
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for emoji, color in bg_colors:
        label = emoji + (" ✅" if color == current_bg else "")
        buttons.append(InlineKeyboardButton(label, callback_data=f"setbg:{color}"))
    for i in range(0, 9, 3):
        markup.add(*buttons[i:i+3])
    markup.add(
        InlineKeyboardButton("Цвет текста", callback_data="show_text_colors"),
        InlineKeyboardButton("Размер шрифта", callback_data="show_sizes"),
    )
    markup.add(InlineKeyboardButton("Изменить текст", callback_data="edit_text"))
    markup.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_direction")
    )
    return markup

def text_color_keyboard():
    current_color = latest_command.get("color", "black")
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for emoji, color in text_colors:
        label = emoji + (" ✅" if color == current_color else "")
        buttons.append(InlineKeyboardButton(label, callback_data=f"setcolor:{color}"))
    for i in range(0, 9, 3):
        markup.add(*buttons[i:i+3])
    markup.add(
        InlineKeyboardButton("Цвет фона", callback_data="show_bg"),
        InlineKeyboardButton("Размер шрифта", callback_data="show_sizes"),
    )
    markup.add(InlineKeyboardButton("Изменить текст", callback_data="edit_text"))
    markup.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_direction")
    )
    return markup

def size_keyboard():
    current_size = latest_command.get("size", "100")
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name, size in sizes:
        label = name + (" ✅" if size == current_size else "")
        buttons.append(InlineKeyboardButton(label, callback_data=f"setsize:{size}"))
    markup.add(*buttons)
    markup.add(
        InlineKeyboardButton("Цвет фона", callback_data="show_bg"),
        InlineKeyboardButton("Цвет текста", callback_data="show_text_colors"),
    )
    markup.add(InlineKeyboardButton("Изменить текст", callback_data="edit_text"))
    markup.add(
        InlineKeyboardButton("Скорость", callback_data="show_speed"),
        InlineKeyboardButton("Направление", callback_data="show_direction")
    )
    return markup

def speed_keyboard():
    current_speed = latest_command.get("speed", "3")
    markup = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for name, value in speed_options:
        label = name + (" ✅" if value == current_speed else "")
        buttons.append(InlineKeyboardButton(label, callback_data=f"setspeed:{value}"))
    markup.add(*buttons)
    return markup

def direction_keyboard():
    current_direction = latest_command.get("direction", "left")
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name, value in direction_options:
        label = name + (" ✅" if value == current_direction else "")
        buttons.append(InlineKeyboardButton(label, callback_data=f"setdirection:{value}"))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"Start command from user {message.from_user.id}")
    bot.send_message(message.chat.id, "Добро пожаловать! Управляй бегущей строкой кнопками 🎨 Меню ниже.", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "🎨 Меню")
def show_main_menu(message):
    print(f"Menu requested by user {message.from_user.id}")
    bot.send_message(message.chat.id, "Выберите настройку:", reply_markup=bg_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setbg:"))
def callback_set_bg(call):
    color = call.data.split(":")[1]
    latest_command["bg"] = color
    print(f"Background changed to: {color} by user {call.from_user.id}")
    bot.answer_callback_query(call.id, text=f"Фон сменён!")
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, None)
    bot.send_message(call.message.chat.id, f"Фон сменён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setcolor:"))
def callback_set_color(call):
    color = call.data.split(":")[1]
    latest_command["color"] = color
    print(f"Text color changed to: {color} by user {call.from_user.id}")
    bot.answer_callback_query(call.id, text=f"Цвет текста: {color}")
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, None)
    bot.send_message(call.message.chat.id, f"Цвет текста обновлён!", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setsize:"))
def callback_set_size(call):
    size = call.data.split(":")[1]
    latest_command["size"] = size
    print(f"Font size changed to: {size} by user {call.from_user.id}")
    bot.answer_callback_query(call.id, text=f"Размер шрифта: {size}")
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, None)
    bot.send_message(call.message.chat.id, f"Размер шрифта: {size}", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "edit_text")
def callback_edit_text(call):
    waiting_text[call.from_user.id] = True
    print(f"User {call.from_user.id} is editing text")
    bot.answer_callback_query(call.id, text="Введи новый текст")
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, None)
    bot.send_message(call.message.chat.id, "Отправь новый текст для бегущей строки:")

@bot.callback_query_handler(func=lambda call: call.data == "show_text_colors")
def show_text_colors(call):
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=text_color_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_bg")
def show_bg_colors(call):
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=bg_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_sizes")
def show_sizes(call):
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=size_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_speed")
def show_speed(call):
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=speed_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "show_direction")
def show_direction(call):
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=direction_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setspeed:"))
def callback_set_speed(call):
    speed = call.data.split(":")[1]
    latest_command["speed"] = speed
    print(f"Speed changed to: {speed} by user {call.from_user.id}")
    bot.answer_callback_query(call.id, text=f"Скорость: {speed}")
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, None)
    bot.send_message(call.message.chat.id, f"Скорость движения: {speed}", reply_markup=menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setdirection:"))
def callback_set_direction(call):
    direction = call.data.split(":")[1]
    latest_command["direction"] = direction
    text_dir = "Влево" if direction == "left" else "Экран (отскок)"
    print(f"Direction changed to: {direction} by user {call.from_user.id}")
    bot.answer_callback_query(call.id, text=f"Направление: {text_dir}")
    safe_edit_reply_markup(call.message.chat.id, call.message.message_id, None)
    bot.send_message(call.message.chat.id, f"Направление: {text_dir}", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    global latest_command
    if waiting_text.get(message.from_user.id, False):
        latest_command["text"] = message.text.strip()
        waiting_text[message.from_user.id] = False
        bot.reply_to(message, "Текст обновлён!")
        print(f"Text updated to: {latest_command['text']} by user {message.from_user.id}")
    else:
        text = message.text.strip()
        if text.upper().startswith("ТЕКСТ:"):
            latest_command["text"] = text[6:].strip()
            bot.reply_to(message, "Текст обновлён!")
            print(f"Text updated to: {latest_command['text']} by user {message.from_user.id}")
        elif text.upper().startswith("ЦВЕТ:"):
            latest_command["color"] = text[5:].strip()
            bot.reply_to(message, "Цвет текста обновлён!")
            print(f"Color updated to: {latest_command['color']} by user {message.from_user.id}")
        elif text.upper().startswith("ФОН:"):
            latest_command["bg"] = text[4:].strip()
            bot.reply_to(message, "Цвет фона обновлён!")
            print(f"Background updated to: {latest_command['bg']} by user {message.from_user.id}")
        elif text.upper().startswith("РАЗМЕР:"):
            try:
                latest_command["size"] = str(int(text[7:].strip()))
                bot.reply_to(message, "Размер шрифта обновлён!")
                print(f"Size updated to: {latest_command['size']} by user {message.from_user.id}")
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
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

if __name__ == '__main__':
    import threading
    threading.Thread(target=bot.polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
