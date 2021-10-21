
import logging
# from datetime import datetime
import settings

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
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
    ask_for_input,
    check_user_photo
)

from handlers import (
    find_work,
    message_if_wrong,
    start
)

from anketa import (
    STEP_NAME,
    STEP_AGE,
    STEP_EXPIRIENCE,
    STEP_KOMMENT,
    STEP_LOCATION,
    STEP_INPUT,
    END,
    STEP_PHOTO
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


def main() -> None:
    mybot = Updater(settings.API_KEY, use_context=True)  # request_kwargs=PROXY
    dp = mybot.dispatcher
    # Диалог для заполнения анкеты, каждый этап возвращается к STEP_INPUT
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
            STEP_LOCATION: [MessageHandler(Filters.text, anketa_location)],
            STEP_PHOTO: [MessageHandler(Filters.photo, check_user_photo)]
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
    dp.add_handler(MessageHandler(
        Filters.regex('^(Найти работу)$'),
        find_work)
        )
    dp.add_handler(anketa_handler)
    dp.add_handler(MessageHandler(
        Filters.text | Filters.photo,
        message_if_wrong)
        )
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
