from typing import Text

import os
from telegram import ParseMode
from bot_project_new.utils import (
    is_human_and_sfw,
    update_user_location,
    make_station_numbers_set,
    make_photo_path,
    print_location,
    firsttime_user,
    get_sepcialisation,
)
from DbFolder.db_file import DBase
from handlers import start_keyboard
from telegram.ext import (
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from cv_keyboards import (
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
    END
)


dbase = DBase()

def print_cv_info(update, context, markup, callback=True):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if firsttime_user(update.effective_user.id):
        dbase.db_client.users.update_one({'_id': user['_id']}, {'$set': {'first_time': False}})
    if user['cv']['speciality'] == 'Врач':
        specialisation_text = f'''\n  <b>Специализация:</b> {get_sepcialisation(tg_id)}'''
        education_text = ''
    else:
        specialisation_text = ''
        education_text = (
            f'''\n  <b>Образование:</b> {user['cv']['education']
            if user['cv'].get('education')
            else 'Значение не установлено'}'''
        )
    text = f'''
<em>Желаемая вакансия:</em>
  <b>Специальность:</b> {user['cv']['speciality']
          if user['cv'].get('speciality')
          else 'Значение не установлено'}{specialisation_text}
  <b>График работы:</b> {user['cv']['schedule']
          if user['cv'].get('schedule')
          else 'Значение не установлено'}
  <b>Минимальная оплата труда:</b> {user['cv']['salary']
          if user['cv'].get('salary')
          else 'Значение не установлено'}
  <b>Предпочитительное место работы:</b>\n{print_location(tg_id)}
<em>Ваши данные:</em>
  <b>ФИО:</b> {user['cv']['name']
          if user['cv'].get('name')
          else 'Значение не установлено'}
  <b>Возраст:</b> {user['cv']['age']
          if user['cv'].get('age')
          else 'Значение не установлено'}{education_text}
  <b>Опыт:</b> {user['cv']['experience']
          if user['cv'].get('experience')
          else 'Значение не установлено'}
  <b>Фото:</b> {'Фото добавлено'
          if user['cv'].get('photo')
          else 'Фото не добавлялось'}

<b>Статус анкеты:</b> {'Анкета видна в поиске'
          if user['cv']['show_cv']
          else 'Анкета удалена из поиска'}
'''
    reply_markup = markup
    if callback:
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


speciality_pattern = ('^Врач$|^Мед работник$|^Ассистент$')
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
    f'^{STEP_PHOTO}$'
)
def get_step_text(key, tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if key == STEP_NAME:
        text = f'''
{show_step_num(tg_id, key)}
<b>ФИО:</b>
Напишите Ваше имя, отчество и фамилию.
<b>Пример:</b> "Иван Иванович Иванов".
'''
        keyboard = None
    elif key == STEP_AGE:
        text = f'''
{show_step_num(tg_id, key)}
<b>Возраст:</b>
Напишите сколько Вам полных лет
'''
        keyboard = None
    elif key == STEP_LOCATION:
        text = f'''
{show_step_num(tg_id, key)}
<b>Местоположение:</b>
Где удобно работать? (Вы можете вводить через запятую необходимые станции метро, линии метро, районы, округа).
<b>Пример:</b> "Речной вокзал, САО".
'''
        keyboard = None
    elif key == STEP_SPECIALITY:
        text = f'''
{show_step_num(tg_id, key)}
<b>Специальность:</b>
Пожалуйста, выберите Вашу специальность.
'''
        keyboard = speciality_keyboard()
    elif key == STEP_SPECIALISATION:
        text = f'''
{show_step_num(tg_id, key)}
<b>Выберите специализацию:</b>
(можно выбрать один или несколько пунктов)
<b>Ваш текущий выбор:</b> {get_sepcialisation(tg_id)}
'''
        keyboard = specialisation_keyboard(tg_id)
    elif key == STEP_SCHEDULE:
        text = f'''
{show_step_num(tg_id, key)}
<b>График:</b>
Выберите предпочтительный график работы.
'''
        keyboard = schedule_keyboard(tg_id)
    elif key == STEP_SALARY:
        if user['cv']['speciality'] != 'Врач':
            text = f'''
{show_step_num(tg_id, key)}
<b>Зарплата:</b>
Выберите минимальную оплату за смену(полдня, 6 - 8 часов).
'''
        else:
            text = f'''
{show_step_num(tg_id, key)}
<b>Зарплата:</b>
Выберите минимальную зароботную плата за месяц.
'''
        keyboard = salary_keyboard(tg_id)
    elif key == STEP_EDUCATION:
        text = f'''
{show_step_num(tg_id, key)}
<b>Образование:</b>
Выберите Ваше образование.
'''
        keyboard = education_keyboard(tg_id)
    elif key == STEP_EXPERIENCE:
        text = f'''
{show_step_num(tg_id, key)}
<b>Опыт:</b>
Выберите Ваш опыт работы.
'''
        keyboard = experience_keyboard(tg_id)
    elif key == STEP_PHOTO:
        text = f'''
{show_step_num(tg_id, key)}
<b>Фото:</b>
Прикрепите Ваше фото, это не обязательно, но сильно повышает шансы найти работу:)
'''
        keyboard = None
    else:
        text = 'Вы завершили заполнение анкеты'
        keyboard = None
    return text, keyboard


def show_step_num(tg_id, key):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if firsttime_user(tg_id):
        max_step = 10
        if key == STEP_SPECIALITY:
            current_step_num = 1
            text_prev_step = ''
        elif key == STEP_SPECIALISATION:
            current_step_num = 2
            text_prev_step = f"<b>Выбранная Вами специальность:</b> {user['cv']['speciality']}"
        elif key == STEP_SCHEDULE:
            current_step_num = 3
            if user['cv']['speciality'] == 'Врач':
                text_prev_step = f"<b>Выбранная Вами специализация:</b> {get_sepcialisation(tg_id)}"
            else:
                text_prev_step = f"<b>Выбранная Вами специальность:</b> {user['cv']['speciality']}"
        elif key == STEP_LOCATION:
            current_step_num = 4
            text_prev_step = f"<b>Выбранный Вами график:</b> {user['cv']['schedule']}"
        elif key == STEP_SALARY:
            current_step_num = 5
            text_prev_step = f"<b>Предпочитительное место работы:</b>\n{print_location(tg_id)}"
        elif key == STEP_NAME:
            current_step_num = 6
            text_prev_step = f"<b>Выбранная Вами минимальная зарплата:</b> {user['cv']['salary']}"
        elif key == STEP_AGE:
            current_step_num = 7
            text_prev_step = f"<b>Введенные Вами ФИО:</b> {user['cv']['name']}"
        elif key == STEP_EDUCATION:
            current_step_num = 8
            text_prev_step = f"<b>Введенный Вами возраст:</b> {user['cv']['age']}"
        elif key == STEP_EXPERIENCE:
            current_step_num = 9
            if user['cv']['speciality'] == 'Врач':
                text_prev_step = f"<b>Введенные Вами ФИО:</b> {user['cv']['name']}"
            else:
                text_prev_step = f"<b>Выбранное Вами образование:</b> {user['cv']['education']}"
        else:
            current_step_num = 10
            text_prev_step = f"<b>Выбранный вами опыт:</b> {user['cv']['experience']}"
        text = f'''
<b>Шаг:</b> {current_step_num} из {max_step}
{text_prev_step}
'''
    else:
        return ''
    return text


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
    if firsttime_user(update.effective_user.id):
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
    dbase.save_cv(tg_id, 'speciality', user_speciality)
    if firsttime_user(tg_id):
        if user_speciality == 'Врач':
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
        if firsttime_user(tg_id):
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
        dbase.update_specialisation(tg_id, user_specialisation)
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
        if user['cv']['speciality'] == 'Врач':
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
    if firsttime_user(tg_id):
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
        user = dbase.db_client.users.find_one({'tg_id': tg_id})
        if firsttime_user(tg_id):
            text = get_step_text(STEP_SALARY, tg_id)[0]
            update.message.reply_text(
                text=text,
                reply_markup=salary_keyboard(tg_id),
                parse_mode=ParseMode.HTML
            )
            dbase.save_cv(tg_id, 'current_step', 'STEP_SALARY')
            return STEP_SALARY
        else:
            print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
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
    user_salary = update.callback_query.data
    dbase.save_cv(tg_id, 'salary', user_salary)
    if firsttime_user(tg_id):
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
    if firsttime_user(update.effective_user.id):
        text = get_step_text(STEP_AGE, tg_id)[0]
        update.message.reply_text(
            text=text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )
        dbase.save_cv(tg_id, 'current_step', 'STEP_AGE')
        return STEP_AGE
    else:
        print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
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
            if firsttime_user(update.effective_user.id):
                user = dbase.db_client.users.find_one({'tg_id': tg_id})
                user_speciality = user['cv']['speciality']
                if user_speciality == 'Врач':
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
                print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
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
    user_education = update.callback_query.data
    dbase.save_cv(tg_id, 'education', user_education)
    if firsttime_user(tg_id):
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
        if user['cv']['speciality'] == 'Врач':
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
    user_experience = update.callback_query.data
    if user_experience == 'Звездный Ассистент':
        user_experience = 'выпускник курса "Звездный Ассистент"'
    dbase.save_cv(tg_id, 'experience', user_experience)
    if firsttime_user(tg_id):
        text = get_step_text(STEP_PHOTO, tg_id)[0]
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=photo_pass_keyboard(),
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
        dbase.save_cv(tg_id, 'photo', photo_path_list)
        print_cv_info(update, context, cv_main_keyboard(update, context), callback=False)
        dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
        return STEP_UPDATE_CV
    else:
        update.message.reply_text('Фото не подхоидт, выберите другое', reply_markup=photo_pass_keyboard())
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
    user_photo = None
    dbase.save_cv(tg_id, 'photo', user_photo)
    print_cv_info(update, context, cv_main_keyboard(update, context))
    dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
    return STEP_UPDATE_CV


# Функция дает ответ если пользователь в анкете не выбрал поле
def cv_fallback(update, context):
    tg_id = update.effective_user.id
    text = 'Заполнение анкеты'
    update.message.reply_text(
        text=text,
        reply_markup=cv_main_keyboard(update, context),
        parse_mode=ParseMode.HTML
    )
    dbase.save_cv(tg_id, 'current_step', 'STEP_UPDATE_CV')
    return STEP_UPDATE_CV


# Завершение анкеты выход из ConversationHandler
def end_describing(update, context):
    text = 'Вы завершили редактирование анкеты, выберите пункт меню.'
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=start_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

cv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(cv_start, pattern='^' + 'Заполнить анкету' + '$')
    ],
    states={
        STEP_SPECIALITY: [CallbackQueryHandler(choose_speciality)],
        STEP_SPECIALISATION: [CallbackQueryHandler(choose_specialisation)],
        STEP_SCHEDULE: [CallbackQueryHandler(choose_schedule)],
        STEP_LOCATION: [
            MessageHandler(Filters.text, choose_location),
            CallbackQueryHandler(location_back),
        ],
        STEP_SALARY: [CallbackQueryHandler(choose_salary)],
        STEP_NAME: [
            MessageHandler(Filters.text, choose_name),
            CallbackQueryHandler(name_back),
        ],
        STEP_AGE: [
            MessageHandler(Filters.text, choose_age),
            CallbackQueryHandler(age_back),
        ],
        STEP_EDUCATION: [CallbackQueryHandler(choose_education)],
        STEP_EXPERIENCE: [CallbackQueryHandler(choose_experience)],
        STEP_PHOTO: [
            MessageHandler(Filters.photo, check_user_photo),
            CallbackQueryHandler(photo_pass, pattern='^back_cv$|^пропустить_фото$'),
        ],
        STEP_UPDATE_CV: [
            CallbackQueryHandler(manage_choosen_button, pattern=input_patterns),
            CallbackQueryHandler(cv_move_other, pattern='^' + str(STEP_OTHER) + '$'),
            CallbackQueryHandler(not_show_cv, pattern='^' + str(STEP_DELETE) + '$'),
            CallbackQueryHandler(cv_start, pattern='^' + str(STEP_BACK) + '$')
        ],
    },
    fallbacks=[
        MessageHandler(Filters.text | Filters.photo | Filters.video, cv_fallback),
        CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$')
    ]
)
