from time import sleep
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ChatAction
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
    CallbackQueryHandler,
)
from credentials import bot_token, bot_user_name, URL
from util.getChatId import get_chat_id

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

END = range(5)

def test() -> str:
    return 'Hello Sylvia! I\'ve heard a lot about you from Wei Soon.'

conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(test, pattern='^1$'),
            CallbackQueryHandler(test, pattern='^2$'),
            CallbackQueryHandler(test, pattern='^3$'),
            CallbackQueryHandler(test, pattern='^4$'),
        ],
        states={

        },
        fallbacks={

        },
        map_to_parent={
            END: END,
        }
    )