from bot.db import DBase
from bot.keyboards import find_work_keyboard, start_keyboard
from bot.utils import firsttime_user

dbase = DBase()


# Обработка стартового хендлера (приветствие)
def start(update, context):
    dbase.get_or_create_user(update.effective_user)
    reply_markup = start_keyboard()
    text = '''
Привет! 👋
Я бот, который поможет найти работу или сотрудника, моя специализация – стоматология 🦷
Чем я могу быть Вам полезен?
'''
    update.message.reply_text(text=text, reply_markup=reply_markup)


def delete_from_base(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv'].get('speciality'):
        dbase.db_client.users.delete_one({'tg_id': tg_id})
        dbase.get_or_create_user(update.effective_user)
        text = 'Текущий пользователь удален из базы'
        update.callback_query.edit_message_text(text=text, reply_markup=start_keyboard())
    else:
        text = 'Пользователя в базе нет'
        dbase.save_cv(tg_id, 'speciality', '_')
        update.callback_query.edit_message_text(text=text, reply_markup=start_keyboard())


# Обработка кнопи - найти работу
def find_work(update, context):
    tg_id = update.effective_user.id
    update.callback_query.answer()
    reply_markup = find_work_keyboard(update.effective_user.id)
    dbase.get_or_create_user(update.effective_user)
    if firsttime_user(tg_id, 'cv'):
        text = '''
Прежде всего, давайте познакомимся. Я задам несколько
вопросов, которые помогут мне предложить Вам наиболее
подходящие вакансии, а также, если Вы захотите,
опубликовать Ваше резюме для соискателя.
Это займет не более 3 минут.
'''
    else:
        text = '''
Здесь Вы можете отредактировать свою анкету, или удалить ее из поиска.
'''
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


# def find_worker(update, context):
#     dbase.get_or_create_user(update.effective_user)
#     text = ("Вы можете создать вакансию или искать работника.")
#     keyboard = ReplyKeyboardMarkup([['Создать вакансию'], ['Смотреть резюме']], resize_keyboard=True)
#     update.message.reply_text(text=text, reply_markup=keyboard)


def message_if_wrong(update, context):
    update.message.reply_text('Занятно:), но лучше воспользоваться кнопокой!', reply_markup=start_keyboard())
