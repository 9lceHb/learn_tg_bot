from typing import Text
import base64
import os
from telegram import ParseMode, LabeledPrice
from utils import (
    update_user_location,
    make_station_numbers_set,
    print_filter_age,
    print_location,
    firsttime_user,
    print_specialisation,
    print_cv,
    clear_photo,
)
from handlers import start_keyboard
from telegram.ext import (
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
)
from payments import payment_conv_handler

from DbFolder.db_file import DBase
dbase = DBase()
from keyboards import(
    filter_main_keyboard,
    filter_speciality_keyboard,
    filter_invite_keyboard,
    filter_specialisation_keyboard,
    filter_schedule_keyboard,
    filter_salary_keyboard,
    filter_education_keyboard,
    filter_experience_keyboard,
    filter_photo_keyboard,
    show_cv_keyboard,
    STEP_FILTER_AGE,
    STEP_FILTER_EXPERIENCE,
    STEP_FILTER_LOCATION,
    STEP_FILTER_MAIN,
    STEP_FILTER_PHOTO,
    STEP_FILTER_SPECIALITY,
    STEP_WRITE_SPECIALITY,
    STEP_FILTER_SPECIALISATION,
    STEP_FILTER_SCHEDULE,
    STEP_FILTER_SALARY,
    STEP_FILTER_EDUCATION,
    STEP_SHOW_CV,
    STEP_FILTER_END,
)


def print_filter_info(update, context, callback=True):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    dbase.db_client.users.update_one({'_id': user['_id']}, {'$set': {'filter.first_time': False}})
    if user['filter']['speciality'] == 'Стоматолог':
        specialisation_text = f'''\n  <b>Специализация:</b> {print_specialisation(tg_id, 'filter')}'''
        education_text = ''
    else:
        specialisation_text = ''
        education_text = (
            f'''\n  <b>Образование:</b> {user['filter']['education']
            if user['filter'].get('education')
            else 'Фильтр не установлен'}'''
        )
    text = f'''
<em>Ваши параметры поиска:</em>
  <b>Специальность:</b> {user['filter']['speciality']
          if user['filter'].get('speciality')
          else 'Фильтр не установлен'}{specialisation_text}
  <b>График работы:</b> {user['filter']['schedule']
          if user['filter'].get('schedule')
          else 'Фильтр не установлен'}
  <b>Минимальная оплата труда:</b> {user['filter']['salary']
          if user['filter'].get('salary')
          else 'Фильтр не установлен'}
  <b>Предпочитительное место работы:</b>\n{print_location(tg_id, 'filter') if user['filter'].get('location')
          else 'Фильтр не установлен'}
  <b>Возраст:</b> {print_filter_age(tg_id)
          if user['filter'].get('age')
          else 'Фильтр не установлен'}{education_text}
  <b>Опыт:</b> {user['filter']['experience']
          if user['filter'].get('experience')
          else 'Фильтр не установлен'}
  <b>Наличие фото:</b> {'Фото необходимо'
          if user['filter'].get('photo')
          else 'Фото не обязательно'}
<em>Количество анкет, найденных по вашим фильтрам:</em> {use_filters_on_db(tg_id)[0]}
'''
    reply_markup = filter_main_keyboard(update, context)
    if callback:
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

show_cv_patterns = (
    f'^' + 'show_cv_back' + '$|'
    f'^' + 'show_cv_next' + '$|'
    f'^' + 'show_cv_end' + '$|'
    f'^' + 'payment_back_filter' + '$'
)
filter_patterns = (
    f'^{STEP_FILTER_AGE}$|'
    f'^{STEP_FILTER_LOCATION}$|'
    f'^{STEP_FILTER_SPECIALITY}$|'
    f'^{STEP_FILTER_SPECIALISATION}$|'
    f'^{STEP_FILTER_SCHEDULE}$|'
    f'^{STEP_FILTER_SALARY}$|'
    f'^{STEP_FILTER_EXPERIENCE}$|'
    f'^{STEP_FILTER_EDUCATION}$|'
    f'^{STEP_FILTER_PHOTO}$'
)

