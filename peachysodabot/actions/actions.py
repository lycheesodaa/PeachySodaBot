import json, requests, traceback, html
from time import sleep
from telegram import ParseMode, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from actions.picture import picture_conv
from util import emojis

RESTART, END, CONTINUE, CHAT, CHOOSING, SYL_CHOOSING = range(6)

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
    if update.effective_chat.username == 'sylviyay':
    # if update.effective_chat.username == 'wei_soooon':
        choices.insert(3, [InlineKeyboardButton(text='<--- Back', callback_data='back')])

    reply_markup = InlineKeyboardMarkup(choices)

    prompt = 'So what would you like me to do today?' if context.user_data['first_prompt'] == True else 'So what else would you like me to do today?'

    if update.callback_query is not None:
        context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            prompt,
            reply_markup=reply_markup
        )
    elif update.message is not None:
        update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        update.message.reply_text(
            prompt,
            reply_markup=reply_markup
        )

    context.user_data['first_prompt'] = False

    return CHOOSING

def syl_options(update: Update, context: CallbackContext) -> str:
    choices = [
        [InlineKeyboardButton(text='2/2/2022', callback_data='message')],
        [InlineKeyboardButton(text='Favourite photos <3', callback_data='fav')],
        [InlineKeyboardButton(text="Basic --->", callback_data='basic')],
        [InlineKeyboardButton(text='End', callback_data='end')]
    ]
    reply_markup = InlineKeyboardMarkup(choices)

    prompt = 'So what would you like me to do today?' if context.user_data['first_prompt'] == True else 'So what else would you like me to do today?'

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        prompt,
        reply_markup=reply_markup
    )
    
    return SYL_CHOOSING

def quote(update: Update, context: CallbackContext) -> str:
    quote_response = requests.get("https://api.quotable.io/random")
    data = json.loads(quote_response.text)

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "Here\'s a random quote to hopefully inspire you!\n\n"
        f"\"{data['content']}\"\n"
        f"- {data['author']}"
    )

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=1)
    sleep(1)
    context.bot.send_message(
        update.effective_chat.id,
        "Did you like the quote?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yeah!', 'I didn\'t like it.']], one_time_keyboard=True
        )
    )
    
    return CONTINUE

def joke(update: Update, context: CallbackContext) -> str:
    url = 'https://v2.jokeapi.dev/joke/Any'

    data = json.loads(requests.get(url).text)

    is_one_liner = True

    if data['type'] == "twopart":
        is_one_liner = False

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "Here's the joke:\n"
        f"{data['joke'] if is_one_liner else data['setup']}"
    )

    if not is_one_liner:
        context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=1)
        sleep(1)
        context.bot.send_message(
            update.effective_chat.id,
            text=data['delivery']
        )
    
    sleep(1)
    
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    # ? possibly randomize this
    context.bot.send_message(
        update.effective_chat.id,
        text="I know, its a horrible joke.",
        reply_markup=ReplyKeyboardMarkup(
            [['Yeah XD', 'Nah it\'s fine']], one_time_keyboard=True
        )
    )

    return CONTINUE

def surprise(update: Update, context: CallbackContext) -> str:
    update.callback_query.answer()
    update.callback_query.edit_message_text("***SURPRISE***")
    sleep(0.5)

    error = None

    try:
        value = context.error.__traceback__
    except AttributeError as e:
        error = e

    tb_list = traceback.format_exception(None, value=error, tb=error.__traceback__)
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

    context.bot.send_message(update.effective_chat.id, message, parse_mode=ParseMode.HTML)
    sleep(1.5)

    context.bot.send_message(update.effective_chat.id, emojis.laughing, parse_mode=ParseMode.MARKDOWN_V2)
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        text="I was kidding ;)"
    )
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        text="Did you get a heart attack?",
        reply_markup=ReplyKeyboardMarkup(
            [['!!?!?!', 'Nah, saw this coming :)']], one_time_keyboard=True
        )
    )

    return CONTINUE

def continue_chat(update: Update, context: CallbackContext) -> str:
    if update.message.text == '!!?!?!':
        context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        context.bot.send_message(update.effective_chat.id, "HAHAHA!")

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
        CallbackQueryHandler(options, pattern='^basic$')
    ],
    states={
        CHOOSING: [
            CallbackQueryHandler(quote, pattern='^1$'),
            picture_conv,
            CallbackQueryHandler(joke, pattern='^3$'),
            CallbackQueryHandler(surprise, pattern='^4$'),
            CallbackQueryHandler(end, pattern='^5$'),
            CallbackQueryHandler(syl_options, pattern='^back$')
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
        SYL_CHOOSING:CHOOSING,
        RESTART: RESTART,
        END: END,
    }
)