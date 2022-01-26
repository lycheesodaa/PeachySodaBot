import os, logging
from time import sleep
from typing import Dict
from telegram import ReplyKeyboardMarkup, Update, ChatAction, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
)
from actions import actions
import syl, credentials
from util.getChatId import get_chat_id
from util.errorhandler import error_handler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

global TOKEN
TOKEN = credentials.bot_token
global bot
bot = Bot(token=TOKEN)

RESTART, END, CONTINUE, NAME, CONFIRMED_NAME, GREETED, TESTLOOP= range(7)

# *=================================== STARTING ===================================*

def start(update: Update, context: CallbackContext) -> str:
    # storing the username, find a use later
    username = update.message.from_user.username
    logger.info("Username: %s", username)
    context.user_data['username'] = username

    user_id = update.message.from_user.id
    logger.info("User ID: %s", user_id)
    context.user_data['user_id'] = user_id

    # chat_id = get_chat_id(update, context)

    update.message.reply_text('Hi, nice to meet you!')
    if username == 'wei_soooon':
        update.message.reply_text('Send something')
        context.user_data['first_prompt'] = True
        return GREETED
    # reply with chat action "Typing..."
    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text('May I know your name?')

    return NAME

def confirm_name(update: Update, context: CallbackContext) -> str:
    name = update.message.text
    context.user_data['name'] = name

    # context.bot.send_chat_action(action=ChatAction.TYPING, timeout=0.5)
    options = [['Yes', 'No']]

    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text(
        'Can I call you ' + name + '?',
        reply_markup=ReplyKeyboardMarkup(
            options, one_time_keyboard=True, input_field_placeholder='Is this your name?'
        ),
    )

    return CONFIRMED_NAME

def wrong_name(update: Update, context: CallbackContext) -> str:
    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text("What's your name?")

    return NAME

def greet(update: Update, context: CallbackContext) -> str:
    name = context.user_data['name']
    username = context.user_data['username']

    greeting = ""

    if name == "Sylvia" and username == "sylviyay":
    # if name == "weisoon" and username == "wei_soooon":
        greeting += (
            'Hello Sylvia! I\'ve heard a lot about you from Wei Soon.'
        )
    else:
        greeting += (
            f'That\'s a lovely name. Once again, hello, {name}.'
        )

    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text(greeting)

    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text(
        'Gimme a high five!',
        reply_markup=ReplyKeyboardMarkup(
            [['High Five!']], one_time_keyboard=True,
        )
    )

    context.user_data['first_prompt'] = True

    return GREETED

def restart(update: Update, _: CallbackContext) -> str:
    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text(
        'Well then, gimme another high five!',
        reply_markup=ReplyKeyboardMarkup(
            [['High Five!']], one_time_keyboard=True,
        )
    )

    return GREETED

def bye(update: Update, _: CallbackContext) -> int:
    update.message.reply_chat_action(ChatAction.TYPING, timeout=1)
    sleep(1)
    update.message.reply_text('Well then, it was nice talking to you.')

    update.message.reply_chat_action(ChatAction.TYPING, timeout=1)
    sleep(1)
    update.message.reply_text('See you again soon!')

    return ConversationHandler.END

def test_loop(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'You have reached the test loop.\n'
        'The bot will now stop. '
        'Restart it again with /start.'
    )

    return ConversationHandler.END

# *=================================== MISCELLANEOUS ===================================*

def facts_to_str(user_data: Dict[str, str]) -> str:
    # """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])

def show_data(update: Update, context: CallbackContext) -> None:
    # """Display the gathered info."""
    update.message.reply_text(
        f"This is what you already told me: {facts_to_str(context.user_data)}"
    )

# *=================================== MAIN ===================================*

def main() -> None:
    # """Run the bot."""
    persistence = PicklePersistence(filename='peachysodabot')
    updater = Updater(TOKEN, persistence=persistence)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text, confirm_name)],
            CONFIRMED_NAME: [
                MessageHandler(Filters.regex('^Yes$'), greet),
                MessageHandler(Filters.regex('^No$'), wrong_name),
            ],
            GREETED: [actions.conversation],
            TESTLOOP: [MessageHandler(Filters.text, test_loop)],
            END: [
                MessageHandler(Filters.regex('^Yes$'), bye),
                MessageHandler(Filters.regex('^No$'), restart)
            ], #!
            RESTART: [
                MessageHandler(Filters.regex('^Yes$'), start),
                MessageHandler(Filters.regex('^No$'), restart)
            ], #!
            # LOCATION: [
            #     MessageHandler(Filters.location, location),
            #     CommandHandler('skip', skip_location),
            # ],
            # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[
            CommandHandler('bye', bye),
            CommandHandler('start', start),
        ],
        name="my_conversation",
        # persistent=True,
    )

    dispatcher.add_handler(conv_handler)

    show_data_handler = CommandHandler('show_data', show_data)
    dispatcher.add_handler(show_data_handler)
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    # updater.start_polling()

    # read MODE env variable, fall back to 'polling' when undefined
    mode = os.environ.get("MODE", "polling")

    if mode == 'webhook':
        # enable webhook
        updater.start_webhook(listen="0.0.0.0",
                            port=3978,
                            url_path=TOKEN)
        updater.bot.setWebhook(f'https://example.com/svc/{TOKEN}')
    else:
        # enable polling
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()