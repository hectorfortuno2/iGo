import iGo
import threading
import collections
from datetime import datetime, date


# para usar el timer
# importa l'API de Telegram

# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start

import random
import os

from staticmap import StaticMap, CircleMarker

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 1000
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/c97072a3-3619-4547-84dd-f1999d2a3fec/download/transit_relacio_trams_format_long.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

Location = collections.namedtuple('Location', 'lng lat')
Congestion = collections.namedtuple('Congestion', 'actual future')

graph = None
iGraph = None
highways = None
congestions = None
congestions_download_datetime = None
# origin = (0, 0) -> user.data


def __boot():
    global graph, iGraph, highways, congestions, congestions_download_datetime

    if not iGo.exists_graph(GRAPH_FILENAME):
        graph = iGo.download_graph(PLACE)
        iGo.save_graph(graph, GRAPH_FILENAME)
    else:
        graph = iGo.load_graph(GRAPH_FILENAME)

    highways = iGo.download_highways(HIGHWAYS_URL)
    congestions = iGo.download_congestions(CONGESTIONS_URL)
    current_datetime = datetime.now()
    congestions_download_datetime = current_datetime

    iGo.build_igraph(graph, highways, congestions)
    current_datetime = datetime.now()
    difference = current_datetime - congestions_download_datetime
    print(difference.minute)


__boot()


def need_refresh():
    current_datetime = datetime.now()
    difference = current_datetime - congestions_download_datetime
    print(difference.minute)


def refresh_info(update, context):
    # actualizamos las congestiones y el igraph
    congestions = iGo.download_congestions(CONGESTIONS_URL)
    iGo.build_igraph(graph, highways, congestions)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is iGo")


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I have the following commands: /author, /go, /where, /congestions.")


def author(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="My creators are Héctor and Ramon")


def congestions(update, context):
    fitxer = "%d.png" % random.randint(1000000, 9999999)

    iGo.plot_congestions(highways, congestions, fitxer, SIZE)

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(fitxer, 'rb'))
    os.remove(fitxer)


def where(update, context):  # imprime la localizacion de origin
    try:
        if origin != (0, 0):  # si ya tenemos una ubicacion, la imprimimos
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Here is your current location')

            lat, lon = origin[0], origin[1]
            fitxer = "%d.png" % random.randint(1000000, 9999999)
            mapa = StaticMap(500, 500)
            mapa.add_marker(CircleMarker((lon, lat), 'red', 10))
            # icon marker
            imatge = mapa.render()
            imatge.save(fitxer)
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=open(fitxer, 'rb'))
            os.remove(fitxer)

            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='In case this is not your current position, send me your location.')

        else:  # cuando no tenemos la ubicacion
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please send me your location')
    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')


def current_location(update, context):
    try:
        user_location = update.message.location
        global origin
        origin = (user_location.latitude, user_location.longitude)
        where(update, context)

    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')


def pos(update, context):
    global origin
    origin = iGo.formatted_address(update.message.text[5:])
    print(origin[0])
    print(origin[1])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Position updated')


def go(update, context):
    global origin
    first = True
    while origin == (0, 0):
        if first:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please send me your location')
            first = False

    # localizacion proporcionada por el usuario (eliminamos el /go y nos quedamos con el resto)
    destination = update.message.text[4:]
    # descargar otra vez la info? declarar como variables globales? def __innit__?
    igraph = build_igraph(graph, highways, congestions)
    alternative_ipaths_list = iGo.get_k_shortest_paths_with_itime(
        igraph, origin, destination, 3, True)
    best_ipath = get_shortest_path_with_itime(igraph, origin, destination, True)

    iGo.plot_k_ipaths(igraph, best_ipath, alternative_ipaths_list, 'ipath.png', SIZE, True)
    # caminos (pintar de gris los dos mas lentos y del color de la congestion el rapido?)


# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(MessageHandler(Filters.location, current_location))
dispatcher.add_handler(CommandHandler('congestions', congestions))
# dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('pos', pos))

# engega el bot
updater.start_polling()
