# Імпорт бібліотек
import telebot
from telebot import types
import sqlite3

API_KEY = '7266481714:AAFGxncNGTycTfwbq80L2JezMJndQV0KE7E'
bot = telebot.TeleBot(API_KEY)

# Функції для роботи з базою даних
def create_tables():
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS authorized_users (
            chat_id INTEGER PRIMARY KEY
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS work_users (
            chat_id INTEGER PRIMARY KEY
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            message_id INTEGER,
            message_text TEXT,
            sender_name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            message_id INTEGER,
            message_text TEXT,
            sender_name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            message_id INTEGER,
            message_text TEXT,
            sender_name TEXT,
            media_type TEXT,
            media_file_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_authorized_user(chat_id):
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO authorized_users (chat_id) VALUES (?)', (chat_id,))
    conn.commit()
    conn.close()

def add_work_user(chat_id):
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO work_users (chat_id) VALUES (?)', (chat_id,))
    conn.commit()
    conn.close()

def add_request(sender_id, message_id, message_text, sender_name):
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('INSERT INTO requests (sender_id, message_id, message_text, sender_name) VALUES (?, ?, ?, ?)',
              (sender_id, message_id, message_text, sender_name))
    conn.commit()
    conn.close()

def add_feedback(sender_id, message_id, message_text, sender_name):
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedbacks (sender_id, message_id, message_text, sender_name) VALUES (?, ?, ?, ?)',
              (sender_id, message_id, message_text, sender_name))
    conn.commit()
    conn.close()

def add_notification(sender_id, message_id, message_text, sender_name, media_type, media_file_id):
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO notifications (sender_id, message_id, message_text, sender_name, media_type, media_file_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (sender_id, message_id, message_text, sender_name, media_type, media_file_id))
    conn.commit()
    conn.close()

def get_authorized_users():
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM authorized_users')
    users = c.fetchall()
    conn.close()
    return {user[0] for user in users}

def get_work_users():
    conn = sqlite3.connect('craftmail.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM work_users')
    users = c.fetchall()
    conn.close()
    return {user[0] for user in users}

# Створення таблиць у базі даних
create_tables()
authorized_chat_ids = get_authorized_users()
work_chat_ids = get_work_users()

def main_menu_buttons(message, chat_id, text):
    if not message.chat.id in work_chat_ids:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = types.KeyboardButton("📦Надіслати запит на замовлення📦")
        b2 = types.KeyboardButton("🔄Перезапустити бота🔄")
        b3 = types.KeyboardButton("❔Відгук❔")
        markup.add(b1, b2, b3)
        bot.send_message(chat_id, text, reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = types.KeyboardButton("🔔Надіслати сповіщення🔔")
        b2 = types.KeyboardButton("🔄Перезапустити бота🔄")
        markup.add(b1, b2)
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    main_menu_buttons(message, message.chat.id, """Привіт, це CraftMail. Бот не призначений для тих, хто просто запустив бота.""")
    user_id = message.chat.id
    print(user_id)

@bot.message_handler(commands=['notification', 'nc'])
def notification(message):
    if message.chat.id in work_chat_ids:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = types.KeyboardButton("✖️Скасувати✖️")
        markup.add(b1)
        msg = bot.send_message(message.chat.id, "Надішліть текст або медіафайл сповіщення:", reply_markup=markup)
        bot.register_next_step_handler(msg, send_notification)
    else:
        bot.send_message(message.chat.id, "Ти не маєш прав на надсилання сповіщення.")

def send_notification(message):
    if message.text == "✖️Скасувати✖️":
        main_menu_buttons(message, message.chat.id, "Надсилання сповіщення скасовано.")
    elif message.chat.id in work_chat_ids:
        bot.send_message(message.chat.id, "Сповіщення надіслано.")
        for chat_id in authorized_chat_ids:
            caption = message.caption if message.caption else ""
            media_type = None
            media_file_id = None

            if message.photo:
                bot.send_photo(chat_id, message.photo[-1].file_id, caption=caption)
                media_type = 'photo'
                media_file_id = message.photo[-1].file_id
            elif message.video:
                bot.send_video(chat_id, message.video.file_id, caption=caption)
                media_type = 'video'
                media_file_id = message.video.file_id
            elif message.audio:
                bot.send_audio(chat_id, message.audio.file_id, caption=caption)
                media_type = 'audio'
                media_file_id = message.audio.file_id
            elif message.text:
                bot.send_message(chat_id, message.text)
                media_type = 'text'
                media_file_id = None

            add_notification(message.chat.id, message.id, message.text or caption, message.from_user.first_name, media_type, media_file_id)

@bot.message_handler(func=lambda message: True)
def menu(message):
    if message.text == "📦Надіслати запит на замовлення📦":
        if message.chat.id in authorized_chat_ids:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            b1 = types.KeyboardButton("✖️Скасувати✖️")
            markup.add(b1)
            msg = bot.send_message(message.chat.id, "Надішліть ваш запит (текст і/або медіафайл):", reply_markup=markup)
            bot.register_next_step_handler(msg, send_request)
        else:
            bot.send_message(message.chat.id, "Ти не маєш прав на надсилання запитів.")
    elif message.text == "🔄Перезапустити бота🔄":
        start(message)
    elif message.text == "❔Відгук❔":
        if message.chat.id in authorized_chat_ids:
            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            b1 = types.KeyboardButton("✖️Скасувати✖️")
            markup2.add(b1)
            msg = bot.send_message(message.chat.id, "Надішліть свій відгук (текст і/або медіафайл):", reply_markup=markup2)
            bot.register_next_step_handler(msg, feedback)
        else:
            bot.send_message(message.chat.id, "Ти не маєш прав на надсилання відгуків.")
    elif message.text == "🔔Надіслати сповіщення🔔":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = types.KeyboardButton("✖️Скасувати✖️")
        markup.add(b1)
        msg = bot.send_message(message.chat.id, "Надішліть текст сповіщення:", reply_markup=markup)
        bot.register_next_step_handler(msg, send_notification)
    else:
        bot.send_message(message.chat.id, "Ти щось хотів(-ла)?")

def send_request(message):
    global sender_id, sender_name, message_id, message_text
    if message.text == "✖️Скасувати✖️":
        main_menu_buttons(message, message.chat.id, "Запит на посилку скасований.")
    elif message.chat.id in authorized_chat_ids:
        markup = types.InlineKeyboardMarkup(row_width=2)
        b1 = types.InlineKeyboardButton("Прийняти", callback_data="allow")
        b2 = types.InlineKeyboardButton("Відхилити", callback_data="deny")
        markup.add(b1, b2)
        bot.send_message(message.chat.id, "Запит на посилку надіслано.")
        caption = f"{message.from_user.first_name}" if not message.caption else f"{message.from_user.first_name}:\n{message.caption}"

        if message.photo:
            bot.send_photo(5692636917, message.photo[-1].file_id, caption=caption, reply_markup=markup)
        elif message.video:
            bot.send_video(5692636917, message.video.file_id, caption=caption, reply_markup=markup)
        elif message.audio:
            bot.send_audio(5692636917, message.audio.file_id, caption=caption, reply_markup=markup)
        elif message.text:
            bot.send_message(5692636917, f"{message.from_user.first_name}:\n{message.text}", reply_markup=markup)

        sender_id = message.chat.id
        message_id = message.id
        message_text = message.text
        sender_name = message.from_user.first_name
        add_request(sender_id, message_id, message_text, sender_name)
        main_menu_buttons(message, message.chat.id, "Ваш запит на посилку надіслано.")
    elif message.chat.id in work_chat_ids:
        bot.send_message(message.chat.id, """Ти не можеш надсилати запити на посилку, оскільки ти робітник пошти.""")
    else:
        bot.send_message(message.chat.id, """Бот не призначений для тих, хто просто запустив бота.""")

def feedback(message):
    if message.text == "✖️Скасувати✖️":
        main_menu_buttons(message, message.chat.id, "Надсилання відгуку скасовано.")
    elif message.chat.id in authorized_chat_ids:
        bot.send_message(message.chat.id, "Відгук надіслано.")
        caption = f"{message.from_user.first_name}" if not message.caption else f"{message.from_user.first_name}:\n{message.caption}"

        if message.photo:
            bot.send_photo(-1002195476312, message.photo[-1].file_id, caption=caption)
        elif message.video:
            bot.send_video(-1002195476312, message.video.file_id, caption=caption)
        elif message.audio:
            bot.send_audio(-1002195476312, message.audio.file_id, caption=caption)
        elif message.text:
            bot.send_message(-1002195476312, f"{message.from_user.first_name}:\n{message.text}")

        add_feedback(message.chat.id, message.id, message.text or caption, message.from_user.first_name)
        main_menu_buttons(message, message.chat.id, "Ваш відгук надіслано.")
    elif message.chat.id in work_chat_ids:
        bot.send_message(message.chat.id, """Ти не можеш надсилати відгуки, оскільки ти робітник пошти.""")
    else:
        bot.send_message(message.chat.id, """Бот не призначений для тих, хто просто запустив бота.""")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'allow':
            bot.send_message(sender_id, "Ваше замовлення прийнято.")
        elif call.data == 'deny':
            bot.send_message(sender_id, "Ваше замовлення відхилено.")

# Запуск бота
def start_bot():
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"Error: {e}")

start_bot()
