from typing import Text
from telegram import (
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import os
from emoji import emojize
from bot_project_new.get_cv import STEP_EXPIRIENCE
from bot_project_new.utils import (
    is_human_and_sfw,
    update_user_location,
    make_station_numbers_set,
    make_photo_path,
    print_location,
    firsttime_user,
)
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
from pprint import pprint

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
    END
) = map(chr, range(15))


dbase = DBase()

def print_anketa_info(update, context, markup, callback=True):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if firsttime_user(update.effective_user.id):
        dbase.db_client.users.update_one({'_id': user['_id']}, {'$set': {'first_time': False}})
    text = f'''
    Желаемая вакансия:
    Специальность: {user['anketa']['speciality']
            if user['anketa'].get('speciality')
            else 'Значение не установлено'}
    График работы: {user['anketa']['schedule']
            if user['anketa'].get('schedule')
            else 'Значение не установлено'}
    Минимальная оплата труда: {user['anketa']['salary']
            if user['anketa'].get('salary')
            else 'Значение не установлено'}
    Предпочитительное место работы:{print_location(user)}
    Ваши данные:
    ФИО: {user['anketa']['name']
            if user['anketa'].get('name')
            else 'Значение не установлено'}
    Возраст: {user['anketa']['age']
            if user['anketa'].get('age')
            else 'Значение не установлено'}
    Образование: {user['anketa']['education']
            if user['anketa'].get('education')
            else 'Значение не установлено'}
    Опыт: {user['anketa']['experience']
            if user['anketa'].get('experience')
            else 'Значение не установлено'}
    Фото: {'Фото добавлено'
            if user['anketa'].get('photo')
            else 'Фото не добавлялось'}
    Статус: {'Анкета видна в поиске'
            if user['anketa']['show_cv']
            else 'Анкета удалена из поиска'}
    '''
    reply_markup = markup
    if callback:
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        update.message.reply_text(text=text, reply_markup=reply_markup)
    #context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)


def cv_main_keyboard(update, context):
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
            InlineKeyboardButton(text='Желаемая локация', callback_data=STEP_LOCATION),
            InlineKeyboardButton(text='Фото', callback_data=STEP_PHOTO),
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


def cv_other_keyboard():
    anketa_other_buttons = [
        [
            InlineKeyboardButton(text='Специальность', callback_data=STEP_SPECIALITY,),
        ],
        [
            InlineKeyboardButton(text='Специализация', callback_data=STEP_SPECIALISATION),
        ],
        [
            InlineKeyboardButton(text='График работы', callback_data=STEP_SCHEDULE),
            InlineKeyboardButton(text='Заработная плата', callback_data=STEP_SALARY),
        ],
        [
            InlineKeyboardButton(text='Образование', callback_data=STEP_EDUCATION),
            InlineKeyboardButton(text='Опыт', callback_data=STEP_EXPIRIENCE),
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data=STEP_BACK),
            InlineKeyboardButton(text='Готово', callback_data=END),
        ]
    ]
    return InlineKeyboardMarkup(anketa_other_buttons)


def speciality_keyboard():
    speciality_buttons = [
        [InlineKeyboardButton(text='Врач', callback_data='Врач')],
        [InlineKeyboardButton(text='Мед работник', callback_data='Мед работник')],
        [InlineKeyboardButton(text='Ассистент', callback_data='Ассистент')]
    ]
    return InlineKeyboardMarkup(speciality_buttons)

def schedule_keyboard():
    schedule_buttons = [
        [InlineKeyboardButton(text='Любой график', callback_data='Любой график')],
        [InlineKeyboardButton(text='Частичная занятость', callback_data='Частичная занятость')],
        [InlineKeyboardButton(text='Разовый выход', callback_data='Разовый выход')],
    ]
    return InlineKeyboardMarkup(schedule_buttons)

def salary_keyboard():
    salary_buttons = [
        [InlineKeyboardButton(text='от 1000', callback_data='от 1000 руб.')],
        [InlineKeyboardButton(text='от 2000', callback_data='от 2000 руб.')],
        [InlineKeyboardButton(text='от 3000', callback_data='от 3000 руб.')],
    ]
    return InlineKeyboardMarkup(salary_buttons)

def education_keyboard():
    education_buttons = [
        [InlineKeyboardButton(text='среднее', callback_data='среднее')],
        [InlineKeyboardButton(
            text='среднее медицинское, неоконченное',
            callback_data='среднее медицинское, неоконченное'
        )],
        [InlineKeyboardButton(text='среднее медицинское', callback_data='среднее медицинское')],
    ]
    return InlineKeyboardMarkup(education_buttons)


