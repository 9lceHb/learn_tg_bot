from telegram import (
    ReplyKeyboardMarkup
  )

from DbFolder.db import get_or_create_user, db


def start_keyboard():
    return ReplyKeyboardMarkup([
        ['Найти работу'], ['Найти сотрудника']
            ], resize_keyboard=True)


# Обработка стартового хендлера (приветствие)
def start(update, context):
    get_or_create_user(db, update.effective_user, update.message.chat.id)
    reply_markup = start_keyboard()
    update.message.reply_text(
        ("Привет, я бот, который поможет тебе найти работу или сотрудника, моя"
            "область - медицина."
            "Пожалуйста укажите, для чего вы используете бота?"),
        reply_markup=reply_markup)


# Обработка кнопи - найти работу
def find_work(update, context):
    get_or_create_user(db, update.effective_user, update.message.chat.id)
    text = ("Вы можете смотеть вакансии или заполнить анкету,"
            " чтобы работодатель мог найти вас.")
    keyboard = ReplyKeyboardMarkup([
        ['Заполнить анкету'], ['Смотреть вакансии']
            ], resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=keyboard)
