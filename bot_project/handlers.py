from telegram import ReplyKeyboardMarkup

from DbFolder.db_file import DBase
dbase = DBase()


def start_keyboard():
    return ReplyKeyboardMarkup([['Найти работу'], ['Найти сотрудника']], resize_keyboard=True)


# Обработка стартового хендлера (приветствие)
def start(update, context):
    dbase.get_or_create_user(update.effective_user, update.message.chat.id)
    reply_markup = start_keyboard()
    update.message.reply_text(
        ("Привет, я бот, который поможет тебе найти работу или сотрудника, моя"
            "область - медицина."
            "Пожалуйста укажите, для чего вы используете бота?"),
        reply_markup=reply_markup)
    # update.effective_message.reply_html('Use bad_command to cause an error.')


# Обработка кнопи - найти работу
def find_work(update, context):
    dbase.get_or_create_user(update.effective_user, update.message.chat.id)
    text = ("Вы можете смотеть вакансии или заполнить анкету,"
            " чтобы работодатель мог найти вас.")
    keyboard = ReplyKeyboardMarkup([['Заполнить анкету'], ['Смотреть вакансии']], resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=keyboard)


def find_worker(update, context):
    dbase.get_or_create_user(update.effective_user, update.message.chat.id)
    text = ("Вы можете создать вакансию или искать работника.")
    keyboard = ReplyKeyboardMarkup([['Создать вакансию'], ['Смотреть резюме']], resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=keyboard)


def message_if_wrong(update, context):
    update.message.reply_text('Занятно:), но лучше воспользоваться кнопокой!')