def experience_keyboard():
    experience_buttons = [
        [InlineKeyboardButton(text='без опыта', callback_data='без опыта')],
        [InlineKeyboardButton(
            text='с опытом работы в медучреждении',
            callback_data='с опытом работы в медучреждении'
        )],
        [InlineKeyboardButton(text='с опытом работы в стоматологии', callback_data='с опытом работы в стоматологии')],
    ]
    return InlineKeyboardMarkup(experience_buttons)

def photo_pass_keyboard():
    photo_button = [
        [
            InlineKeyboardButton(text='Пропустить (вы сможете добавить фото позднее)', callback_data='пропустить_фото'),
        ],
    ]
    return InlineKeyboardMarkup(photo_button)

speciality_pattern = ('^Врач$|^Мед работник$|^Ассистент$')
input_patterns = (
    f'^{STEP_AGE}$|'
    f'^{STEP_LOCATION}$|'
    f'^{STEP_NAME}$|'
    f'^{STEP_SPECIALITY}$|'
    f'^{STEP_SPECIALISATION}$|'
    f'^{STEP_SCHEDULE}$|'
    f'^{STEP_SALARY}$|'
    f'^{STEP_EXPIRIENCE}$|'
    f'^{STEP_EDUCATION}$|'
    f'^{STEP_PHOTO}$'
)

step_dict = {
    STEP_NAME: ['''
    Напишите Ваше имя, отчество и фамилию.
    Пример: "Иван Иванович Иванов".
    ''', None],
    STEP_AGE: ['Напишите сколько вам полных лет', None],
    STEP_LOCATION: ['''
    Где удобно работать?
    (Вы можете вводить через запятую необходимые станции метро, линии метро, районы, округа.
    Пример: "Речной вокзал, САО".
    ''', None],
    STEP_SPECIALITY: ['Пожалуйста, выберите вашу специальность', speciality_keyboard()],
    STEP_SPECIALISATION: ['Пожалуйста, выберите вашу специализацию (вы можете выбрать сразу несколько пунктов)', None],
    STEP_SCHEDULE: ['Выберите предпочтительный график работы', schedule_keyboard()],
    STEP_SALARY: ['Выберите минимальную оплату за смену(полдня, 6 - 8 часов)', salary_keyboard()],
    STEP_EDUCATION: ['Выберите ваше образование', education_keyboard()],
    STEP_EXPIRIENCE: ['Выберите ваш опыт работы', experience_keyboard()],
    STEP_PHOTO: ['Прикрепите вашу фотографию', None],
    END: ['Вы завершили заполнение анкеты', None],
}

def manage_choosen_button(update, context):
    update.callback_query.answer()
    context.user_data['CURRENT_FEATURE'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE']
    text = step_dict[user_data_key][0]
    reply_markup = step_dict[user_data_key][1]
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    return user_data_key


def cv_move_other(update, context):
    update.callback_query.answer()
    print_anketa_info(update, context, cv_other_keyboard())
    return STEP_UPDATE_CV


# Обработчик кнопки заполнить анкету
def cv_start(update, context):
    update.callback_query.answer()
    if firsttime_user(update.effective_user.id):
        text = 'Пожалуйста, выберите вашу специальность'
        update.callback_query.edit_message_text(text=text, reply_markup=speciality_keyboard())
        return STEP_SPECIALITY
    else:
        print_anketa_info(update, context, cv_main_keyboard(update, context))
        return STEP_UPDATE_CV

def not_show_cv(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['anketa']['show_cv']:
        dbase.save_anketa(tg_id, 'show_cv', False)
    else:
        dbase.save_anketa(tg_id, 'show_cv', True)
    print_anketa_info(update, context, cv_main_keyboard(update, context))
    return STEP_UPDATE_CV


def choose_speciality(update, context):
    update.callback_query.answer()
    user_speciality = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'speciality', user_speciality)
    if firsttime_user(tg_id):
        text = 'Выберите предпочтительный график работы'
        update.callback_query.edit_message_text(text=text, reply_markup=schedule_keyboard())
        return STEP_SCHEDULE
    else:
        print_anketa_info(update, context, cv_other_keyboard())
        return STEP_UPDATE_CV


def choose_schedule(update, context):
    update.callback_query.answer()
    user_schedule = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'schedule', user_schedule)
    if firsttime_user(tg_id):
        text = '''
        Где удобно работать?
        (Вы можете вводить через запятую необходимые станции метро, линии метро, районы, округа.
        Пример: "Речной вокзал, САО".
        '''
        update.callback_query.edit_message_text(text=text)
        return STEP_LOCATION
    else:
        print_anketa_info(update, context, cv_other_keyboard())
        return STEP_UPDATE_CV

