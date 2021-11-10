from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from bot_project_new.utils import firsttime_user
from DbFolder.db_file import DBase
dbase = DBase()


def start_keyboard():
    start_buttons = [
        [
            InlineKeyboardButton(text='Найти работу', callback_data='Найти работу'),
            InlineKeyboardButton(text='Найти сотрудника', callback_data='Найти сотрудника'),
            InlineKeyboardButton(text='Аренда стоматологического кресла', callback_data='Аренда кресла'),
        ],
    ]
    return InlineKeyboardMarkup(start_buttons)


def find_work_keyboard(tg_id):
    if firsttime_user(tg_id):
        text = 'Заполнить анкету'
    else:
        text = 'Редактировать анкету'
    find_work_buttons = [
        [
            InlineKeyboardButton(text=text, callback_data='Заполнить анкету'),
            InlineKeyboardButton(text='Смотреть вакансии', callback_data='Смотреть вакансии'),
        ],
    ]
    return InlineKeyboardMarkup(find_work_buttons)

# Обработка стартового хендлера (приветствие)
def start(update, context):
    dbase.get_or_create_user(update.effective_user)
    reply_markup = start_keyboard()
    update.message.reply_text(
        ("Привет, я бот, который поможет тебе найти работу или сотрудника, моя"
            "область - медицина."
            "Пожалуйста укажите, для чего вы используете бота?"),
        reply_markup=reply_markup)
    # update.effective_message.reply_html('Use bad_command to cause an error.')


# Обработка кнопи - найти работу
def find_work(update, context):
    update.callback_query.answer()
    reply_markup = find_work_keyboard(update.effective_user.id)
    dbase.get_or_create_user(update.effective_user)
    text = 'Для того, чтобы работодатель мог найти вас, пожалуйста, заполните анкету'
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


def find_worker(update, context):
    dbase.get_or_create_user(update.effective_user)
    text = ("Вы можете создать вакансию или искать работника.")
    keyboard = ReplyKeyboardMarkup([['Создать вакансию'], ['Смотреть резюме']], resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=keyboard)


def message_if_wrong(update, context):
    update.message.reply_text('Занятно:), но лучше воспользоваться кнопокой!')
