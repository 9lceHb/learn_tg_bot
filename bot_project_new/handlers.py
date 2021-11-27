from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from utils import firsttime_user
from DbFolder.db_file import DBase
from telegram.ext import ConversationHandler
dbase = DBase()
from emoji import emojize

def start_keyboard():
    smile_work = emojize(':hospital:', use_aliases=True)
    smile_worker = emojize(':construction_worker:', use_aliases=True)
    smile_chair = emojize(':seat:', use_aliases=True)
    start_buttons = [
        [InlineKeyboardButton(text=f'{smile_work} Найти работу', callback_data='Найти работу')],
        [InlineKeyboardButton(text=f'{smile_worker} Найти сотрудника', callback_data='Найти сотрудника')],
        [InlineKeyboardButton(text=f'{smile_chair} удалить запись из базы', callback_data='удалить запись')],
    ]
    return InlineKeyboardMarkup(start_buttons)


def find_work_keyboard(tg_id):
    smile_write = emojize(':pencil2:', use_aliases=True)
    smile_look = emojize(':page_with_curl:', use_aliases=True)
    if firsttime_user(tg_id, 'cv'):
        text = f'{smile_write} Приступим!'
    else:
        text = f'{smile_write} Моя анкета'
    find_work_buttons = [
        [
            InlineKeyboardButton(text=text, callback_data='Заполнить анкету'),
            # InlineKeyboardButton(text=f'{smile_look} Смотреть вакансии', callback_data='Смотреть вакансии'),
        ],
    ]
    return InlineKeyboardMarkup(find_work_buttons)

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
    # update.effective_message.reply_html('Use bad_command to cause an error.')

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
    update.callback_query.answer()
    reply_markup = find_work_keyboard(update.effective_user.id)
    dbase.get_or_create_user(update.effective_user)
    text = '''
Прежде всего, давайте познакомимся. Я задам несколько
вопросов, которые помогут мне предложить Вам наиболее
подходящие вакансии, а также, если Вы захотите,
опубликовать Ваше резюме для соискателя.
Это займет не более 3 минут.
'''
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


def find_worker(update, context):
    dbase.get_or_create_user(update.effective_user)
    text = ("Вы можете создать вакансию или искать работника.")
    keyboard = ReplyKeyboardMarkup([['Создать вакансию'], ['Смотреть резюме']], resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=keyboard)


def message_if_wrong(update, context):
    update.message.reply_text('Занятно:), но лучше воспользоваться кнопокой!', reply_markup=start_keyboard())