def choose_location(update, context):
    user_location = update.message.text
    if update_user_location(user_location):
        user_location = update_user_location(user_location)
        station_numbers = make_station_numbers_set(user_location)
        tg_id = update.effective_user.id
        dbase.save_anketa(tg_id, 'location', user_location)
        dbase.save_anketa(tg_id, 'station_numbers', station_numbers)
        if firsttime_user(tg_id):
            text = 'Выберите минимальную оплату за смену(полдня, 6 - 8 часов)'
            update.message.reply_text(text=text, reply_markup=salary_keyboard())
            return STEP_SALARY
        else:
            print_anketa_info(update, context, cv_main_keyboard(update, context), callback=False)
            return STEP_UPDATE_CV
    else:
        update.message.reply_text('Один или несколько объектов не распознаны, попробуйте еще раз')
        return STEP_LOCATION


def choose_salary(update, context):
    update.callback_query.answer()
    user_salary = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'salary', user_salary)
    if firsttime_user(tg_id):
        text = '''
        Теперь заполним вашу анкету,
        Напишите Ваше имя, отчество и фамилию.
        Пример: "Иван Иванович Иванов".
        '''
        update.callback_query.edit_message_text(text=text)
        return STEP_NAME
    else:
        print_anketa_info(update, context, cv_other_keyboard())
        return STEP_UPDATE_CV

def choose_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста, введите ФИО(не менее 2-х слов)')
        return STEP_NAME
    else:
        tg_id = update.effective_user.id
        dbase.save_anketa(tg_id, 'name', user_name)
    if firsttime_user(update.effective_user.id):
        update.message.reply_text('Напишите сколько вам полных лет')
        return STEP_AGE
    else:
        print_anketa_info(update, context, cv_main_keyboard(update, context), callback=False)
        return STEP_UPDATE_CV


def choose_age(update, context):
    user_age = update.message.text
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            tg_id = update.effective_user.id

            dbase.save_anketa(tg_id, 'age', user_age)
            if firsttime_user(update.effective_user.id):
                text = 'Выберите ваше образование'
                update.message.reply_text(text=text, reply_markup=education_keyboard())
                return STEP_EDUCATION
            else:
                print_anketa_info(update, context, cv_main_keyboard(update, context), callback=False)
                return STEP_UPDATE_CV
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст')
            return STEP_AGE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст')
        return STEP_AGE

def choose_education(update, context):
    update.callback_query.answer()
    user_education = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'education', user_education)
    if firsttime_user(tg_id):
        text = 'Выберите ваш опыт работы'
        update.callback_query.edit_message_text(text=text, reply_markup=experience_keyboard())
        return STEP_EXPERIENCE
    else:
        print_anketa_info(update, context, cv_other_keyboard())
        return STEP_UPDATE_CV

def choose_experience(update, context):
    update.callback_query.answer()
    user_experience = update.callback_query.data
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'experience', user_experience)
    if firsttime_user(tg_id):
        text = '''
        Прикрепите Ваше фото. Это не обязательно, но сильно повышает Ваши шансы найти работу:)
        '''
        update.callback_query.edit_message_text(text=text, reply_markup=photo_pass_keyboard())
        return STEP_PHOTO
    else:
        print_anketa_info(update, context, cv_other_keyboard())
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
        dbase.save_anketa(tg_id, 'photo', photo_path_list)
        print_anketa_info(update, context, cv_main_keyboard(update, context), callback=False)
        return STEP_UPDATE_CV
    else:
        update.message.reply_text('Фото не подхоидт, выберите другое', reply_markup=photo_pass_keyboard())
        return STEP_PHOTO

def photo_pass(update, context):
    update.callback_query.answer()
    user_photo = None
    tg_id = update.effective_user.id
    dbase.save_anketa(tg_id, 'photo', user_photo)
    print_anketa_info(update, context, cv_main_keyboard(update, context))
    return STEP_UPDATE_CV


# Функция дает ответ если пользователь в анкете не выбрал поле
def cv_fallback(update, context):
    text = 'Заполнение анкеты'
    update.message.reply_text(text=text, reply_markup=cv_main_keyboard(update, context))
    # не работает готово
    return STEP_UPDATE_CV


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
        STEP_SPECIALITY: [CallbackQueryHandler(choose_speciality)],
        STEP_SCHEDULE: [CallbackQueryHandler(choose_schedule)],
        STEP_LOCATION: [MessageHandler(Filters.text, choose_location)],
        STEP_SALARY: [CallbackQueryHandler(choose_salary)],
        STEP_NAME: [MessageHandler(Filters.text, choose_name)],
        STEP_AGE: [MessageHandler(Filters.text, choose_age)],
        STEP_EDUCATION: [CallbackQueryHandler(choose_education)],
        STEP_EXPERIENCE: [CallbackQueryHandler(choose_experience)],
        STEP_PHOTO: [
            MessageHandler(Filters.photo, check_user_photo),
            CallbackQueryHandler(photo_pass, pattern='^' + 'пропустить_фото' + '$'),
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
