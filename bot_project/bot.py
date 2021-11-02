import logging
import settings

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)

from anketa import anketa_handler

from filter_cv import filter_cv_handler


from handlers import (
    find_work,
    message_if_wrong,
    start,
    find_worker
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
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^(Найти работу)$'), find_work))
    dp.add_handler(MessageHandler(Filters.regex('^(Найти сотрудника)$'), find_worker))
    dp.add_handler(anketa_handler)
    dp.add_handler(filter_cv_handler)
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, message_if_wrong))
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
