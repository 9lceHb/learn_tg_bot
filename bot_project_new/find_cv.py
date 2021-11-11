from telegram import (
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import os
from bot_project_new.utils import (
    is_human_and_sfw,
    update_user_location,
    make_station_numbers_set,
    send_user_photo,
    send_user_info,
)

from DbFolder.db_file import DBase
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from handlers import start_keyboard

(
    STEP_FILTER_AGE,
    STEP_FILTER_EXPIRIENCE,
    STEP_FILTER_KOMMENT,
    STEP_FILTER_LOCATION,
    STEP_FILTER_INPUT,
    STEP_FILTER_PHOTO,
    STEP_SHOW_USERS,
    END
) = map(chr, range(8))
# from enum import Enum
# Задать класс
step_dict_cv = {
    STEP_FILTER_AGE: 'Задайте диапазон возраста - 2 цифры через пробел(в годах)',
    STEP_FILTER_EXPIRIENCE: 'Задайте диапазон опыта-2 цифры через пробел(в годах)',
    STEP_FILTER_KOMMENT: 'Наличие комментария, напишите "да" или "нет"',
    STEP_FILTER_LOCATION: '''
    Введите через запятую название метро или округа или района или линии метро
    Пример: Калининская линия, Первомайская, ЦАО
    ''',
    STEP_FILTER_PHOTO: 'Наличие фотографии, напишите "да" или "нет"',
    STEP_SHOW_USERS: 'Показываем пользователей'
}

dbase = DBase()

def filter_cv_keyboard():
    anketa_buttons = [
        [
            InlineKeyboardButton(text='Задать опыт', callback_data=str(STEP_FILTER_EXPIRIENCE)),
            InlineKeyboardButton(text='Задать возраст', callback_data=str(STEP_FILTER_AGE)),
        ],
        [
            InlineKeyboardButton(text='Наличие комментария', callback_data=str(STEP_FILTER_KOMMENT)),
            InlineKeyboardButton(text='Задать локацию для поиска', callback_data=str(STEP_FILTER_LOCATION)),
        ],
        [
            InlineKeyboardButton(text='Выход', callback_data=str(END)),
            InlineKeyboardButton(text='Наличие фото', callback_data=str(STEP_FILTER_PHOTO)),
        ],
        [
            InlineKeyboardButton(text='Показать резюме)', callback_data=str(STEP_SHOW_USERS)),
        ],
    ]
    return InlineKeyboardMarkup(anketa_buttons)


def use_filters_on_db(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    filters = []
    if user['filters'].get('photo'):
        is_photo = True
        filters.append({'anketa.photo': {'$exists': True}})
    else:
        is_photo = False

    if user['filters'].get('komment'):
        is_komment = True
        filters.append({'anketa.komment': {'$exists': True}})
    else:
        is_komment = False

    if user['filters'].get('age'):
        age_from = user['filters']['age'][0]
        age_to = user['filters']['age'][1]
        filters.append({'anketa.age': {'$gt': age_from}})
        filters.append({'anketa.age': {'$lt': age_to}})

    if user['filters'].get('expirience'):
        expirience_from = user['filters']['expirience'][0]
        expirience_to = user['filters']['expirience'][1]
        filters.append({'anketa.expirience': {'$gt': expirience_from}})
        filters.append({'anketa.expirience': {'$lt': expirience_to}})

    if user['filters'].get('location'):
        filter_station_numbers = user['filters']['station_numbers']
        filters.append({'anketa.station_numbers': {'$in': filter_station_numbers}})

    users_count = dbase.db_client.users.count_documents({'$and': filters})
    if filters:
        users_count = dbase.db_client.users.count_documents({'$and': filters})
        users = dbase.db_client.users.find({'$and': filters})
    else:
        users_count = dbase.db_client.users.count_documents({})
        users = dbase.db_client.users.find({})
    return users_count, users


def print_filters_info(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    update.message.reply_text(
        f'''
        Ваши фильтры:
        Возраст: {user['filters']['age']
                if user['filters'].get('age')
                else 'фильтр не установлен'}
        Опыт: {user['filters']['expirience']
                if user['filters'].get('expirience')
                else 'фильтр не установлен'}
        Комментарий: {'Наличие необходимо'
                if user['filters'].get('komment') == True
                else 'наличие не обязательно'}
        Локация: {user['filters']['location']
                if user['filters'].get('location')
                else 'фильтр не установлен'}
        Фото: {'Наличие необходимо'
                if user['filters'].get('photo') == True
                else 'наличие не обязательно'}
        Количество пользователей, найденных по вашему запросу: {use_filters_on_db(update, context)[0]}
        ''', reply_markup=filter_cv_keyboard()
    )

def filter_cv_start(update, context):
    update.callback_query.answer()
    text = 'Поиск резюме, выберите фильтры поиска'
    update.callback_query.edit_message_text(text=text, reply_markup=filter_cv_keyboard())
    return STEP_FILTER_INPUT


def filter_ask_for_input(update, context):
    """Prompt user to input data for selected feature."""
    update.callback_query.answer()
    context.user_data['CURRENT_FEATURE_CV'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE_CV']
    text = step_dict_cv[user_data_key]
    update.callback_query.edit_message_text(text=text)
    return user_data_key


def filter_age(update, context):
    filter_value = update.message.text
    filter_value = filter_value.split(' ')
    tg_id = update.effective_user.id
    if len(filter_value) != 2:
        update.message.reply_text('Пожалуйста, введите 2 числа, через пробел')
        return STEP_FILTER_AGE
    try:
        filter_value[0] = int(filter_value[0])
        filter_value[1] = int(filter_value[1])
        dbase.save_filters(tg_id, 'age', filter_value)
        print_filters_info(update, context)
        return STEP_FILTER_INPUT
    except ValueError:
        update.message.reply_text('Пожалуйста, введите 2 числа, через пробел')
        return STEP_FILTER_AGE

def filter_expirience(update, context):
    filter_value = update.message.text
    filter_value = filter_value.split(' ')
    tg_id = update.effective_user.id
    if len(filter_value) != 2:
        update.message.reply_text('Пожалуйста, введите 2 числа, через пробел')
        return STEP_FILTER_EXPIRIENCE
    try:
        filter_value[0] = int(filter_value[0])
        filter_value[1] = int(filter_value[1])
        dbase.save_filters(tg_id, 'expirience', filter_value)
        print_filters_info(update, context)
        return STEP_FILTER_INPUT
    except ValueError:
        update.message.reply_text('Пожалуйста, введите 2 числа, через пробел')
        return STEP_FILTER_EXPIRIENCE

def filter_komment(update, context):
    tg_id = update.effective_user.id
    try:
        answer = update.message.text
        answer = answer.lower()
        if answer == 'нет':
            answer = False
            dbase.save_filters(tg_id, 'komment', answer)
            print_filters_info(update, context)
            return STEP_FILTER_INPUT
        elif answer == 'да':
            answer = True
            dbase.save_filters(tg_id, 'komment', answer)
            print_filters_info(update, context)
            return STEP_FILTER_INPUT
        else:
            update.message.reply_text('Пожалуйста введите "да" или "нет"')
            return STEP_FILTER_KOMMENT
    except ValueError:
        update.message.reply_text('Пожалуйста введите "да" или "нет"')
        return STEP_FILTER_KOMMENT

def filter_location(update, context):
    user_location = update.message.text
    if update_user_location(user_location):
        user_location = update_user_location(user_location)
        station_numbers = make_station_numbers_set(user_location)
        tg_id = update.effective_user.id
        dbase.save_filters(tg_id, 'location', user_location)
        dbase.save_filters(tg_id, 'station_numbers', station_numbers)
        print_filters_info(update, context)
        return STEP_FILTER_INPUT
    else:
        update.message.reply_text('Один или несколько объектов не распознаны, попробуйте еще раз')
        return STEP_FILTER_LOCATION

def filter_photo(update, context):
    tg_id = update.effective_user.id
    try:
        answer = update.message.text
        answer = answer.lower()
        if answer == 'нет':
            answer = False
            dbase.save_filters(tg_id, 'photo', answer)
            print_filters_info(update, context)
            return STEP_FILTER_INPUT
        elif answer == 'да':
            answer = True
            dbase.save_filters(tg_id, 'photo', answer)
            print_filters_info(update, context)
            return STEP_FILTER_INPUT
        else:
            update.message.reply_text('Пожалуйста введите "да" или "нет"')
            return STEP_FILTER_PHOTO
    except ValueError:
        update.message.reply_text('Пожалуйста введите "да" или "нет"')
        return STEP_FILTER_PHOTO

def show_users(update, context):
    update.callback_query.answer()
    print('+')
    count = use_filters_on_db(update, context)[0]
    users = use_filters_on_db(update, context)[1]
    users_list = []
    for user in users:
        users_list.append(user)
    user_photos = users_list[0]['anketa']['photo']
    for photo in user_photos:
        if 'mid' in photo:
            user_photo = photo
    text = send_user_info(users_list[0])
    send_user_photo(update, context, user_photo)
    update.callback_query.edit_message_text(text=text)
    return STEP_FILTER_INPUT


def filter_fallback(update, context):
    update.message.reply_text('Пожалуйста выберите поле из списка!')

def end_filter(update, context):
    update.callback_query.answer()
    text = 'Вы завершили заполнение фильтров, для продолжения работы нажмите /start'
    update.callback_query.edit_message_text(text=text, reply_markup=None)
    return ConversationHandler.END


pattern = (
    f'^{STEP_FILTER_AGE}$|'
    '^{STEP_FILTER_EXPIRIENCE}$|'
    '^{STEP_FILTER_KOMMENT}$|'
    '^{STEP_FILTER_LOCATION}$|'
    '^{STEP_FILTER_PHOTO}$'
)

filter_cv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(filter_cv_start, pattern='^' + 'Найти сотрудника' + '$')
    ],
    states={
        STEP_FILTER_INPUT: [
            CallbackQueryHandler(filter_ask_for_input, pattern=pattern),
            CallbackQueryHandler(show_users, pattern='^' + str(STEP_SHOW_USERS) + '$')
        ],
        STEP_FILTER_AGE: [MessageHandler(Filters.text, filter_age)],
        STEP_FILTER_EXPIRIENCE: [MessageHandler(Filters.text, filter_expirience)],
        STEP_FILTER_KOMMENT: [MessageHandler(Filters.text, filter_komment)],
        STEP_FILTER_LOCATION: [MessageHandler(Filters.text, filter_location)],
        STEP_FILTER_PHOTO: [MessageHandler(Filters.text, filter_photo)],
    },
    fallbacks=[
        MessageHandler(Filters.text | Filters.photo | Filters.video, filter_fallback),
        CallbackQueryHandler(end_filter, pattern='^' + str(END) + '$')
    ]
)
