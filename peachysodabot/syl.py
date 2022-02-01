import certifi, os
from secrets import randbelow
from time import sleep
from telegram import ParseMode, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction, parsemode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from util import emojis
from actions import actions
from pymongo import MongoClient

MONGO = os.environ['mongo']

client = MongoClient(MONGO, tlsCAFile=certifi.where())
db = client.peachysoda

RESTART, END, CONTINUE, CHAT, CHOOSING, MESSAGE_READ = range(6)

def options(update: Update, context: CallbackContext) -> str:
    choices = [
        [InlineKeyboardButton(text='2/2/2022', callback_data='message')],
        [InlineKeyboardButton(text='Favourite photos <3', callback_data='fav')],
        [InlineKeyboardButton(text="Basic --->", callback_data='basic')],
        [InlineKeyboardButton(text='End', callback_data='end')]
    ]
    reply_markup = InlineKeyboardMarkup(choices)

    prompt = 'So what would you like me to do today?' if context.user_data['first_prompt'] == True else 'So what else would you like me to do today?'

    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text(
        prompt,
        reply_markup=reply_markup
    )

    context.user_data['first_prompt'] = False

    return CHOOSING

def message(update: Update, context: CallbackContext) -> str:
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "Here, Wei Soon has a message for you:"
    )

    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        os.environ.get('my_message', 'error'),
        parse_mode=ParseMode.HTML
    )
    context.bot.send_message(update.effective_chat.id, emojis.heart)

    context.bot.send_message(
        update.effective_chat.id,
        "Let me know when you're done reading :)",
        reply_markup=ReplyKeyboardMarkup(
            [["I'm done :')"]], one_time_keyboard=True
        )
    )
    
    return MESSAGE_READ

def favourites(update: Update, context: CallbackContext) -> str:
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "Loading image...please wait a moment."
    )

    data = db.photo.find()[randbelow(db.photo.estimated_document_count())]

    if data is None:
        context.bot.send_message(
            update.effective_chat.id,
            "An error occurred somewhere. Please ask Wei Soon to fix it :(\n\n"
            "Send me something to continue... ><"
        )
        return CONTINUE

    elif "mp4" in data['fileName']:
        context.bot.send_animation(
            update.effective_chat.id,
            data['webContentLink'],
            caption = data['description']
        )
    else:
        context.bot.send_photo(
            update.effective_chat.id,
            data['webContentLink'],
            caption = data['description']
        )

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        "Did you like it?",
        reply_markup=ReplyKeyboardMarkup(
            [["Yes!", "YESSSS"]], one_time_keyboard=True
        )
    )

    return CONTINUE

def continue_chat(update: Update, context: CallbackContext) -> str:
    # print(update.message.text)
    if update.message.text == 'YESSSS':
        context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        context.bot.send_message(update.effective_chat.id, "Wei Soon will be glad!")

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        text='Would you like me to continue?',
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)
    )
    return CHAT

def restart(update: Update, context: CallbackContext) -> str:
    update.message.reply_text(
        "Restart the conversation?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True
        )
    )
    return RESTART

def end(update: Update, context: CallbackContext) -> int:
    if update.callback_query is not None:
        update.callback_query.answer()
        update.callback_query.edit_message_text(emojis.smiley_tears)
        context.bot.send_message(
            update.effective_chat.id,
            "Really end?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True
            )
        )
    elif update.message is not None:
        update.message.reply_text(
            "Really end?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True
            )
        )
    
    return END

# * substitute main function for being called in peachysodabot.py
conversation = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^High Five!$'), options),
        MessageHandler(Filters.text, options),
        CallbackQueryHandler(options, pattern='^back$'),
    ],
    states={
        CHOOSING: [
            CallbackQueryHandler(message, pattern='^message$'),
            CallbackQueryHandler(favourites, pattern='^fav$'),
            actions.conversation,
            CallbackQueryHandler(end, pattern='^end$'),
        ],
        MESSAGE_READ: [MessageHandler(Filters.text, options)],
        CONTINUE: [MessageHandler(Filters.text, continue_chat)],
        CHAT: [
            MessageHandler(Filters.regex('^Yes$'), options),
            MessageHandler(Filters.regex('^No$'), end),
        ]
    },
    fallbacks={
        CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
        CommandHandler('start', restart),
        CommandHandler('bye', end),
    },
    map_to_parent={
        RESTART: RESTART,
        END: END,
    }
)