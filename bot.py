# importa l'API de Telegram


# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start

import random
import os

from staticmap import StaticMap, CircleMarker

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


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


def where(update, context):
    try:
        lat, lon = update.message.location.latitude, update.message.location.longitude
        fitxer = "%d.png" % random.randint(1000000, 9999999)
        mapa = StaticMap(500, 500)
        mapa.add_marker(CircleMarker((lon, lat), 'blue', 10))
        imatge = mapa.render()
        imatge.save(fitxer)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(fitxer, 'rb'))
        os.remove(fitxer)
    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')


# def go():
    # necesitamos leer el destino del usuario, una vez leido pedimos que nos
    # mande su ubicacion mediante la funcion /where


# def pos():

    # declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(MessageHandler(Filters.location, where))

# engega el bot
updater.start_polling()

"""
PREGUNTES:
idioma
pep8

TODO:
comandes bot (go (desti argument comanda¿?, obtencio de la localitzacio), where, pos)

"""
