
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
    end_describing
)

from anketa import (
    STEP_NAME,
    STEP_AGE,
    STEP_EXPIRIENCE,
    STEP_KOMMENT,
    STEP_LOCATION,
    STEP_INPUT,
    END,
    step_dict
)

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
        "Привет, я бот, который поможет тебе найти работу или сотрудника, моя"
        " область - медицина",
        reply_markup=reply_markup)


def ask_for_input(update: Update, context: CallbackContext) -> str:
    """Prompt user to input data for selected feature."""
    print('step_input')
    context.user_data['CURRENT_FEATURE'] = update.callback_query.data
    user_data_key = context.user_data['CURRENT_FEATURE']
    text = f'Пожалуйста введите значение для поля-{step_dict[user_data_key]}:'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return user_data_key


def main() -> None:
    mybot = Updater(settings.API_KEY, use_context=True)  # request_kwargs=PROXY

    dp = mybot.dispatcher

    anketa_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                Filters.regex('^(Заполнить анкету)$'),
                anketa_start
            )
            ],
        states={
            STEP_INPUT: [CallbackQueryHandler(
                ask_for_input,
                pattern='^(?!' + str(END) + ').*$'
                )],
            STEP_NAME: [MessageHandler(Filters.text, anketa_name)],
            STEP_AGE: [MessageHandler(Filters.text, anketa_age)],
            STEP_EXPIRIENCE: [MessageHandler(Filters.text, anketa_expirience)],
            STEP_KOMMENT: [MessageHandler(Filters.text, anketa_komment)],
            STEP_LOCATION: [MessageHandler(Filters.text, anketa_location)]
            },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.photo | Filters.video,
                anketa_fallback
                ),
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$')
        ]
        )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(anketa_handler)
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
