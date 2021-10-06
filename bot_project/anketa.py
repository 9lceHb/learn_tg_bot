from telegram import (
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ConversationHandler

(
    STEP_NAME,
    STEP_AGE,
    STEP_EXPIRIENCE,
    STEP_KOMMENT,
    STEP_LOCATION,
    STEP_INPUT,
    END
) = map(chr, range(7))

step_dict = {
    STEP_NAME: 'Имя, Фамилия',
    STEP_AGE: 'Возраст(в годах)',
    STEP_EXPIRIENCE: 'Опыт(в годах)',
    STEP_KOMMENT: 'Комментарий',
    STEP_LOCATION: 'Локация'}


def anketa_keyboard():
    anketa_buttons = [
            [
                InlineKeyboardButton(
                    text='Имя, Фамилия', callback_data=str(STEP_NAME)
                    ),
                InlineKeyboardButton(
                    text='Возраст(в годах)', callback_data=str(STEP_AGE)
                    ),
            ],
            [
                InlineKeyboardButton(
                    text='Опыт(в годах)', callback_data=str(STEP_EXPIRIENCE)
                    ),
                InlineKeyboardButton(
                    text='Комментарий', callback_data=str(STEP_KOMMENT)
                    ),
                InlineKeyboardButton(
                    text='Локация', callback_data=str(STEP_LOCATION)
                    ),
            ],
            [
                InlineKeyboardButton(text='Готово', callback_data=str(END))
            ]
        ]
    return InlineKeyboardMarkup(anketa_buttons)


def print_anketa_info(update, context):
    update.message.reply_text(
        f'''
        Ваши данные:
        Имя: {context.user_data['anketa']['name'] if context.user_data.get('anketa') else 'Значение не установлено'}
        Возраст: {context.user_data['anketa']['age'] if context.user_data['anketa'].get('age') else 'Значение не установлено'}
        Опыт: {context.user_data['anketa']['expirience'] if context.user_data['anketa'].get('expirience') else 'Значение не установлено'}
        Комментарий: {context.user_data['anketa']['komment'] if context.user_data['anketa'].get('komment') else 'Значение не установлено'}
        Место жительства: {context.user_data['anketa']['location'] if context.user_data['anketa'].get('location') else 'Значение не установлено'}
        ''', reply_markup=anketa_keyboard()
        )


def anketa_start(update, context):
    context.user_data['anketa'] = {}
    update.message.reply_text(
        'Заполнение анкеты',
        reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_text(
        "Выберите поле для заполнения",
        reply_markup=anketa_keyboard())
    return STEP_INPUT


def anketa_name(update, context):

    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста введите корректно имя и фамилию')
        return STEP_NAME
    else:
        context.user_data['anketa']['name'] = user_name
        print(user_name)
        print(context.user_data['anketa']['name'])
        print_anketa_info(update, context)
    return STEP_INPUT


def anketa_age(update, context):
    user_age = update.message.text
    try:
        user_age = int(user_age)
        if user_age > 0 and user_age < 100:
            context.user_data['anketa']['age'] = user_age
            print_anketa_info(update, context)
            return STEP_INPUT
        else:
            update.message.reply_text('Пожалуйста введите корректный возраст')
            return STEP_AGE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректный возраст')
        return STEP_AGE


def anketa_expirience(update, context):
    user_expirience = update.message.text
    try:
        user_expirience = int(user_expirience)
        if user_expirience > 0 and user_expirience < 100:
            context.user_data['anketa']['expirience'] = user_expirience
            print_anketa_info(update, context)
            return STEP_INPUT
        else:
            update.message.reply_text('Пожалуйста введите корректное число')
            return STEP_EXPIRIENCE
    except ValueError:
        update.message.reply_text('Пожалуйста введите корректное число')
        return STEP_EXPIRIENCE


def anketa_komment(update, context):
    user_komment = update.message.text
    context.user_data['anketa']['komment'] = user_komment
    print_anketa_info(update, context)
    return STEP_INPUT


def anketa_location(update, context):
    user_location = update.message.text
    context.user_data['anketa']['location'] = user_location
    print_anketa_info(update, context)
    print(context.user_data)
    print(update)
    return STEP_INPUT


def anketa_fallback(update, context):
    update.message.reply_text('Пожалуйста выберите поле из списка!')


def end_describing(update, context):
    text = 'Вы завершили заполнение анкеты'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return ConversationHandler.END
