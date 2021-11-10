from telegram import (
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import os
from emoji import emojize
from bot_project_new.utils import is_human_and_sfw, update_user_location, make_station_numbers_set, make_photo_path
from DbFolder.db_file import DBase
from handlers import start_keyboard
import pprint as pp
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from handlers import start

(
    STEP_NAME,
    STEP_AGE,
    STEP_EXPIRIENCE,
    STEP_LOCATION,
    STEP_INPUT,
    STEP_PHOTO,
    STEP_SPECIALITY,
    STEP_OTHER,
    STEP_DELETE,
    END
) = map(chr, range(10))

step_dict = {
    STEP_NAME: 'Введите ваше Имя и Фамилию (через пробел)',
    STEP_AGE: 'Введите ваш возраст (в годах)',
    STEP_EXPIRIENCE: 'Введите ваш опыт опыт(в годах)',
    STEP_LOCATION: ('''
    Введите район в котором вы проживаете, или ближайшую станцию метро
    '''),
    STEP_PHOTO: 'Прикрепите вашу фотографию',
    END: 'Вы завершили заполнение анкеты',
}

dbase = DBase()

def cv_main_keyboard(update, cotext):
    # основная клавиатура для анкеты
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    smile_yes = emojize(':white_check_mark:', use_aliases=True)
    smile_no = emojize(':white_medium_square:', use_aliases=True)
    if user['anketa']['show_cv']:
        text = f'{smile_yes}Убрать анкету из поиска'
    else:
        text = f'{smile_no}Добавить анкету в поиск'
    anketa_main_buttons = [
        [
            InlineKeyboardButton(text='ФИО', callback_data=STEP_NAME),
            InlineKeyboardButton(text='Возраст(в годах)', callback_data=STEP_AGE),
        ],
        [
            InlineKeyboardButton(text='Место работы', callback_data=STEP_LOCATION),
        ],
        [
            InlineKeyboardButton(text='Заполнить прочие пункты анкеты', callback_data=STEP_OTHER),
        ],
        [
            InlineKeyboardButton(text=text, callback_data=STEP_DELETE),
        ],
        [
            InlineKeyboardButton(text='Готово', callback_data=END),
        ]
    ]
    return InlineKeyboardMarkup(anketa_main_buttons)


def speciality_keyboard():
    speciality_buttons = [
        [
            InlineKeyboardButton(text='Врач', callback_data='Врач'),
            InlineKeyboardButton(text='Мед работник', callback_data='Мед работник'),
            InlineKeyboardButton(text='Ассистент', callback_data='Ассистент'),
        ],
    ]
    return InlineKeyboardMarkup(speciality_buttons)

speciality_pattern = ('^Врач$|^Мед работник$|^Ассистент$')
input_patterns = (f'^{STEP_AGE}$|^{STEP_LOCATION}$|^{STEP_NAME}$')

# Функция для показа пользователью анкеты данные подтягиваются из DB
def print_anketa_info(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    update.message.reply_text(
        f'''
        Ваши данные:
        Имя: {user['anketa']['name']
                if user['anketa'].get('name')
                else 'Значение не установлено'}
        Возраст: {user['anketa']['age']
                if user['anketa'].get('age')
                else 'Значение не установлено'}
        Опыт: {user['anketa']['expirience']
                if user['anketa'].get('expirience')
                else 'Значение не установлено'}
        Комментарий: {user['anketa']['komment']
                if user['anketa'].get('komment')
                else 'Значение не установлено'}
        Место жительства: {user['anketa']['location']
                if user['anketa'].get('location')
                else 'Значение не установлено'}
        Фото: {'Фото добавлено'
                if user['anketa'].get('photo')
                else 'Значение не установлено'}
        ''', reply_markup=cv_main_keyboard(update, context)
    )


# Функция обрабатывает нажатие пользователем клавиши на клавиатуре (анкеты)
# и переводит на соответствующий step
def ask_for_input(update, context):
    update.callback_query.answer()
    context.user_data['CURRENT_FEATURE'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE']
    text = step_dict[user_data_key]
    update.callback_query.edit_message_text(text=text)
    return user_data_key


def not_show_cv(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['anketa']['show_cv']:
        dbase.save_anketa(tg_id, 'show_cv', False)
        text = 'Анкета удалена из поиска'
    else:
        dbase.save_anketa(tg_id, 'show_cv', True)
        text = 'Анкета добавлена в поиск'
    update.callback_query.edit_message_text(text=text, reply_markup=cv_main_keyboard(update, context))
    return STEP_INPUT

def cv_move_other(update, context):
    pass

# Обработчик кнопки заполнить анкету
def cv_start(update, context):
    update.callback_query.answer()
    text = 'Пожалуйста, выберите вашу специальность'
    update.callback_query.edit_message_text(text=text, reply_markup=speciality_keyboard())
    return STEP_SPECIALITY


def choose_speciality(update, context):
    update.callback_query.answer()
    context.user_data['CURRENT_FEATURE'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE']
    print(user_data_key)
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'speciality', user_data_key)
    text = 'Пожалуйста заполните пункты анкеты'
    update.callback_query.edit_message_text(text=text, reply_markup=cv_main_keyboard(update, context))
    return STEP_INPUT


def choose_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста, введите ФИО(не менее 2-х слов)')
        return STEP_NAME
    else:
        tg_id = update.effective_user.id
        dbase.save_anketa(tg_id, 'name', user_name)
        print_anketa_info(update, context)
    return STEP_INPUT


def choose_age(update, context):
    user_age = update.message.text
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            tg_id = update.effective_user.id
            dbase.save_anketa(tg_id, 'age', user_age)
            print_anketa_info(update, context)
            return STEP_INPUT
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст')
            return STEP_AGE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст')
        return STEP_AGE


def choose_expirience(update, context):
    user_expirience = update.message.text
    try:
        user_expirience = int(user_expirience)
        if user_expirience > 0 and user_expirience < 100:
            tg_id = update.effective_user.id
            dbase.save_anketa(tg_id, 'expirience', user_expirience)
            print_anketa_info(update, context)
            return STEP_INPUT
        else:
            update.message.reply_text('Пожалуйста введите корректное число')
            return STEP_EXPIRIENCE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректное число')
        return STEP_EXPIRIENCE


def choose_location(update, context):
    user_location = update.message.text
    if update_user_location(user_location):
        user_location = update_user_location(user_location)
        station_numbers = make_station_numbers_set(user_location)
        tg_id = update.effective_user.id
        dbase.save_anketa(tg_id, 'location', user_location)
        dbase.save_anketa(tg_id, 'station_numbers', station_numbers)
        print_anketa_info(update, context)
        return STEP_INPUT
    else:
        update.message.reply_text('Один или несколько объектов не распознаны, попробуйте еще раз')
        return STEP_LOCATION


def check_user_photo(update, context):
    tg_id = update.effective_user.id
    update.message.reply_text('Обрабатываем фотографию')
    photo_path_list = []
    for id, photo in enumerate(update.message.photo[::-1]):
        user_photo = context.bot.getFile(photo.file_id)
        photo_path = make_photo_path(id, user_photo, 'downloads', update, context)
        photo_path_list.append(photo_path)

    if is_human_and_sfw(photo_path_list[0]):
        update.message.reply_text('Фото сохранено')
        files = os.listdir(path=f'images/{tg_id}')
        if files:
            for file in files:
                os.remove(f'images/{tg_id}/{file}')
        for id, photo in enumerate(update.message.photo):
            user_photo = context.bot.getFile(photo.file_id)
            photo_path = make_photo_path(id, user_photo, 'images', update, context)
            os.rename(photo_path_list[id], photo_path)
            photo_path_list[id] = photo_path
        files = os.listdir(path='downloads')
        for file in files:
            os.remove(f'downloads/{file}')
        dbase.save_anketa(tg_id, 'photo', photo_path_list)
        print_anketa_info(update, context)
        return STEP_INPUT
    else:
        update.message.reply_text('Фото не подхоидт, выберите другое')
        return STEP_PHOTO


# Функция дает ответ если пользователь в анкете не выбрал поле
def cv_fallback(update, context):
    text = 'Заполнение анкеты'
    update.message.reply_text(text=text, reply_markup=cv_main_keyboard(update, context))
    # не работает готово
    return STEP_INPUT


# Завершение анкеты выход из ConversationHandler
def end_describing(update, context):
    text = 'Вы завершили заполнение анкеты'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=start_keyboard())
    return ConversationHandler.END

anketa_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(cv_start, pattern='^' + 'Заполнить анкету' + '$')
    ],
    states={
        STEP_INPUT: [
            CallbackQueryHandler(ask_for_input, pattern=input_patterns),
            CallbackQueryHandler(cv_move_other, pattern='^' + str(STEP_OTHER) + '$'),
            CallbackQueryHandler(not_show_cv, pattern='^' + str(STEP_DELETE) + '$'),
        ],
        STEP_SPECIALITY: [CallbackQueryHandler(choose_speciality, pattern=speciality_pattern)],
        STEP_NAME: [MessageHandler(Filters.text, choose_name)],
        STEP_AGE: [MessageHandler(Filters.text, choose_age)],
        STEP_EXPIRIENCE: [MessageHandler(Filters.text, choose_expirience)],
        STEP_LOCATION: [MessageHandler(Filters.text, choose_location)],
        STEP_PHOTO: [MessageHandler(Filters.photo, check_user_photo)]
    },
    fallbacks=[
        MessageHandler(Filters.text | Filters.photo | Filters.video, cv_fallback),
        CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$')
    ]
)
