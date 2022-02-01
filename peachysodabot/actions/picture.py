import requests, json
from time import sleep
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update, ChatAction
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CommandHandler
)

RESTART, END, CONTINUE, CHAT, CHOOSING_PIC, CUSTOM, RETRY, PICTURE = range(8)

url = "https://meme-api.herokuapp.com/gimme/"

def picture(update: Update, context: CallbackContext) -> str:

    picture_options = [
        [InlineKeyboardButton(text='Cute animals', callback_data='aww')],
        [InlineKeyboardButton(text='Dank memes', callback_data='dankmemes')],
        [InlineKeyboardButton(text='Random picture', callback_data='pics')],
        [InlineKeyboardButton(text='Custom', callback_data='custom')]
    ]

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "What kind of picture would you like to see?",
        reply_markup=InlineKeyboardMarkup(picture_options)
    )

    return CHOOSING_PIC

def custom(update: Update, context: CallbackContext) -> str:
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        "What do you have in mind?"
    )
    return CUSTOM

def subreddit(update: Update, context: CallbackContext) -> str:
    new_url = url
    is_callback = True
    if update.callback_query is not None:
        new_url += update.callback_query.data
    elif update.message is not None:
        new_url += update.message.text
        is_callback = False

    result = requests.get(new_url).text
    # print(result)
    data = json.loads(result)

    if "code" in data:
        context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        if is_callback:
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                "I couldn't find a picture for you :<\n"
                "Try something else?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Sure", callback_data='sure')],
                        [InlineKeyboardButton("Nah, it's okay", callback_data='nah')]
                    ], one_time_keyboard=True
                )
            )
        else:
            update.message.reply_text(
                "I couldn't find a picture for you :<\n"
                "Try something else?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Sure", callback_data='sure')],
                        [InlineKeyboardButton("Nah, it's okay", callback_data='nah')]
                    ], one_time_keyboard=True
                )
            )
        return RETRY

    elif data['nsfw'] == True or data['spoiler'] == True:
        context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
        sleep(0.5)
        if is_callback:
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                "The picture wasn't safe for work :(\n"
                "Try something else?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Sure", callback_data='sure')],
                        [InlineKeyboardButton("Nah, it's okay", callback_data='nah')]
                    ], one_time_keyboard=True
                )
            )
        else:
            update.message.reply_text(
                "The picture wasn't safe for work :(\n"
                "Try something else?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Sure", callback_data='sure')],
                        [InlineKeyboardButton("Nah, it's okay", callback_data='nah')]
                    ], one_time_keyboard=True
                )
            )
        return RETRY
    
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    if is_callback:
        update.callback_query.answer()
        update.callback_query.edit_message_text("You got it!")

        context.bot.sendPhoto(
            update.effective_chat.id,
            data['url'],
            caption=f"\"{data['title']}\"\n"
            f"By user {data['author']}, on r/{data['subreddit']}:",
        )
    else:
        update.message.reply_photo(
            data['url'],
            caption=f"\"{data['title']}\"\n"
            f"By user {data['author']}, on r/{data['subreddit']}:"
        )

    sleep(1)

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        "How'd you find it?"
    )

    return PICTURE

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

def _continue(update: Update, context: CallbackContext) -> str:
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    context.bot.send_message(
        update.effective_chat.id,
        "Well, are you still up for more?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True
        )
    )
    return CONTINUE

picture_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(picture, pattern='^2$')],
    states={
        CHOOSING_PIC: [
            CallbackQueryHandler(subreddit, pattern='^(?!custom).*$'),
            CallbackQueryHandler(custom, pattern='^custom$'),
        ],
        CUSTOM: [
            MessageHandler(Filters.text, subreddit),
        ],
        RETRY: [
            CallbackQueryHandler(picture, pattern=('^sure$')),
            CallbackQueryHandler(_continue, pattern=('^nah$')),
        ],
        PICTURE: [
            MessageHandler(Filters.text, _continue),
        ]
    },
    fallbacks={
        CommandHandler('start', restart),
        CommandHandler('bye', end),
    },
    map_to_parent={
        RESTART: RESTART, #!
        END: END,
        CONTINUE: CHAT
    }
)