import datetime

from telegram import LabeledPrice, ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    PreCheckoutQueryHandler,
)

from bot.db import DBase
from bot.keyboards import (
    STEP_AFTER_PAYMENT,
    STEP_INVOICE,
    STEP_MANAGE_AREA,
    STEP_PAYMENT_BACK_AREA,
    STEP_PAYMENT_BACK_FILTER,
    STEP_PAYMENT_DONE,
    STEP_PRECHECKOUT,
    STEP_SHOW_CV,
    after_success_keyboard,
    back_payment_keyboard,
    choose_amount_keyboard,
    personal_area_keyboard,
    show_cv_keyboard,
)
from bot.utils import print_cv

dbase = DBase()


def choose_invoice_amount(update, context):
    update.callback_query.answer()
    if update.callback_query.data == 'pay_balance_filter':
        context.user_data['payment_from'] = 'filter'
    elif update.callback_query.data == 'pay_balance_area':
        context.user_data['payment_from'] = 'area'
    text = 'Пожалуйста, выберите сумму для пополнения'
    reply_markup = choose_amount_keyboard(context.user_data['payment_from'])
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_INVOICE


def send_payment_invoice(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    for_show_user_id = user['filter']['show_cv_tg_id']['showed_tg_id']
    balance = user['balance']
    if update.callback_query.data == 'payment_back_filter':
        text = print_cv(tg_id, for_show_user_id)
        reply_markup = show_cv_keyboard(tg_id)
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return STEP_PAYMENT_BACK_FILTER
    elif update.callback_query.data == 'payment_back_area':
        text = f'''
Здесь вы можете пополнить баланс, или обратиться в поддержку, по любым вопросам.
Ваш <b>текущий баланс</b> составляет <b>{balance} рублей</b>.
'''
        reply_markup = personal_area_keyboard()
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return STEP_PAYMENT_BACK_AREA
    amount = int(update.callback_query.data[0:3])
    chat_id = update.callback_query.message.chat.id
    title = "Пополнение баланса."
    description = f"Пополнение баланса на сумму {amount} рублей."
    # select a payload just for you to recognize its the donation from your bot
    payload = "hh_bot"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = "381764678:TEST:31486"
    currency = "RUB"
    # price in dollars
    price = amount
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Оплата", price * 100)]
    reply_markup = back_payment_keyboard(amount)
    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        chat_id, title,
        description,
        payload,
        provider_token,
        currency,
        prices,
        reply_markup=reply_markup
        # need_phone_number=True,
        # send_phone_number_to_provider=True
    )
    return STEP_PRECHECKOUT


def successful_payment_callback(update, context):
    tg_id = update.effective_user.id
    amount = int(update.message.successful_payment.total_amount) / 100
    invoice_id = update.message.successful_payment.provider_payment_charge_id
    now = datetime.datetime.now()
    payment_details = {'amount': amount, 'datetime': now, 'invoice_id': invoice_id}
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    new_balance = user['balance'] + amount
    dbase.db_client.users.update_one({'_id': user['_id']}, {'$set': {'balance': new_balance}})
    dbase.db_client.users.update_one({'_id': user['_id']}, {'$push': {'payments': payment_details}})
    text = f"Платеж успешно зачислен! Ваш текущий баланс составляет {new_balance} рублей!"
    reply_markup = after_success_keyboard(context.user_data['payment_from'])
    update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return STEP_AFTER_PAYMENT


def payment_invoice_back(update, context):
    update.callback_query.answer()
    text = 'Пожалуйста, выберите сумму для пополнения'
    reply_markup = choose_amount_keyboard(context.user_data['payment_from'])
    chat_id = update.callback_query.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return STEP_INVOICE


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'hh_bot':
        query.answer(ok=False, error_message="Проблемы с оплатой, обратитесь к разработчику")
    else:
        query.answer(ok=True)
    return STEP_PAYMENT_DONE
    # выдавать что то по таймауту?


def move_after_payment(update, context):
    update.callback_query.answer()
    tg_id = update.effective_user.id
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    for_show_user_id = user['filter']['show_cv_tg_id']['showed_tg_id']
    balance = user['balance']
    if update.callback_query.data == 'success_to_filter':
        text = print_cv(tg_id, for_show_user_id)
        reply_markup = show_cv_keyboard(tg_id)
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return STEP_PAYMENT_BACK_FILTER
    elif update.callback_query.data == 'success_to_area':
        text = f'''
Здесь вы можете пополнить баланс, или обратиться в поддержку, по любым вопросам.
Ваш <b>текущий баланс</b> составляет <b>{balance} рублей</b>.
'''
        reply_markup = personal_area_keyboard()
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return STEP_PAYMENT_BACK_AREA
    else:
        text = 'Пожалуйста, выберите сумму для пополнения'
        reply_markup = choose_amount_keyboard(context.user_data['payment_from'])
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return STEP_INVOICE


pay_balance_patterns = (
    '^' + 'pay_balance_filter' + '$|'
    '^' + 'pay_balance_area' + '$'
)


def payment_fallback(update, context):
    text = 'Пожалуйста, выберите сумму для пополнения'
    reply_markup = choose_amount_keyboard(context.user_data['payment_from'])
    chat_id = update.callback_query.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return STEP_INVOICE


payment_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(choose_invoice_amount, pattern=pay_balance_patterns),
    ],
    states={
        STEP_INVOICE: [CallbackQueryHandler(send_payment_invoice)],
        STEP_PRECHECKOUT: [
            PreCheckoutQueryHandler(precheckout_callback),
            CallbackQueryHandler(payment_invoice_back, pattern='^' + 'back_payment' + '$')
        ],
        STEP_PAYMENT_DONE: [MessageHandler(Filters.successful_payment, successful_payment_callback)],
        STEP_AFTER_PAYMENT: [CallbackQueryHandler(move_after_payment)]
    },
    fallbacks=[
        MessageHandler(Filters.text & (~ Filters.command) | Filters.photo | Filters.video, payment_fallback),
        # CallbackQueryHandler(end_describing_filter, pattern='^' + str(END) + '$'),
    ],
    map_to_parent={
        STEP_PAYMENT_BACK_FILTER: STEP_SHOW_CV,
        STEP_PAYMENT_BACK_AREA: STEP_MANAGE_AREA
    },
    allow_reentry=True,
    per_chat=False
)
