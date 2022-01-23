import json, html, traceback
from time import sleep
from telegram import ReplyKeyboardMarkup, Update, ChatAction
from telegram.ext import CallbackContext
from util.getChatId import get_chat_id
from actions import CONTINUE

def surprise(update: Update, context: CallbackContext) -> str:
    try:
        update.message.reply_to_message("***SURPRISE***")
    except:
        value = context.error
        tb = context.error.__traceback__

    tb_list = traceback.format_exception(None, value=value, tb=tb)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    update.callback_query.answer()
    update.callback_query.edit_message_text(message)

    context.bot.send_dice(get_chat_id(update,context), dice='bowling')
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text="I was kidding ;)"
    )
    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text="Did you get a heart attack?",
        reply_markup=ReplyKeyboardMarkup(
            [['!!?!?!', 'Nah, saw this coming :)']], one_time_keyboard=True
        )
    )

    return CONTINUE