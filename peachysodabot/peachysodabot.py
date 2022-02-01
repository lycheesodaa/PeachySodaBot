import os, logging, syl, certifi
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
from util.errorhandler import error_handler
from pymongo import MongoClient

global TOKEN
TOKEN = os.environ['bot_token']
global bot
bot = Bot(token=TOKEN)
MONGO = os.environ['mongo']

# initializing mongo client
client = MongoClient(MONGO, tlsCAFile=certifi.where())
db = client.peachysoda

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


RESTART, END, CONTINUE, NAME, CONFIRMED_NAME, GREETED, TESTLOOP, SYL = range(8)

# *=================================== STARTING ===================================*

def start(update: Update, context: CallbackContext) -> str:
    user = db.user

    skip2 = user.find_one({"username": 'sylviyay'})
    # skip2 = user.find_one({"username": 'wei_soooon'})
    skip = user.find_one({"username": update.effective_chat.username})
    # print(type(skip))

    if skip2 is not None:
        context.user_data['first_prompt'] = True
        update.message.reply_text(
            f"Welcome, {skip2['name']}.",
            reply_markup=ReplyKeyboardMarkup(
                [["Glad to be back :)", "Hehe"]], one_time_keyboard=True
            )
        )
        return SYL
    elif skip is not None:
        context.user_data['first_prompt'] = True
        update.message.reply_text(
            f"Welcome, {skip['name']}.",
            reply_markup=ReplyKeyboardMarkup(
                [["Hello!"]], one_time_keyboard=True
            )
        )
        return GREETED

    update.message.reply_text('Hi, nice to meet you!')

    # reply with chat action "Typing..."
    update.message.reply_chat_action(ChatAction.TYPING, timeout=0.5)
    sleep(0.5)
    update.message.reply_text('May I know your name?')

    return NAME

def confirm_name(update: Update, context: CallbackContext) -> str:
    name = update.message.text
    context.user_data['name'] = name

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
    username = update.effective_chat.username
    result = db.user.insert_one(
        {'name': name,
        'username': username,
        'user_id': update.effective_user.id,
        'chat_id': update.effective_chat.id}
    )
    # print(result)

    greeting = ""

    if username == "sylviyay":
    # if name == "weisoon" and username == "wei_soooon":
        greeting += (
            f'Hello {name}! I\'ve heard a lot about you from Wei Soon.'
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

    if username == "sylviyay":
        return SYL

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
            SYL: [syl.conversation],
            GREETED: [actions.conversation],
            TESTLOOP: [MessageHandler(Filters.text, test_loop)],
            END: [
                MessageHandler(Filters.regex('^Yes$'), bye),
                MessageHandler(Filters.regex('^No$'), restart)
            ],
            RESTART: [
                MessageHandler(Filters.regex('^Yes$'), start),
                MessageHandler(Filters.regex('^No$'), restart)
            ],
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

    # read MODE env variable, fall back to 'polling' when undefined
    mode = os.environ.get("MODE", "polling")

    if mode == 'webhook':
        # enable webhook
        updater.start_webhook(listen="0.0.0.0",
                            port=os.environ['PORT'],
                            url_path=TOKEN)
        updater.bot.setWebhook(os.environ['URL'] + TOKEN)
    else:
        # enable polling
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()