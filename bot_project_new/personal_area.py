from telegram import ParseMode
from payments import payment_conv_handler
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
)
from DbFolder.db_file import DBase
from keyboards import (
    personal_area_keyboard,
    STEP_MANAGE_AREA,
    # STEP_SUPPORT,
    # STEP_PAYMENT_BACK
)
dbase = DBase()


def personal_area(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    balance = user['balance']
    text = f'''
    Здесь вы можете пополнить баланс, или обратиться в поддержку, по любым вопросам.
    Ваш текущий баланс составляет {balance} рублей.
    '''
    reply_markup = personal_area_keyboard
    update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_MANAGE_AREA


personal_area_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(personal_area, pattern='^' + 'Личный кабинет' + '$'),
    ],
    states={
        STEP_MANAGE_AREA: [
            payment_conv_handler,
            # CallbackQueryHandler(start_support, pattern='^' + 'STEP_SUPPORT' + '$'),
        ],
    },
    fallbacks=[
        # MessageHandler(Filters.text & (~ Filters.command) | Filters.photo | Filters.video, filter_fallback),
        # CallbackQueryHandler(end_describing_filter, pattern='^' + str(END) + '$'),
        ],
    allow_reentry=True,
    per_chat=False
)
