import json, requests, traceback, html
from time import sleep
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from util.getChatId import get_chat_id
from actions.picture import picture_conv

RESTART, END, CONTINUE, CHAT, CHOOSING = range(5)

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
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=1)

    context.user_data['first_prompt'] = True

    quote_response = requests.get("https://api.quotable.io/random")
    data = json.loads(quote_response.text)

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
    
    return CONTINUE

def joke(update: Update, context: CallbackContext) -> str:
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=1)
    url = 'https://v2.jokeapi.dev/joke/Any'

    data = json.loads(requests.get(url).text)

    is_one_liner = True

    if data['type'] == "twopart":
        is_one_liner = False

    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "Here's the joke:\n"
        f"{data['joke'] if is_one_liner else data['setup']}"
    )

    if not is_one_liner:
        context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=1)
        sleep(1)
        context.bot.send_message(
            chat_id=get_chat_id(update, context),
            text=data['delivery']
        )
    
    sleep(1)
    
    context.bot.send_chat_action(chat_id=get_chat_id(update, context), action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    # ? possibly randomize this
    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text="I know, its a horrible joke.",
        reply_markup=ReplyKeyboardMarkup(
            [['Yeah XD', 'Nah it\'s fine']], one_time_keyboard=True
        )
    )

    return CONTINUE

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

def restart(update: Update, context: CallbackContext) -> str:
    update.message.reply_text(
        "Restart the conversation?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True
        )
    )
    return RESTART

def end(update: Update, context: CallbackContext) -> int:
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
        MessageHandler(Filters.text, options)
    ],
    states={
        CHOOSING: [
            CallbackQueryHandler(quote, pattern='^1$'),
            picture_conv,
            CallbackQueryHandler(joke, pattern='^3$'),
            CallbackQueryHandler(surprise, pattern='^4$'),
            CallbackQueryHandler(end, pattern='^5$'),
        ],
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
        RESTART: RESTART, #!
        END: END,
    }
)