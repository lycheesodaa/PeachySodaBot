import json, requests, html, traceback
from time import sleep
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from credentials import bot_token
from util.getChatId import get_chat_id
from peachysodabot import END
import picture, surprise

CHOOSING, QUOTE, CONTINUE, CHAT, RESTART = range(5)

def options(update: Update, context: CallbackContext) -> str:
    choices = [
        [InlineKeyboardButton(text='Send me a quote', callback_data='1')],
        [InlineKeyboardButton(text='Send me a picture', callback_data='2')],
        [InlineKeyboardButton(text='Tell me a joke', callback_data='3')],
        [
            InlineKeyboardButton(text='Surprise..?', callback_data='4'),
            InlineKeyboardButton(text='End', callback_data='5')
        ]
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

def quote(update: Update, context: CallbackContext) -> str:
    context.user_data['first_prompt'] = True

    quote_response = requests.get("https://api.quotable.io/random")
    data = json.loads(quote_response.text)

    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "Here\'s a random quote to hopefully inspire you!\n\n"
        f"\"{data['content']}\"\n"
        f"- {data['author']}"
    )

    context.bot.send_chat_action(get_chat_id(update, context), action=ChatAction.TYPING, timeout=1)
    sleep(1)
    context.bot.send_message(
        get_chat_id(update, context),
        "Did you like the quote?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yeah!', 'I didn\'t like it.']], one_time_keyboard=True
        )
    )
    
    return QUOTE

def joke(update: Update, context: CallbackContext) -> str:
    # TODO

    return CONTINUE

def continue_chat(update: Update, context: CallbackContext) -> str:
    choices = [['Yes', 'No']]
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text='Would you like me to continue?',
        reply_markup=ReplyKeyboardMarkup(choices, one_time_keyboard=True)
    )
    return CHAT


def restart(update: Update, context: CallbackContext) -> int:
    return RESTART

def end(update: Update, context: CallbackContext) -> int:
    return END


# * substitute main function for being called in peachysodabot.py
conversation = ConversationHandler(
    entry_points=[(MessageHandler(Filters.regex('^High Five!$'), options))],
    states={
        CHOOSING: [
            CallbackQueryHandler(quote, pattern='^1$'),
            CallbackQueryHandler(joke, pattern='^3$'),
            CallbackQueryHandler(surprise.surprise, pattern='^4$'),
            CallbackQueryHandler(end, pattern='^5$'),
            picture.picture_conv,
        ],
        QUOTE: [
            MessageHandler(Filters.text, continue_chat),
        ],
        CONTINUE: [continue_chat],
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