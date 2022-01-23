from time import sleep
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

def type_reply(update: Update, context:CallbackContext, text: str, reply_markup=None) -> None:
    if reply_markup is not None:
        update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        update.message.reply_text(text)
    else:
        update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        update.message.reply_text(text, reply_markup)

    return

def longer_type_reply(update: Update, context:CallbackContext, text: str, reply_markup=None) -> None:
    if reply_markup is not None:
        update.message.reply_chat_action(ChatAction.TYPING, timeout=1)
        sleep(1)
        update.message.reply_text(text)
    else:
        update.message.reply_chat_action(ChatAction.TYPING, timeout=1)
        sleep(1)
        update.message.reply_text(text, reply_markup)

    return