from typing import Text
import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from utils import firsttime_user
from emoji import emojize
from DbFolder.db_file import DBase
dbase = DBase()
(
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
    END
) = map(chr, range(16))

smile_speciality = emojize(':memo:', use_aliases=True)
smile_specialisation = emojize(':microscope:', use_aliases=True)
smile_education = emojize(':mortar_board:', use_aliases=True)
smile_expirience = emojize(':clock12:', use_aliases=True)
smile_shedule = emojize(':date:', use_aliases=True)
smile_salary = emojize(':dollar:', use_aliases=True)
smile_back = emojize(':arrow_left:', use_aliases=True)
smile_yes = emojize(':white_check_mark:', use_aliases=True)
smile_no = emojize(':white_medium_square:', use_aliases=True)
smile_name = emojize(':mens:', use_aliases=True)
smile_age = emojize(':hourglass_flowing_sand:', use_aliases=True)
smile_location = emojize(':earth_africa:', use_aliases=True)
smile_photo = emojize(':camera:', use_aliases=True)
smile_other = emojize(':capital_abcd:', use_aliases=True)
smile_rdy = emojize(':arrow_right:', use_aliases=True)
smile_1 = None  # emojize(':one:', use_aliases=True)
smile_2 = None  # emojize(':two:', use_aliases=True)
smile_3 = None  # emojize(':three:', use_aliases=True)
smile_4 = None  # emojize(':four:', use_aliases=True)
smile_5 = None  # emojize(':five:', use_aliases=True)
smile_pass = emojize(':arrow_right:', use_aliases=True)
smile_worker = emojize(':construction_worker:', use_aliases=True)
smile_write = emojize(':pencil2:', use_aliases=True)


def cv_main_keyboard(update, context):
    # основная клавиатура для анкеты
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['show_cv']:
        text = f'{smile_yes} Убрать анкету из поиска'
    else:
        text = f'{smile_no} Добавить анкету в поиск'
    cv_main_buttons = [
        [
            InlineKeyboardButton(text=f'{smile_write} Изменить анкету', callback_data=STEP_OTHER),
        ],
        [
            InlineKeyboardButton(text=text, callback_data=STEP_DELETE),
        ],
        [
            InlineKeyboardButton(text=f'{smile_rdy} Готово', callback_data=END),
        ]
    ]
    return InlineKeyboardMarkup(cv_main_buttons)


