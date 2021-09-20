
import logging
from datetime import datetime
import settings

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from anketa import anketa_start, anketa_name


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


# PROXY = {
#     'proxy_url': settings.PROXY_url,
#     'urllib3_proxy_kwargs': {
#         'username': settings.PROXY_username,
#         'password': settings.PROXY_pass
#     }
# }

def my_keyboard():
    return ReplyKeyboardMarkup([['Заполнить анкету']])


def greet_user(update, context):
    text = 'Привет, я бот, который поможет вам найти работу или работника). Моя область поиска медицинские учереждения, стоматология.'
    my_keyboardd = my_keyboard()
    print(text)
    #my_keyboard = ReplyKeyboardMarkup([['Ищу работу', 'Ищу сотрудника']])
    update.message.reply_text(text, reply_markup=my_keyboardd)


def talk_to_me(update, context):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text('Пожалуйста используйте команду: /planet (any planet)')


def main():
    mybot = Updater(settings.API_KEY, use_context=True)# request_kwargs=PROXY

    dp = mybot.dispatcher

    anketa = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Заполнить анкету)$'), anketa_start)
        ],
        states={
            'name': [MessageHandler(Filters.text, anketa_name)]
        },
        fallbacks=[]
    )
    dp.add_handler(anketa)
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
