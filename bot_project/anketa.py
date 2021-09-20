from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, replymarkup


def anketa_start(update, context):
    print('hi')
    update.message.reply_text(
        'Как вас зовут(Имя, Фамилия)?',
          reply_markup=ReplyKeyboardRemove()
     )
    return 'name'


def anketa_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Пожалуйста введите имя и фамилию')
        return 'name'
    else:
        context.user_data['anketa'] = {'name': user_name}
        reply_keyboard = [['1', '2', '3', '4', '5']]
        update.message.reply_text(
            'Пожалуйста оцените бота от 1 до 5',
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
    return 'rating'