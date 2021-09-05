import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings


logging.basicConfig(filename='bot.log', level=logging.INFO)


def talk_to_me(update, context):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text(user_text)


def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, я бот повторятель!')


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()
    


if __name__ == '__main__':
    main()
