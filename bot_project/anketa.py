from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, replymarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler


step_name, step_age, step_expirience, step_komment, step_location = range(5)

def print_anketa_info(update, context):
    update.message.reply_text(
        f'''
        Ваши данные:
        Имя: {context.user_data['anketa']['name'] if context.user_data.get('anketa') else 'Значение не установлено'}
        Возраст: {context.user_data['anketa']['age'] if context.user_data['anketa'].get('age') else 'Значение не установлено'}
        Опыт: {context.user_data['anketa']['expirience'] if context.user_data['anketa'].get('expirience') else 'Значение не установлено'}
        Комментарий: {context.user_data['anketa']['komment'] if context.user_data['anketa'].get('komment') else 'Значение не установлено'}
        Место жительства: {context.user_data['anketa']['location'] if context.user_data['anketa'].get('location') else 'Значение не установлено'}
        '''
        )

def anketa_start(update, context):
    update.message.reply_text("Пожалуйста введите имя и фамилию", reply_markup=ReplyKeyboardRemove())
    return step_name

def anketa_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста введите корректно имя и фамилию')
        return step_name
    else:
        context.user_data['anketa'] = {'name': user_name}
        print_anketa_info(update, context)
        update.message.reply_text('Пожалуйста введите возраст')
    return step_age

def anketa_age(update, context):
    user_age = update.message.text
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            context.user_data['anketa']['age'] = user_age
            update.message.reply_text(f'Установлен возраст {user_age}')
            print_anketa_info(update, context)
            update.message.reply_text('Введите ваш опыт(в годах)')
            return step_expirience
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст')
            return step_age
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст')
        return step_age

def anketa_expirience(update, context):
    user_expirience = update.message.text
    try:
        user_expirience = int(user_expirience)
        if user_expirience > 0 and user_expirience < 100:
            context.user_data['anketa']['expirience'] = user_expirience
            update.message.reply_text(f'Установлен опыт {user_expirience}')
            print_anketa_info(update, context)
            update.message.reply_text('Пожалуйста, напишите о себе')
            return step_komment
        else:
            update.message.reply_text('Пожалуйста введите корректное число')
            return step_expirience
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректное число')
        return step_expirience


def anketa_komment(update, context):
    user_komment = update.message.text
    context.user_data['anketa']['komment'] = user_komment
    update.message.reply_text(f'Вашк комментарий: {user_komment}')
    print_anketa_info(update, context)
    update.message.reply_text('Пожалуйста введите ваше местоположение')
    return step_location

def anketa_location(update, context):
    user_location = update.message.text
    context.user_data['anketa']['location'] = user_location
    update.message.reply_text(f'Ваше местоположение: {user_location}')
    update.message.reply_text('Анкета заполнена, спасибо')
    print_anketa_info(update, context)
    #print_anketa_info(update, context)
    return ConversationHandler.END

def anketa_fallback(update, context):
    update.message.reply_text('Я вас не понимаю!')