def get_filter_text(key, tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if key == STEP_FILTER_AGE:
        text = '''
Установите желаемый диапазон возраста(2 цифры через '-')
<b>Пример:</b> 18-34
'''
        keyboard = None
    elif key == STEP_FILTER_LOCATION:
        text = '''
Установите желаемое местоположение.
(Вы можете вводить через запятую необходимые станции метро, линии метро, районы, округа).
<b>Пример:</b> "Речной вокзал, САО".
'''
        keyboard = None
    elif key == STEP_FILTER_SPECIALITY:
        text = '''
Какой специалист вам нужен?
'''
        keyboard = filter_speciality_keyboard()
    elif key == STEP_FILTER_SPECIALISATION:
        text = f'''
Врач какой специализации вам необходим?
(можно выбрать один или несколько пунктов)
<b>Ваш текущий выбор:</b> {print_specialisation(tg_id, 'filter')}
'''
        keyboard = filter_specialisation_keyboard(tg_id)
    elif key == STEP_FILTER_SCHEDULE:
        text = '''
Задайте желаемый график работы
'''
        keyboard = filter_schedule_keyboard(tg_id)
    elif key == STEP_FILTER_SALARY:
        if user['filter']['speciality'] != 'Стоматолог':
            text = '''
Выберите минимальную оплату сотрудника за смену(полдня, 6 - 8 часов).
'''
        else:
            text = '''
Выберите минимальную зароботную плата врача за месяц.
'''
        keyboard = filter_salary_keyboard(tg_id)
    elif key == STEP_FILTER_EDUCATION:
        text = '''
Выберите желаемое образование сотрудника.
'''
        keyboard = filter_education_keyboard(tg_id)
    elif key == STEP_FILTER_EXPERIENCE:
        text = '''
Выберите желаемый опыт работы сотрудника.
'''
        keyboard = filter_experience_keyboard(tg_id)
    elif key == STEP_FILTER_PHOTO:
        text = '''
Выберите необходимость наличия фото
'''
        keyboard = filter_photo_keyboard(tg_id)
    else:
        text = 'Вы завершили выбор фильров'
        keyboard = None
    return text, keyboard


def use_filters_on_db(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    filters = []
    filters.append({'cv.show_cv': {'$eq': True}})
    if user['filter'].get('speciality'):
        filters.append({'cv.speciality': {'$eq': user['filter'].get('speciality')}})

    if user['filter'].get('specialisation'):
        filter_specialisation = user['filter'].get('specialisation')
        filters.append({'cv.specialisation': {'$in': filter_specialisation}})

    if user['filter'].get('photo'):
        filters.append({'cv.photo': {'$ne': False}})

    if user['filter'].get('age'):
        age_from = user['filter']['age'][0]
        age_to = user['filter']['age'][1]
        filters.append({'cv.age': {'$gte': age_from}})
        filters.append({'cv.age': {'$lte': age_to}})

    if user['filter'].get('experience_key'):
        experience_filter = user['filter']['experience_key']
        filters.append({'cv.experience_key': {'$gte': experience_filter}})

    if user['filter'].get('education_key'):
        education_filter = user['filter']['education_key']
        filters.append({'cv.education_key': {'$gte': education_filter}})

    if user['filter'].get('salary_key'):
        salary_filter = user['filter']['salary_key']
        filters.append({'cv.salary_key': {'$lte': salary_filter}})

    if user['filter'].get('location'):
        filter_station_numbers = user['filter']['station_numbers']
        filters.append({'cv.station_numbers': {'$in': filter_station_numbers}})

    if user['filter'].get('schedule'):
        schedule_filter = user['filter'].get('schedule')
        if schedule_filter != 'любой график':
            filters.append({'cv.schedule': {'$eq': user['filter'].get('schedule')}})

    if filters:
        users_count = dbase.db_client.users.count_documents({'$and': filters})
        users = dbase.db_client.users.find({'$and': filters})
    else:
        users_count = dbase.db_client.users.count_documents({})
        users = dbase.db_client.users.find({})
    tg_id_list = []
    for user in users:
        tg_id_list.append(user['tg_id'])
    return users_count, tg_id_list


def manage_filter_button(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    context.user_data['CURRENT_FEATURE_FILTER'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE_FILTER']
    text = get_filter_text(user_data_key, tg_id)[0]
    reply_markup = get_filter_text(user_data_key, tg_id)[1]
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return user_data_key

def filter_start(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if firsttime_user(tg_id, 'filter'):
        text = '''
Пожалуйста, задайте важные для Вас параметры, и я покажу анкеты, которые подходят для Вас наилучшим образом!
'''
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=filter_invite_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return STEP_WRITE_SPECIALITY
    else:
        print_filter_info(update, context)
        return STEP_FILTER_MAIN


def write_speciality(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    text = get_filter_text(STEP_FILTER_SPECIALITY, tg_id)[0]
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=filter_speciality_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return STEP_FILTER_SPECIALITY


def filter_speciality(update, context):
    update.callback_query.answer()
    filter_speciality = update.callback_query.data
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['filter'].get('speciality') != filter_speciality:
        dbase.clear_filters(tg_id)
    dbase.save_filter(tg_id, 'speciality', filter_speciality)
    print_filter_info(update, context)
    return STEP_FILTER_MAIN


def filter_specialisation(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if update.callback_query.data == 'end_specialisation_f':
        print_filter_info(update, context)
        return STEP_FILTER_MAIN
    else:
        filter_specialisation = update.callback_query.data
        dbase.update_specialisation(tg_id, filter_specialisation, 'filter')
        text = get_filter_text(STEP_FILTER_SPECIALISATION, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=filter_specialisation_keyboard(tg_id),
            parse_mode=ParseMode.HTML
        )
        return STEP_FILTER_SPECIALISATION


def filter_schedule(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    filter_schedule = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_filter(tg_id, 'schedule', filter_schedule)
    print_filter_info(update, context)
    return STEP_FILTER_MAIN


def filter_location(update, context):
    filter_location = update.message.text
    tg_id = update.effective_user.id
    if update_user_location(filter_location):
        filter_location = update_user_location(filter_location)
        filter_station_numbers = make_station_numbers_set(filter_location)
        dbase.save_filter(tg_id, 'location', filter_location)
        dbase.save_filter(tg_id, 'station_numbers', filter_station_numbers)
        print_filter_info(update, context, callback=False)
        return STEP_FILTER_MAIN
    else:
        update.message.reply_text('Один или несколько объектов не распознаны, попробуйте еще раз')
        return STEP_FILTER_LOCATION


def filter_salary(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    filter_data = update.callback_query.data
    filter_salary = filter_data.split('/')[0]
    filter_salary_key = filter_data.split('/')[1]
    dbase.save_filter(tg_id, 'salary', filter_salary)
    dbase.save_filter(tg_id, 'salary_key', filter_salary_key)
    print_filter_info(update, context)
    return STEP_FILTER_MAIN


def filter_age(update, context):
    filter_age = update.message.text
    tg_id = update.effective_user.id
    fail_text = '''
Пожалуйста, корректно укажите желаемчй диапазон возраста(2 цифры через '-')
<b>Пример:</b> 18-34
'''
    if '-' in filter_age:
        filter_age = filter_age.split('-')
        for i, age in enumerate(filter_age):
            filter_age[i] = age.strip()
    else:
        update.message.reply_text(text=fail_text, parse_mode=ParseMode.HTML)
        return STEP_FILTER_AGE
    if len(filter_age) != 2:
        update.message.reply_text(text=fail_text, parse_mode=ParseMode.HTML)
        return STEP_FILTER_AGE
    try:
        filter_age[0] = int(filter_age[0])
        filter_age[1] = int(filter_age[1])
        filter_age = sorted(filter_age)
        dbase.save_filter(tg_id, 'age', filter_age)
        print_filter_info(update, context, callback=False)
        return STEP_FILTER_MAIN
    except ValueError:
        update.message.reply_text(text=fail_text, parse_mode=ParseMode.HTML)
        return STEP_FILTER_AGE


def filter_education(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    filter_data = update.callback_query.data
    filter_education = filter_data.split('/')[0]
    filter_education_key = filter_data.split('/')[1]
    if filter_education == 'среднее мед., неоконченное':
        filter_education = 'среднее медицинское, неоконченное'
    dbase.save_filter(tg_id, 'education', filter_education)
    dbase.save_filter(tg_id, 'education_key', filter_education_key)
    print_filter_info(update, context)
    return STEP_FILTER_MAIN


def filter_experience(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    filter_data = update.callback_query.data
    filter_experience = filter_data.split('/')[0]
    filter_experience_key = filter_data.split('/')[1]
    if filter_experience == 'Звездный Ассистент':
        filter_experience = 'выпускник курса "Звездный Ассистент"'
    dbase.save_filter(tg_id, 'experience', filter_experience)
    dbase.save_filter(tg_id, 'experience_key', filter_experience_key)
    print_filter_info(update, context)
    return STEP_FILTER_MAIN


def filter_photo(update, context):
    update.callback_query.answer()
    filter_photo = update.callback_query.data
    tg_id = update.effective_user.id
    if filter_photo == 'Фото необходимо':
        filter_photo = True
    elif filter_photo == 'Фото не обязательно':
        filter_photo = False
    dbase.save_filter(tg_id, 'photo', filter_photo)
    print_filter_info(update, context)
    return STEP_FILTER_MAIN

def show_cv_first(update, context):
    update.callback_query.answer()
    current_tg_id = update.effective_user.id
    users_count, tg_id_list = use_filters_on_db(current_tg_id)
    if users_count == 0:
        dbase.save_filter(current_tg_id, 'show_cv_tg_id', {'tg_id_list': tg_id_list})
        reply_markup = show_cv_keyboard(current_tg_id)
        text = 'К сожалению по вашему запросу анкеты не найдены'
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return STEP_SHOW_CV
    for_show_user_id = tg_id_list[0]
    dbase.save_filter(current_tg_id, 'show_cv_tg_id', {'tg_id_list': tg_id_list, 'showed_tg_id': for_show_user_id})
    user = dbase.db_client.users.find_one({'tg_id': current_tg_id})
    balance = user['balance']
    text = print_cv(for_show_user_id, balance)
    reply_markup = show_cv_keyboard(current_tg_id)
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_SHOW_CV

def show_cv(update, context):
    update.callback_query.answer()
    if update.callback_query.data == 'show_cv_end':
        print_filter_info(update, context)
        return STEP_FILTER_MAIN
    # if update.callback_query.data == 'pay_balance':
    #     send_payment_invoice(update, context)
    current_tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': current_tg_id})
    current_user = dbase.db_client.users.find_one({'tg_id': current_tg_id})
    showed_user_id = current_user['filter']['show_cv_tg_id']['showed_tg_id']
    tg_id_list = current_user['filter']['show_cv_tg_id']['tg_id_list']
    if update.callback_query.data == 'show_cv_back':
        for_show_user_id = tg_id_list[tg_id_list.index(showed_user_id) - 1]
        dbase.save_filter(current_tg_id, 'show_cv_tg_id', {'tg_id_list': tg_id_list, 'showed_tg_id': for_show_user_id})
    elif update.callback_query.data == 'show_cv_next':
        for_show_user_id = tg_id_list[tg_id_list.index(showed_user_id) + 1]
        dbase.save_filter(current_tg_id, 'show_cv_tg_id', {'tg_id_list': tg_id_list, 'showed_tg_id': for_show_user_id})
    else:
        for_show_user_id = user['filter']['show_cv_tg_id']['showed_tg_id']
    balance = user['balance']
    text = print_cv(for_show_user_id, balance)
    reply_markup = show_cv_keyboard(current_tg_id)
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_SHOW_CV

def show_photo(update, context):
    current_tg_id = update.effective_user.id
    current_user = dbase.db_client.users.find_one({'tg_id': current_tg_id})
    showed_user_id = current_user['filter']['show_cv_tg_id']['showed_tg_id']
    showed_user = dbase.db_client.users.find_one({'tg_id': showed_user_id})
    user = dbase.db_client.users.find_one({'tg_id': current_tg_id})
    balance = user['balance']
    text = print_cv(showed_user_id, balance)
    photo_str = showed_user['cv'].get('photo')
    os.makedirs(f'downloads/{showed_user_id}', exist_ok=True)
    photo_path = os.path.join('downloads', f'{showed_user_id}', 'user_photo.jpg')
    with open(photo_path, "wb") as fimage:
        fimage.write(base64.decodebytes(photo_str))
    chat_id = update.effective_chat.id
    reply_markup = show_cv_keyboard(current_tg_id)
    context.bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))
    clear_photo(showed_user_id)
    update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_SHOW_CV


# Завершение анкеты выход из ConversationHandler
def end_describing_filter(update, context):
    text = 'Вы завершили редактирование фильров, выберите пункт меню.'
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=start_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

def filter_fallback(update, context):
    tg_id = update.effective_user.id
    if firsttime_user(tg_id, 'filter'):
        text = '''
Пожалуйста, задайте важные для Вас параметры, и я покажу анкеты, которые подходят для Вас наилучшим образом!
'''
        update.message.reply_text(
            text=text,
            reply_markup=filter_invite_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return STEP_WRITE_SPECIALITY
    else:
        print_filter_info(update, context, callback=False)
        return STEP_FILTER_MAIN

filter_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(filter_start, pattern='^' + 'Найти сотрудника' + '$'),
    ],
    states={
        STEP_WRITE_SPECIALITY: [CallbackQueryHandler(write_speciality)],
        STEP_FILTER_SPECIALITY: [CallbackQueryHandler(filter_speciality)],
        STEP_FILTER_SPECIALISATION: [CallbackQueryHandler(filter_specialisation)],
        STEP_FILTER_SCHEDULE: [CallbackQueryHandler(filter_schedule)],
        STEP_FILTER_LOCATION: [MessageHandler(Filters.text & (~ Filters.command), filter_location)],
        STEP_FILTER_SALARY: [CallbackQueryHandler(filter_salary)],
        STEP_FILTER_AGE: [MessageHandler(Filters.text & (~ Filters.command), filter_age)],
        STEP_FILTER_EDUCATION: [CallbackQueryHandler(filter_education)],
        STEP_FILTER_EXPERIENCE: [CallbackQueryHandler(filter_experience)],
        STEP_FILTER_PHOTO: [CallbackQueryHandler(filter_photo)],
        STEP_SHOW_CV: [
            CallbackQueryHandler(show_cv, pattern=show_cv_patterns),
            CommandHandler('photo', show_photo),
            payment_conv_handler
        ],
        STEP_FILTER_MAIN: [
            CallbackQueryHandler(manage_filter_button, pattern=filter_patterns),
            CallbackQueryHandler(show_cv_first, pattern='^' + 'Показать анкеты' + '$'),
        ],
    },
    fallbacks=[
        MessageHandler(Filters.text & (~ Filters.command) | Filters.photo | Filters.video, filter_fallback),
        CallbackQueryHandler(end_describing_filter, pattern='^' + str(STEP_FILTER_END) + '$'),
    ],
    allow_reentry=True,
    per_chat=False
)
