from typing import Text

import os
import base64
from telegram import ParseMode
from utils import (
    is_human_and_sfw,
    update_user_location,
    make_station_numbers_set,
    make_photo_path,
    print_location,
    firsttime_user,
    print_specialisation,
    clear_photo
)
from DbFolder.db_file import DBase
from handlers import start_keyboard
from telegram.ext import (
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
)
from handlers import start

from keyboards import (
    cv_main_keyboard,
    cv_other_keyboard,
    speciality_keyboard,
    specialisation_keyboard,
    schedule_keyboard,
    salary_keyboard,
    education_keyboard,
    experience_keyboard,
    photo_pass_keyboard,
    back_keyboard,
    contact_keyboard,
    STEP_NAME,
    STEP_AGE,
    STEP_EXPERIENCE,
    STEP_LOCATION,
    STEP_UPDATE_CV,
    STEP_PHOTO,
    STEP_SPECIALITY,
    STEP_SPECIALISATION,
    STEP_OTHER,
    STEP_DELETE,
    STEP_SCHEDULE,
    STEP_SALARY,
    STEP_EDUCATION,
    STEP_BACK,
    STEP_CONTACT,
    STEP_CV_END
)


dbase = DBase()

def print_cv_info(update, context, markup, callback=True):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if firsttime_user(update.effective_user.id, 'cv'):
        dbase.db_client.users.update_one({'_id': user['_id']}, {'$set': {'cv.first_time': False}})
        firsttime_text = '''
Теперь Ваша анкета видна для работодателей, вероятно, скоро Вам позвонят! 🥳
А Вы тем временем можете поискать вакансии, нажав кнопку ниже.

Если Вы не хотите, чтоб Ваша анкета была видна работодателям, нажмите <b>«убрать анкету из поиска»</b>.
'''
    else:
        firsttime_text = ''
    if user['cv']['speciality'] == 'Стоматолог':
        specialisation_text = f'''\n<b>Специализация:</b> {print_specialisation(tg_id, 'cv')}'''
        education_text = ''
    else:
        specialisation_text = ''
        education_text = (
            f'''\n<b>Образование:</b> {user['cv']['education']
            if user['cv'].get('education')
            else 'Значение не установлено'}'''
        )
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    text = f'''
Давайте посмотрим на Вашу анкету! 😌
В таком виде ее увидит работодатель.

<b>ФИО:</b> {user['cv']['name']
        if user['cv'].get('name')
        else 'Значение не установлено'}
<b>Возраст:</b> {user['cv']['age']
        if user['cv'].get('age')
        else 'Значение не установлено'}{education_text}
<b>Опыт:</b> {user['cv']['experience']
        if user['cv'].get('experience')
        else 'Значение не установлено'}
<b>Специальность:</b> {user['cv']['speciality']
        if user['cv'].get('speciality')
        else 'Значение не установлено'}{specialisation_text}
<b>График работы:</b> {user['cv']['schedule']
        if user['cv'].get('schedule')
        else 'Значение не установлено'}
<b>Минимальная оплата труда:</b> {user['cv']['salary']
        if user['cv'].get('salary')
        else 'Значение не установлено'}
<b>Предпочитительное место работы:</b>\n{print_location(tg_id, 'cv')}
<b>Номер телефона:</b> {user['cv']['phone']
        if user['cv'].get('phone')
        else 'Значение не установлено'}
<b>Фото:</b> {'Чтобы посмотреть фотографию, нажмите /photo'
        if user['cv'].get('photo')
        else 'Фото не добавлялось'}

<b>Статус анкеты:</b> {'Анкета видна в поиске'
          if user['cv']['show_cv']
          else 'Анкета удалена из поиска'}
{firsttime_text}
'''
    reply_markup = markup
    if callback:
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


input_patterns = (
    f'^{STEP_AGE}$|'
    f'^{STEP_LOCATION}$|'
    f'^{STEP_NAME}$|'
    f'^{STEP_SPECIALITY}$|'
    f'^{STEP_SPECIALISATION}$|'
    f'^{STEP_SCHEDULE}$|'
    f'^{STEP_SALARY}$|'
    f'^{STEP_EXPERIENCE}$|'
    f'^{STEP_EDUCATION}$|'
    f'^{STEP_CONTACT}$|'
    f'^{STEP_PHOTO}$'
)

