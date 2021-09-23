from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, replymarkup
from telegram.ext import ConversationHandler


def anketa_keyboard():
    return ReplyKeyboardMarkup([['name', 'age']])

def anketa_start(update, context):
    update.message.reply_text(
        'Как вас зовут(Имя, Фамилия)?',
          reply_markup=anketa_keyboard()
     )
    return 'name'


def anketa_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста введите имя и фамилию')
        return 'name'
    else:
        context.user_data['anketa'] = {'name': user_name}
        update.message.reply_text(
            'Пожалуйста введите возраст', reply_markup=anketa_keyboard())
    return 'age'


def anketa_age(update, context):
    user_age = update.message.text
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            context.user_data['anketa']['age'] = user_age
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст', reply_markup=anketa_keyboard())
            return 'age'
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст', reply_markup=anketa_keyboard())
        return 'age'
    return ConversationHandler.END
