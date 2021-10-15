from telegram import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    callbackquery,
    replymarkup
)
import os

from telegram.ext import ConversationHandler
from bot_project.utils import is_human_and_sfw
from DbFolder.db import db, get_or_create_user, save_anketa

(
    STEP_NAME,
    STEP_AGE,
    STEP_EXPIRIENCE,
    STEP_KOMMENT,
    STEP_LOCATION,
    STEP_INPUT,
    STEP_PHOTO,
    END
) = map(chr, range(8))

step_dict = {
    STEP_NAME: 'Имя, Фамилия',
    STEP_AGE: 'Возраст(в годах)',
    STEP_EXPIRIENCE: 'Опыт(в годах)',
    STEP_KOMMENT: 'Комментарий',
    STEP_LOCATION: 'Локация',
    STEP_PHOTO: 'Ваша фотография'}


def anketa_keyboard():
    anketa_buttons = [
            [
                InlineKeyboardButton(
                    text='Имя, Фамилия', callback_data=str(STEP_NAME)
                    ),
                InlineKeyboardButton(
                    text='Возраст(в годах)', callback_data=str(STEP_AGE)
                    ),
            ],
            [
                InlineKeyboardButton(
                    text='Опыт(в годах)', callback_data=str(STEP_EXPIRIENCE)
                    ),
                InlineKeyboardButton(
                    text='Комментарий', callback_data=str(STEP_KOMMENT)
                    ),
                InlineKeyboardButton(
                    text='Локация', callback_data=str(STEP_LOCATION)
                    ),
            ],
            [
                InlineKeyboardButton(text='Готово', callback_data=str(END)),
                InlineKeyboardButton(
                    text='Добавить фото', callback_data=str(STEP_PHOTO)
                    )
            ]
        ]
    return InlineKeyboardMarkup(anketa_buttons)


def print_anketa_info(update, context, db):
    tg_id = update.effective_user.id
    user = db.users.find_one({'tg_id': tg_id})
    update.message.reply_text(
        f'''
        Ваши данные:
        Имя: {user['anketa']['name'] if user['anketa'].get('name') else 'Значение не установлено'}
        Возраст: {user['anketa']['age'] if user['anketa'].get('age') else 'Значение не установлено'}
        Опыт: {user['anketa']['expirience'] if user['anketa'].get('expirience') else 'Значение не установлено'}
        Комментарий: {user['anketa']['komment'] if user['anketa'].get('komment') else 'Значение не установлено'}
        Место жительства: {user['anketa']['location'] if user['anketa'].get('location') else 'Значение не установлено'}
        ''', reply_markup=anketa_keyboard()
        )


def ask_for_input(update, context):
    """Prompt user to input data for selected feature."""
    context.user_data['CURRENT_FEATURE'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE']
    print(update.callback_query.data)
    text = f'Пожалуйста введите значение для поля-{step_dict[user_data_key]}:'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return user_data_key


def anketa_start(update, context):
    update.message.reply_text(
        'Заполнение анкеты',
        reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_text(
        "Выберите поле для заполнения",
        reply_markup=anketa_keyboard())
    return STEP_INPUT


def anketa_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста введите корректно имя и фамилию')
        return STEP_NAME
    else:
        tg_id = update.effective_user.id
        save_anketa(db, tg_id, 'name', user_name)
        print_anketa_info(update, context, db)
    return STEP_INPUT


def anketa_age(update, context):
    user_age = update.message.text
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            tg_id = update.effective_user.id
            save_anketa(db, tg_id, 'age', user_age)
            print_anketa_info(update, context, db)
            return STEP_INPUT
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст')
            return STEP_AGE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст')
        return STEP_AGE


def anketa_expirience(update, context):
    user_expirience = update.message.text
    try:
        user_expirience = int(user_expirience)
        if user_expirience > 0 and user_expirience < 100:
            tg_id = update.effective_user.id
            save_anketa(db, tg_id, 'expirience', user_expirience)
            print_anketa_info(update, context, db)
            return STEP_INPUT
        else:
            update.message.reply_text('Пожалуйста введите корректное число')
            return STEP_EXPIRIENCE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректное число')
        return STEP_EXPIRIENCE


def anketa_komment(update, context):
    user_komment = update.message.text
    tg_id = update.effective_user.id
    save_anketa(db, tg_id, 'komment', user_komment)
    print_anketa_info(update, context, db)
    return STEP_INPUT


def anketa_location(update, context):
    user_location = update.message.text
    tg_id = update.effective_user.id
    save_anketa(db, tg_id, 'location', user_location)
    print_anketa_info(update, context, db)
    return STEP_INPUT


def check_user_photo(update, context):
    update.message.reply_text('Обрабатываем фотографию')
    os.makedirs('downloads', exist_ok=True)
    user_photo = context.bot.getFile(update.message.photo[0].file_id)
    file_name = os.path.join('downloads', f'{user_photo.file_id}.jpg')
    user_photo.download(file_name)
    if is_human_and_sfw(file_name):
        update.message.reply_text('Фото сохранено', reply_markup=anketa_keyboard())
    else:
        update.message.reply_text('фото не подходит:(', reply_markup=anketa_keyboard())
    return STEP_INPUT


def anketa_fallback(update, context):
    update.message.reply_text('Пожалуйста выберите поле из списка!')


def end_describing(update, context):
    text = 'Вы завершили заполнение анкеты'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return ConversationHandler.END
