from telegram import ParseMode
from telegram.ext import CallbackQueryHandler, ConversationHandler, Filters, MessageHandler

from bot.db import DBase
from bot.keyboards import (  # STEP_SUPPORT,; STEP_PAYMENT_BACK
    STEP_MANAGE_AREA,
    STEP_SAVE_ISSUE,
    personal_area_keyboard,
    start_keyboard,
)
from bot.payments import payment_conv_handler

dbase = DBase()


def personal_area(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    balance = user['balance']
    text = f'''
Здесь вы можете пополнить баланс, или обратиться в поддержку, по любым вопросам.
Ваш <b>текущий баланс</b> составляет <b>{balance} рублей</b>.
'''
    reply_markup = personal_area_keyboard()
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_MANAGE_AREA


def end_describing_area(update, context):
    text = '''
Привет! 👋
Я бот, который поможет найти работу или сотрудника, моя специализация – стоматология 🦷
Чем я могу быть Вам полезен?
'''
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=start_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


def start_support(update, context):
    text = 'Пожалуйста, опишите вашу проблему как можно конкретнее!'
    chat_id = update.callback_query.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.HTML
    )
    return STEP_SAVE_ISSUE


def save_issue(update, context):
    issue_text = update.message.text
    tg_id = update.effective_user.id
    dbase.create_issue(update.effective_user, issue_text)
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    balance = user['balance']
    reply_markup = personal_area_keyboard()
    text = f'''
Спасибо, ваше обращение принято!
Ваш <b>текущий баланс</b> составляет <b>{balance} рублей</b>.
'''
    update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_MANAGE_AREA


def area_fallback(update, context):
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    balance = user['balance']
    text = f'''
Здесь вы можете пополнить баланс, или обратиться в поддержку, по любым вопросам.
Ваш <b>текущий баланс</b> составляет <b>{balance} рублей</b>.
'''
    reply_markup = personal_area_keyboard()
    chat_id = update.callback_query.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return STEP_MANAGE_AREA


personal_area_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(personal_area, pattern='^' + 'Личный кабинет' + '$'),
    ],
    states={
        STEP_MANAGE_AREA: [
            payment_conv_handler,
            CallbackQueryHandler(start_support, pattern='^' + 'STEP_SUPPORT' + '$'),
        ],
        STEP_SAVE_ISSUE: [MessageHandler(Filters.text, save_issue)]
    },
    fallbacks=[
        MessageHandler(Filters.text & (~ Filters.command) | Filters.photo | Filters.video, area_fallback),
        CallbackQueryHandler(end_describing_area, pattern='^' + 'back_menu' + '$'),
        ],
    allow_reentry=True,
    per_chat=False
)
