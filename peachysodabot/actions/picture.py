import requests, json
from time import sleep
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardMarkup, Update, ChatAction
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)
from util.getChatId import get_chat_id
from actions import CONTINUE

url = "https://meme-api.herokuapp.com/gimme"
CHOOSING_PIC, CUSTOM, RETRY = range(3)

def picture(update: Update, context: CallbackContext) -> str:

    picture_options = [
        [InlineKeyboardButton('Cute animals', callback_data='aww')],
        [InlineKeyboardButton('Dank memes', callback_data='dankmemes')],
        [InlineKeyboardButton('Random picture', callback_data='pics')],
        [InlineKeyboardButton('Custom', callback_data='custom')]
    ]

    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "What kind of picture would you like to see?",
        reply_markup=[
            InlineKeyboardMarkup(picture_options)
        ]
    )

    return CHOOSING_PIC

def custom(update: Update, context: CallbackContext) -> str:
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "What do you have in mind?"
    )
    return CUSTOM

def subreddit(update: Update, context: CallbackContext) -> str:
    new_url = url
    if update.callback_query is not None:
        new_url += update.callback_query.message.text
    elif update.message is not None:
        new_url += update.message.text

    data = json.loads(requests.get(new_url).text)

    if data['code'] == 404:
        context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            "I couldn't find a picture for you :<\n"
            "Try something else?",
            reply_markup=ReplyKeyboardMarkup(
                [['Okay', 'Nah it\'s fine']], one_time_keyboard=True
            )
        )
        return RETRY
    elif data['nsfw'] == True or data['spoiler'] == True:
        context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            "Not gonna let you search for that >:(\n"
            "Try something else?",
            reply_markup=ReplyKeyboardMarkup(
                [['Okay', 'Nah it\'s fine']], one_time_keyboard=True
            )
        )
        return RETRY
    
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        f"\"{data['title']}\""
        f"By user {data['author']}, on r/{data['subreddit']}:",
    )
    update.callback_query.edit_message_media(media=InputMediaPhoto(data['url']))

    return CONTINUE

def end(update: Update, context: CallbackContext) -> str:
    return CONTINUE

picture_conv = ConversationHandler(
    entry_points=[(CallbackQueryHandler(picture, pattern='^2$'))],
    states={
        CHOOSING_PIC: [
            CallbackQueryHandler(subreddit, pattern='^(?!custom).*$'),
            CallbackQueryHandler(custom, pattern='^custom$'),
        ],
        CUSTOM: [
            MessageHandler(Filters.text, subreddit),
        ],
        RETRY: [
            MessageHandler(Filters.regex('^Okay$'), picture),
            MessageHandler(Filters.regex('^Nah$'), end),
        ]
    },
    map_to_parent={
        CONTINUE: CONTINUE
    }
)