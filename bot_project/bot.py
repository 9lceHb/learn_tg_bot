
import logging
# from datetime import datetime
import settings

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from anketa import anketa_expirience, anketa_komment, anketa_location, step_name, step_age, step_expirience, step_komment, step_location
from anketa import anketa_start, anketa_name, anketa_age, anketa_expirience, anketa_komment, anketa_location, anketa_fallback

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

logger = logging.getLogger(__name__)

def start_keyboard():
    return ReplyKeyboardMarkup([
        ['Заполнить анкету']
            ], resize_keyboard=True)

def start(update: Update, context: CallbackContext) -> int:
    reply_markup = start_keyboard()
    update.message.reply_text(
        "Привет, я бот, который поможет тебе найти работу или сотрудника, моя область - медицина",
     reply_markup=reply_markup)
    
def main() -> None:
    mybot = Updater(settings.API_KEY, use_context=True)  # request_kwargs=PROXY
    dp = mybot.dispatcher

    anketa_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Заполнить анкету)$'), anketa_start)],
        states={
            step_name: [MessageHandler(Filters.text, anketa_name)],
            step_age: [MessageHandler(Filters.text, anketa_age)],
            step_expirience: [MessageHandler(Filters.text, anketa_expirience)],
            step_komment: [MessageHandler(Filters.text, anketa_komment)],   
            step_location: [MessageHandler(Filters.text, anketa_location)]
        },
        fallbacks=[MessageHandler(Filters.text | Filters.photo | Filters.video, anketa_fallback)])

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(anketa_handler)
    mybot.start_polling()
    mybot.idle()

if __name__ == '__main__':
    main()
