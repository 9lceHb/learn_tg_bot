
import logging
# from datetime import datetime
import settings

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)

from anketa import (
    anketa_start,
    anketa_name,
    anketa_age,
    anketa_expirience,
    anketa_komment,
    anketa_location,
    anketa_fallback,
    end_describing,
    ask_for_input
)
def anketa_start(update, context):

    if not context.user_data.get('anketa'):
        print('yes')
        context.user_data['anketa'] = {}
    print(context.user_data['anketa'])
    update.message.reply_text(
        'Заполнение анкеты',

    )
    update.message.reply_text(
        "Выберите поле для заполнения",
    )
def main():
    mybot = Updater(settings.API_KEY, use_context=True)  # request_kwargs=PROXY

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', anketa_start))

    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()