def get_step_text(key, tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if key == STEP_NAME:
        text = f'''
{show_step_num(tg_id, key)}
Напишите Ваше <b>имя, отчество и фамилию</b>.
<b>Пример:</b> "Иван Иванович Иванов".
'''
        keyboard = None
    elif key == STEP_AGE:
        text = f'''
{show_step_num(tg_id, key)}
Сколько Вам <b>лет</b>?
'''
        keyboard = None
    elif key == STEP_LOCATION:
        text = f'''
{show_step_num(tg_id, key)}
<b>Где удобно работать?</b> (Вы можете вводить через запятую необходимые станции метро, линии метро, районы, округа).
<b>Пример:</b> "Речной вокзал, САО".
'''
        keyboard = None
    elif key == STEP_SPECIALITY:
        text = f'''
{show_step_num(tg_id, key)}
Выберите вашу <b>специальность</b>.
'''
        keyboard = speciality_keyboard()
    elif key == STEP_SPECIALISATION:
        text = f'''
{show_step_num(tg_id, key)}
Выберите <b>специализацию</b>:
(можно выбрать один или несколько пунктов)
<b>Ваш текущий выбор:</b> {print_specialisation(tg_id, 'cv')}
'''
        keyboard = specialisation_keyboard(tg_id)
    elif key == STEP_SCHEDULE:
        text = f'''
{show_step_num(tg_id, key)}
Выберите предпочтительный <b>график работы</b>.
'''
        keyboard = schedule_keyboard(tg_id)
    elif key == STEP_SALARY:
        if user['cv']['speciality'] != 'Стоматолог':
            text = f'''
{show_step_num(tg_id, key)}
Выберите <b>минимальную оплату</b> за смену(полдня, 6 - 8 часов).
'''
        else:
            text = f'''
{show_step_num(tg_id, key)}
Выберите минимальную <b>заработную плату</b> за месяц.
'''
        keyboard = salary_keyboard(tg_id)
    elif key == STEP_EDUCATION:
        text = f'''
{show_step_num(tg_id, key)}
Выберите Ваше <b>образование</b>.
'''
        keyboard = education_keyboard(tg_id)
    elif key == STEP_EXPERIENCE:
        text = f'''
{show_step_num(tg_id, key)}
Выберите Ваш <b>опыт работы</b>.
'''
        keyboard = experience_keyboard(tg_id)
    elif key == STEP_CONTACT:
        text = f'''
{show_step_num(tg_id, key)}
Поделитесь контактным <b>номером телефона</b>, чтобы работодатель мог связаться с Вами. 
'''
        keyboard = contact_keyboard()
    elif key == STEP_PHOTO:
        text = f'''
{show_step_num(tg_id, key)}
Прикрепите Ваше <b>фото</b>.
Для этого нажмите на скрепку (эмоджи скрепки) в левом нижнем углу.
Это не обязательно, но сильно повышает Ваши шансы найти работу :)
'''
        keyboard = None
    else:
        text = 'Вы завершили заполнение анкеты'
        keyboard = None
    return text, keyboard


def show_step_num(tg_id, key):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    step_num_dict = {
                STEP_SPECIALITY: [1, 1],
                STEP_SPECIALISATION: [2, 2],
                STEP_SCHEDULE: [3, 2],
                STEP_LOCATION: [4, 3],
                STEP_SALARY: [5, 4],
                STEP_NAME: [6, 5],
                STEP_AGE: [7, 6],
                STEP_EDUCATION: [7, 7],
                STEP_EXPERIENCE: [8, 8],
                STEP_PHOTO: [9, 9],
                STEP_CONTACT: [10, 10],
            }
    if user['cv'].get('speciality'):
        if user['cv']['speciality'] == 'Стоматолог':
            current_step_num = step_num_dict[key][0]
        else:
            current_step_num = step_num_dict[key][1]
    else:
        current_step_num = 1
    text_prev_step = get_text_prev(tg_id, key)
    if firsttime_user(tg_id, 'cv'):
        max_step = 10
        text = f'''
<b>Шаг:</b> {current_step_num} из {max_step}
{text_prev_step}
'''
    else:
        return ''
    return text


def get_text_prev(tg_id, key):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if key == STEP_SPECIALITY:
        text_prev_step = '<b>Для выхода из заполнения анкеты, Вы в любой момент можете ввести команду /stop</b>'
    elif key == STEP_SPECIALISATION:
        text_prev_step = f"Выбранная Вами специальность: {user['cv']['speciality']}"
    elif key == STEP_SCHEDULE:
        if user['cv']['speciality'] == 'Стоматолог':
            text_prev_step = f"Выбранная Вами специализация: {print_specialisation(tg_id, 'cv')}"
        else:
            text_prev_step = f"Выбранная Вами специальность: {user['cv']['speciality']}"
    elif key == STEP_LOCATION:
        text_prev_step = f"Выбранный Вами график: {user['cv']['schedule']}"
    elif key == STEP_SALARY:
        text_prev_step = f"Предпочитительное место работы:\n{print_location(tg_id, 'cv')}"
    elif key == STEP_NAME:
        text_prev_step = f"Выбранная Вами минимальная зарплата: {user['cv']['salary']}"
    elif key == STEP_AGE:
        text_prev_step = f"Введенные Вами ФИО: {user['cv']['name']}"
    elif key == STEP_EDUCATION:
        text_prev_step = f"Введенный Вами возраст: {user['cv']['age']}"
    elif key == STEP_EXPERIENCE:
        if user['cv']['speciality'] == 'Стоматолог':
            text_prev_step = f"Введенные Вами ФИО: {user['cv']['name']}"
        else:
            text_prev_step = f"Выбранное Вами образование: {user['cv']['education']}"
    elif key == STEP_PHOTO:
        text_prev_step = f"Выбранный вами опыт: {user['cv']['experience']}"
    elif key == STEP_CONTACT:
        text_prev_step = ('Фото добавлено' if user['cv'].get('photo') else 'Фото не добавлялось')
    return text_prev_step

def manage_choosen_button(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    context.user_data['CURRENT_FEATURE'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE']
    text = get_step_text(user_data_key, tg_id)[0]
    reply_markup = get_step_text(user_data_key, tg_id)[1]
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return user_data_key


def cv_move_other(update, context):
    tg_id = update.effective_user.id
    update.callback_query.answer()
    print_cv_info(update, context, cv_other_keyboard(update, context))
    dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
    return STEP_UPDATE_CV


# Обработчик кнопки заполнить анкету
def cv_start(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if firsttime_user(update.effective_user.id, 'cv'):
        text = get_step_text(STEP_SPECIALITY, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=speciality_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALITY')
        return STEP_SPECIALITY
    else:
        print_cv_info(update, context, cv_main_keyboard(update, context))
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV

def not_show_cv(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['show_cv']:
        dbase.save_cv(tg_id, 'show_cv', False)
    else:
        dbase.save_cv(tg_id, 'show_cv', True)
    print_cv_info(update, context, cv_main_keyboard(update, context))
    dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
    return STEP_UPDATE_CV


def choose_speciality(update, context):
    update.callback_query.answer()
    user_speciality = update.callback_query.data
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv'].get('speciality') != user_speciality:
        dbase.db_client.users.update_one({'_id': user['_id']}, {'$set': {'cv.first_time': True}})
        dbase.clear_cv(tg_id)
    dbase.save_cv(tg_id, 'speciality', user_speciality)
    if firsttime_user(tg_id, 'cv'):
        if user_speciality == 'Стоматолог':
            text = get_step_text(STEP_SPECIALISATION, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=specialisation_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALISATION')
            return STEP_SPECIALISATION
        else:
            text = get_step_text(STEP_SCHEDULE, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=schedule_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SCHEDULE')
            return STEP_SCHEDULE
    else:
        print_cv_info(update, context, cv_other_keyboard(update, context))
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV


def choose_specialisation(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if update.callback_query.data == 'back_cv':
        text = get_step_text(STEP_SPECIALITY, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=speciality_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALITY')
        return STEP_SPECIALITY
    elif update.callback_query.data == 'end_specialisation':
        if firsttime_user(tg_id, 'cv'):
            text = get_step_text(STEP_SCHEDULE, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=schedule_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SCHEDULE')
            return STEP_SCHEDULE
        else:
            print_cv_info(update, context, cv_other_keyboard(update, context))
            dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
            return STEP_UPDATE_CV
    else:
        user_specialisation = update.callback_query.data
        dbase.update_specialisation(tg_id, user_specialisation, 'cv')
        user = dbase.db_client.users.find_one({'tg_id': tg_id})
        text = get_step_text(STEP_SPECIALISATION, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=specialisation_keyboard(tg_id),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALISATION')
        return STEP_SPECIALISATION


def choose_schedule(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if update.callback_query.data == 'back_cv':
        if user['cv']['speciality'] == 'Стоматолог':
            text = get_step_text(STEP_SPECIALISATION, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=specialisation_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALISATION')
            return STEP_SPECIALISATION
        else:
            text = get_step_text(STEP_SPECIALITY, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=speciality_keyboard(),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALITY')
            return STEP_SPECIALITY
    user_schedule = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_cv(tg_id, 'schedule', user_schedule)
    if firsttime_user(tg_id, 'cv'):
        text = get_step_text(STEP_LOCATION, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_LOCATION')
        return STEP_LOCATION
    else:
        print_cv_info(update, context, cv_other_keyboard(update, context))
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV

def choose_location(update, context):
    user_location = update.message.text
    tg_id = update.effective_user.id
    if update_user_location(user_location):
        user_location = update_user_location(user_location)
        station_numbers = make_station_numbers_set(user_location)
        dbase.save_cv(tg_id, 'location', user_location)
        dbase.save_cv(tg_id, 'station_numbers', station_numbers)
        if firsttime_user(tg_id, 'cv'):
            text = get_step_text(STEP_SALARY, tg_id)[0]
            update.message.reply_text(
                text=text,
                reply_markup=salary_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SALARY')
            return STEP_SALARY
        else:
            print_cv_info(update, context, cv_other_keyboard(update, context), callback=False)
            dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
            return STEP_UPDATE_CV
    else:
        update.message.reply_text('Один или несколько объектов не распознаны, попробуйте еще раз')
        dbase.save_cv(tg_id, 'current_step', 'STEP_LOCATION')
        return STEP_LOCATION

def location_back(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    text = get_step_text(STEP_SCHEDULE, tg_id)[0]
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=schedule_keyboard(tg_id),
        parse_mode=ParseMode.HTML
    )
    dbase.save_cv(tg_id, 'current_step', 'STEP_SCHEDULE')
    return STEP_SCHEDULE


def choose_salary(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if update.callback_query.data == 'back_cv':
        text = get_step_text(STEP_LOCATION, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_LOCATION')
        return STEP_LOCATION
    user_data = update.callback_query.data
    user_salary = user_data.split('/')[0]
    user_salary_key = user_data.split('/')[1]
    dbase.save_cv(tg_id, 'salary', user_salary)
    dbase.save_cv(tg_id, 'salary_key', user_salary_key)
    if firsttime_user(tg_id, 'cv'):
        text = get_step_text(STEP_NAME, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_NAME')
        return STEP_NAME
    else:
        print_cv_info(update, context, cv_other_keyboard(update, context))
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV

def choose_name(update, context):
    user_name = update.message.text
    tg_id = update.effective_user.id
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста, введите ФИО(не менее 2-х слов)')
        dbase.save_cv(tg_id, 'current_step', 'STEP_NAME')
        return STEP_NAME
    else:
        dbase.save_cv(tg_id, 'name', user_name)
    if firsttime_user(update.effective_user.id, 'cv'):
        text = get_step_text(STEP_AGE, tg_id)[0]
        update.message.reply_text(
            text=text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_AGE')
        return STEP_AGE
    else:
        print_cv_info(update, context, cv_other_keyboard(update, context), callback=False)
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV

def name_back(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    text = get_step_text(STEP_SALARY, tg_id)[0]
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=salary_keyboard(tg_id),
        parse_mode=ParseMode.HTML
    )
    dbase.save_cv(tg_id, 'current_step', 'STEP_SALARY')
    return STEP_SALARY


def choose_age(update, context):
    user_age = update.message.text
    tg_id = update.effective_user.id
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            dbase.save_cv(tg_id, 'age', user_age)
            if firsttime_user(update.effective_user.id, 'cv'):
                user = dbase.db_client.users.find_one({'tg_id': tg_id})
                user_speciality = user['cv']['speciality']
                if user_speciality == 'Стоматолог':
                    text = get_step_text(STEP_EXPERIENCE, tg_id)[0]
                    update.message.reply_text(
                        text=text,
                        reply_markup=experience_keyboard(tg_id),
                        parse_mode=ParseMode.HTML
                    )
                    dbase.save_cv(tg_id, 'current_step', 'STEP_EXPERIENCE')
                    return STEP_EXPERIENCE
                else:
                    text = get_step_text(STEP_EDUCATION, tg_id)[0]
                    update.message.reply_text(
                        text=text,
                        reply_markup=education_keyboard(tg_id),
                        parse_mode=ParseMode.HTML
                    )
                    dbase.save_cv(tg_id, 'current_step', 'STEP_EDUCATION')
                    return STEP_EDUCATION
            else:
                print_cv_info(update, context, cv_other_keyboard(update, context), callback=False)
                dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
                return STEP_UPDATE_CV
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст')
            dbase.save_cv(tg_id, 'current_step', 'STEP_AGE')
            return STEP_AGE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст')
        dbase.save_cv(tg_id, 'current_step', 'STEP_AGE')
        return STEP_AGE

def age_back(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    text = get_step_text(STEP_NAME, tg_id)[0]
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=back_keyboard(),
        parse_mode=ParseMode.HTML
    )
    dbase.save_cv(tg_id, 'current_step', 'STEP_NAME')
    return STEP_NAME


def choose_education(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if update.callback_query.data == 'back_cv':
        text = get_step_text(STEP_AGE, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_AGE')
        return STEP_AGE
    user_data = update.callback_query.data
    user_education = user_data.split('/')[0]
    user_education_key = user_data.split('/')[1]
    if user_education == 'среднее мед., неоконченное':
        user_education = 'среднее медицинское, неоконченное'
    dbase.save_cv(tg_id, 'education', user_education)
    dbase.save_cv(tg_id, 'education_key', user_education_key)
    if firsttime_user(tg_id, 'cv'):
        text = get_step_text(STEP_EXPERIENCE, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=experience_keyboard(tg_id),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_EXPERIENCE')
        return STEP_EXPERIENCE
    else:
        print_cv_info(update, context, cv_other_keyboard(update, context))
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV

def choose_experience(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if update.callback_query.data == 'back_cv':
        if user['cv']['speciality'] == 'Стоматолог':
            text = get_step_text(STEP_AGE, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=back_keyboard(),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_AGE')
            return STEP_AGE
        else:
            text = get_step_text(STEP_EDUCATION, tg_id)[0]
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=education_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_EDUCATION')
            return STEP_EDUCATION
    user_data = update.callback_query.data
    user_experience = user_data.split('/')[0]
    user_experience_key = user_data.split('/')[1]
    if user_experience == 'Звездный Ассистент':
        user_experience = 'выпускник курса "Звездный Ассистент"'
    dbase.save_cv(tg_id, 'experience', user_experience)
    dbase.save_cv(tg_id, 'experience_key', user_experience_key)
    if firsttime_user(tg_id, 'cv'):
        text = get_step_text(STEP_PHOTO, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=photo_pass_keyboard(tg_id),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_PHOTO')
        return STEP_PHOTO
    else:
        print_cv_info(update, context, cv_other_keyboard(update, context))
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV


def check_user_photo(update, context):
    tg_id = update.effective_user.id
    update.message.reply_text('Обрабатываю фотографию')
    photo = update.message.photo[-1]
    user_photo = context.bot.getFile(photo.file_id)
    photo_path = make_photo_path(user_photo, update, context)
    if is_human_and_sfw(photo_path):
        update.message.reply_text('Фото сохранено')
        with open(photo_path, "rb") as imageFile:
            image_str = base64.b64encode(imageFile.read())
        clear_photo(tg_id)
        dbase.save_cv(tg_id, 'photo', image_str)
        if firsttime_user(tg_id, 'cv'):
            text = get_step_text(STEP_CONTACT, tg_id)[0]
            update.message.reply_text(
                text=text,
                reply_markup=contact_keyboard(),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_CONTACT')
            return STEP_CONTACT
        else:
            print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
            dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
            return STEP_UPDATE_CV
    else:
        clear_photo(tg_id)
        update.message.reply_text('Фото не подхоидт, выберите другое', reply_markup=photo_pass_keyboard(tg_id))
        dbase.save_cv(tg_id, 'current_step', 'STEP_PHOTO')
        return STEP_PHOTO


def photo_pass(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    if update.callback_query.data == 'back_cv':
        text = get_step_text(STEP_EXPERIENCE, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=experience_keyboard(tg_id),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_EXPERIENCE')
        return STEP_EXPERIENCE
    user_photo = False
    dbase.save_cv(tg_id, 'photo', user_photo)
    chat_id = update.callback_query.message.chat.id
    text = get_step_text(STEP_CONTACT, tg_id)[0]
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=contact_keyboard(),
        parse_mode=ParseMode.HTML
    )
    dbase.save_cv(tg_id, 'current_step', 'STEP_CONTACT')
    return STEP_CONTACT

def get_contact(update, context):
    user_phone = update.message.contact.phone_number
    tg_id = update.effective_user.id
    dbase.save_cv(tg_id, 'phone', user_phone)
    dbase.save_cv(tg_id, 'show_cv', True)
    print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
    dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
    return STEP_UPDATE_CV

def get_contact_fail(update, context):
    tg_id = update.effective_user.id
    text = 'Чтобы поделиться совим номером телефона, пожалуйста нажмите кнопку на клавиатуре'
    update.message.reply_text(
        text=text,
        reply_markup=contact_keyboard(),
        parse_mode=ParseMode.HTML
    )
    dbase.save_cv(tg_id, 'current_step', 'STEP_CONTACT')
    return STEP_CONTACT

def show_photo(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv'].get('photo'):
        photo_str = user['cv'].get('photo')
        os.makedirs(f'downloads/{tg_id}', exist_ok=True)
        photo_path = os.path.join('downloads', f'{tg_id}', 'user_photo.jpg')
        with open(photo_path, "wb") as fimage:
            fimage.write(base64.decodebytes(photo_str))
        chat_id = update.effective_chat.id
        context.bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))
        clear_photo(tg_id)
    print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
    return STEP_UPDATE_CV


def cancel_conversation(update, context):
    reply_markup = start_keyboard()
    text = 'Вы прервали редактирование анкеты, выберите пункт меню.'
    update.message.reply_text(text=text, reply_markup=reply_markup)
    return ConversationHandler.END


# Завершение анкеты выход из ConversationHandler
def end_describing_cv(update, context):
    text = 'Вы завершили редактирование анкеты, выберите пункт меню.'
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=start_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


def cv_fallback(update, context):
    tg_id = update.effective_user.id
    if firsttime_user(tg_id, 'cv'):
        text = get_step_text(STEP_SPECIALITY, tg_id)[0]
        update.message.reply_text(
            text=text,
            reply_markup=speciality_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_SPECIALITY')
        return STEP_SPECIALITY
    else:
        print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV


cv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(cv_start, pattern='^' + 'Заполнить анкету' + '$')
    ],
    states={
        STEP_SPECIALITY: [CallbackQueryHandler(choose_speciality)],
        STEP_SPECIALISATION: [CallbackQueryHandler(choose_specialisation)],
        STEP_SCHEDULE: [CallbackQueryHandler(choose_schedule)],
        STEP_LOCATION: [
            MessageHandler(Filters.text & (~ Filters.command), choose_location),
            CallbackQueryHandler(location_back),
        ],
        STEP_SALARY: [CallbackQueryHandler(choose_salary)],
        STEP_NAME: [
            MessageHandler(Filters.text & (~ Filters.command), choose_name),
            CallbackQueryHandler(name_back),
        ],
        STEP_AGE: [
            MessageHandler(Filters.text & (~ Filters.command), choose_age),
            CallbackQueryHandler(age_back),
        ],
        STEP_EDUCATION: [CallbackQueryHandler(choose_education)],
        STEP_EXPERIENCE: [CallbackQueryHandler(choose_experience)],
        STEP_PHOTO: [
            MessageHandler(Filters.photo, check_user_photo),
            CallbackQueryHandler(photo_pass, pattern='^back_cv$|^пропустить_фото$'),
        ],
        STEP_CONTACT: [
            MessageHandler(Filters.contact, get_contact),
            MessageHandler(Filters.text & (~ Filters.command), get_contact_fail),
        ],
        STEP_UPDATE_CV: [
            CallbackQueryHandler(manage_choosen_button, pattern=input_patterns),
            CallbackQueryHandler(cv_move_other, pattern='^' + str(STEP_OTHER) + '$'),
            CallbackQueryHandler(not_show_cv, pattern='^' + str(STEP_DELETE) + '$'),
            CallbackQueryHandler(cv_start, pattern='^' + str(STEP_BACK) + '$'),
            CommandHandler('photo', show_photo),
        ],
    },
    fallbacks=[
        MessageHandler(Filters.text & (~ Filters.command) | Filters.photo | Filters.video, cv_fallback),
        CallbackQueryHandler(end_describing_cv, pattern='^' + str(STEP_CV_END) + '$'),
        CommandHandler('stop', cancel_conversation),
    ],
    allow_reentry=True
)

