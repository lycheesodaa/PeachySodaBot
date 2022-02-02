# PeachySodaBot
>A very peachy conversation bot.

This bot makes use of the [Telegram Bot API](https://github.com/python-telegram-bot/python-telegram-bot "Python-Telegram-Bot") to maintain a close-knit flow of conversation with you. 

It can send you inspirational quotes, pictures and memes from Reddit _(subject to a filter)_, tell you great jokes, and even...give you a *surprise*??

## Usage
To start a conversation with the bot, search for `@peachysodabot` on Telegram and enter `/start` to begin the conversation!

## Setup
Clone the repository into a directory of your choice:
```
git clone https://github.com/lycheesodaa/PeachySodaBot
```
Create a `.env` file under the `/peachysoda` directory. This file defines all the environment variables necessary for the app to run.

Necessary environment variables include:
- `bot_token`: Your Telegram bot API token
- `mongo`: URL to connect to MongoDB/Atlas
- `MODE`: Either *'polling'* or *'webhook'* depending on deployment state
- `URL`: Your Heroku URL (if necessary)

## Run
To run the application locally:
```
cd peachysodabot
python peachysodabot.py
```
Access the bot via Telegram or `https://t.me/peachysodabot` to start chatting.

## Misc
_This bot makes calls to external APIs, including calls to a personal MongoDB Atlas database and personal Google Drive storages which allow the app to function - that being said, the app will still function otherwise, but may not work as originally intended._
