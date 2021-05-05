# importa l'API de Telegram
from telegram.ext import Updater, CommandHandler

# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! My name is iGo")


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I have the following commands: /author, /go, /where.")


def author(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="My authors are Héctor and Ramon")


# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))

# engega el bot
updater.start_polling()
