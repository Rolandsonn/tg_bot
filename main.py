import os
from dotenv import load_dotenv
import telebot
from telebot import types
import psycopg2

load_dotenv()
token_api = os.getenv("TOKEN_KEY")

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
)
conn.autocommit = True

cursor = conn.cursor()


cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS tele_users (
            ID  SERIAL PRIMARY KEY,
            Name varchar(30),
            Age integer
        )
    """
)


bot = telebot.TeleBot(token_api)

name = ""
surname = ""
age = 0


@bot.message_handler(content_types=["text"])
def start(message, res=False):
    chat_id = message.chat.id

    if message.text == "/reg":
        bot.send_message(chat_id, "Напишите ваше имя")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(chat_id, "Напиши /reg")


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, "Какая у тебя Фамилия?")
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.chat.id, "Напиши ваш возраст")
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age

    while age == 0:
        try:
            age = int(message.text)
        except Exception:
            bot.send_message(message.chat.id, "Цифрами, пожалуйста")

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text="yes", callback_data="yes")
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text="no", callback_data="no")
    keyboard.add(key_no)
    question = f"Тебе {str(age)} лет, тебя зовут {name} {surname} ?"
    bot.send_message(message.chat.id, question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def call_back(call):

    if call.data == "yes":
        user_name = name + surname
        # код добавления в базу
        cursor.execute(
            """
                       INSERT INTO tele_users(name, age)
                       VALUES(%s, %s)
                       """,
            (name, age),
        )
        bot.send_message(call.message.chat.id, text="Вы успешно заргистрированы")


bot.polling(none_stop=True, interval=0)

# sdgfsf
