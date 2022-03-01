import logging

from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater

from bot import settings
from bot.filter_cv import filter_handler
from bot.get_cv import cv_handler
from bot.handlers import delete_from_base, find_work, message_if_wrong, start  # find_worker,
from bot.personal_area import personal_area_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


logger = logging.getLogger(__name__)


def main() -> None:
    mybot = Updater(settings.API_KEY, use_context=True)  # request_kwargs=PROXY
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(find_work, pattern='^Найти работу$'))
    dp.add_handler(CallbackQueryHandler(delete_from_base, pattern='^удалить запись$'))
    dp.add_handler(cv_handler)
    dp.add_handler(filter_handler)
    dp.add_handler(personal_area_handler)
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, message_if_wrong))
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