def cv_other_keyboard(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    cv_other_buttons = [
        [
            InlineKeyboardButton(text=f'{smile_speciality} Специальность', callback_data=STEP_SPECIALITY),
        ],
        [
            InlineKeyboardButton(text=f'{smile_specialisation} Специализация', callback_data=STEP_SPECIALISATION),
        ],
        [
            InlineKeyboardButton(text=f'{smile_education} Образование', callback_data=STEP_EDUCATION),
            InlineKeyboardButton(text=f'{smile_expirience} Опыт', callback_data=STEP_EXPERIENCE),
        ],
        [
            InlineKeyboardButton(text=f'{smile_name} ФИО', callback_data=STEP_NAME),
            InlineKeyboardButton(text=f'{smile_age} Возраст', callback_data=STEP_AGE),
        ],
        [
            InlineKeyboardButton(text=f'{smile_location} Местоположение', callback_data=STEP_LOCATION),
            InlineKeyboardButton(text=f'{smile_photo} Фото', callback_data=STEP_PHOTO),
        ],
        [
            InlineKeyboardButton(text=f'{smile_shedule} График работы', callback_data=STEP_SCHEDULE),
            InlineKeyboardButton(text=f'{smile_salary} Зарплата', callback_data=STEP_SALARY),
        ],
        [
            InlineKeyboardButton(text=f'{smile_back} Назад', callback_data=STEP_BACK),
            InlineKeyboardButton(text=f'{smile_rdy} Готово', callback_data=END),
        ]
    ]
    if user['cv']['speciality'] != 'Стоматолог':
        cv_other_buttons.remove([InlineKeyboardButton(
            text=f'{smile_specialisation} Специализация',
            callback_data=STEP_SPECIALISATION
        )])
    else:
        cv_other_buttons[2] = [InlineKeyboardButton(text=f'{smile_expirience} Опыт', callback_data=STEP_EXPERIENCE)]
    return InlineKeyboardMarkup(cv_other_buttons)


def speciality_keyboard():
    speciality_buttons = [
        [InlineKeyboardButton(text='Стоматолог', callback_data='Стоматолог')],
        [InlineKeyboardButton(text='Медсестра', callback_data='Медсестра')],
        [InlineKeyboardButton(text='Ассистент', callback_data='Ассистент')]
    ]
    return InlineKeyboardMarkup(speciality_buttons)


def specialisation_keyboard(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    specialisation_buttons = []
    specialisation_list = ['Терапевт', 'Ортопед', 'Хирург', 'Ортодонт', 'Детский врач']
    if user['cv']['specialisation']:
        user_specialis_list = user['cv'].get('specialisation')
        for spec in specialisation_list:
            if spec in user_specialis_list:
                text = f'{smile_yes} {spec}'
            else:
                text = f'{smile_no} {spec}'
            specialisation_buttons.append([InlineKeyboardButton(text=text, callback_data=spec)])
    else:
        for spec in specialisation_list:
            text = f'{smile_no} {spec}'
            specialisation_buttons.append([InlineKeyboardButton(text=text, callback_data=spec)])
    if firsttime_user(tg_id, 'cv'):
        text_back = f'{smile_back} Назад'
        specialisation_buttons.append([InlineKeyboardButton(text=text_back, callback_data='back_cv')])
        text_rdy = f'{smile_rdy} Далее'
    else:
        text_rdy = f'{smile_rdy} Готово'
    specialisation_buttons.append([InlineKeyboardButton(text=text_rdy, callback_data='end_specialisation')])
    return InlineKeyboardMarkup(specialisation_buttons)


def schedule_keyboard(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['speciality'] == 'Медсестра':
        schedule_buttons = [
            [InlineKeyboardButton(text='Любой график', callback_data='Любой график')],
            [InlineKeyboardButton(text='Частичная занятость', callback_data='Частичная занятость')],
            [InlineKeyboardButton(text='Разовый выход', callback_data='Разовый выход')],
        ]
    elif user['cv']['speciality'] == 'Ассистент':
        schedule_buttons = [
            [InlineKeyboardButton(text='Любой график', callback_data='Любой график')],
            [InlineKeyboardButton(text='Только выходные', callback_data='Только выходные')],
            [InlineKeyboardButton(text='Только первая смена', callback_data='Только первая смена')],
            [InlineKeyboardButton(text='Только вторая смена', callback_data='Только вторая смена')],
            [InlineKeyboardButton(text='Разовый выход', callback_data='Разовый выход')],
        ]
    else:
        schedule_buttons = [
            [InlineKeyboardButton(text='Полная занятость', callback_data='Полная занятость')],
            [InlineKeyboardButton(text='Частичная занятость', callback_data='Частичная занятость')],
        ]
    if firsttime_user(tg_id, 'cv'):
        text_back = f'{smile_back} Назад'
        schedule_buttons.append([InlineKeyboardButton(text=text_back, callback_data='back_cv')])
    return InlineKeyboardMarkup(schedule_buttons)

def salary_keyboard(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['speciality'] != 'Стоматолог':
        salary_buttons = [
            [InlineKeyboardButton(text=f'{smile_salary} от 1000 руб.', callback_data='от 1000 руб./0')],
            [InlineKeyboardButton(text=f'{smile_salary} от 2000 руб.', callback_data='от 2000 руб./1')],
            [InlineKeyboardButton(text=f'{smile_salary} от 3000 руб.', callback_data='от 3000 руб./2')],
        ]
    else:
        salary_buttons = [
            [InlineKeyboardButton(text=f'{smile_salary} от 15000 руб.', callback_data='от 15000 руб./0')],
            [InlineKeyboardButton(text=f'{smile_salary} от 40000 руб.', callback_data='от 40000 руб./1')],
            [InlineKeyboardButton(text=f'{smile_salary} от 80000 руб.', callback_data='от 80000 руб./2')],
        ]
    if firsttime_user(tg_id, 'cv'):
        text_back = f'{smile_back} Назад'
        salary_buttons.append([InlineKeyboardButton(text=text_back, callback_data='back_cv')])
    return InlineKeyboardMarkup(salary_buttons)

def education_keyboard(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['speciality'] == 'Медсестра':
        education_buttons = [
            [InlineKeyboardButton(text='среднее', callback_data='среднее/0')],
            [InlineKeyboardButton(
                text='среднее медицинское, неоконченное',
                callback_data='среднее мед., неоконченное/1'
            )],
            [InlineKeyboardButton(text='среднее медицинское', callback_data='среднее медицинское/2')],
        ]
    else:
        education_buttons = [
            [InlineKeyboardButton(text='среднее', callback_data='среднее/0')],
            [InlineKeyboardButton(text='среднее медицинское', callback_data='среднее медицинское/1')],
            [InlineKeyboardButton(text='высшее неоконченное', callback_data='высшее неоконченное/2')],
            [InlineKeyboardButton(text='высшее', callback_data='высшее/3')],
        ]
    if firsttime_user(tg_id, 'cv'):
        text_back = f'{smile_back} Назад'
        education_buttons.append([InlineKeyboardButton(text=text_back, callback_data='back_cv')])
    return InlineKeyboardMarkup(education_buttons)


def experience_keyboard(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['speciality'] == 'Медсестра':
        experience_buttons = [
            [InlineKeyboardButton(text='без опыта', callback_data='без опыта/0')],
            [InlineKeyboardButton(
                text='с опытом работы в медучреждении',
                callback_data='с опытом работы в медучреждении/1'
            )],
            [InlineKeyboardButton(
                text='с опытом работы в стоматологии',
                callback_data='с опытом работы в стоматологии/2'
            )],
        ]
    elif user['cv']['speciality'] == 'Ассистент':
        experience_buttons = [
            [InlineKeyboardButton(text='без опыта', callback_data='без опыта/0')],
            [InlineKeyboardButton(
                text='выпускник курса "Звездный Ассистент"',
                callback_data="Звездный Ассистент/1"
            )],
            [InlineKeyboardButton(text='с опытом работы', callback_data='с опытом работы/2')],
        ]
    else:
        experience_buttons = [
            [InlineKeyboardButton(text='без опыта', callback_data='без опыта/0')],
            [InlineKeyboardButton(text='от 1 года', callback_data='от 1 года/1')],
            [InlineKeyboardButton(text='от 3 лет', callback_data='от 3 лет/2')],
            [InlineKeyboardButton(text='от 5 лет', callback_data='от 5 лет/3')],
        ]
    if firsttime_user(tg_id, 'cv'):
        text_back = f'{smile_back} Назад'
        experience_buttons.append([InlineKeyboardButton(text=text_back, callback_data='back_cv')])
    return InlineKeyboardMarkup(experience_buttons)

def photo_pass_keyboard(tg_id):
    text = f'{smile_pass} Пропустить (можно добавить позднее)'
    text_back = f'{smile_back} Назад'
    photo_button = [
        [InlineKeyboardButton(text=text, callback_data='пропустить_фото')],
    ]
    if firsttime_user(tg_id, 'cv'):
        text_back = f'{smile_back} Назад'
        photo_button.append([InlineKeyboardButton(text=text_back, callback_data='back_cv')])
    return InlineKeyboardMarkup(photo_button)

def back_keyboard():
    text_back = f'{smile_back} Назад'
    photo_button = [
        [InlineKeyboardButton(text=text_back, callback_data='back_cv')]
    ]
    return InlineKeyboardMarkup(photo_button)

def contact_keyboard():
    button = KeyboardButton('Поделиться номером телефона', request_contact=True)
    return ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
