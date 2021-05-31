#bot.py

"""bot.py

The bot.py Python file provides the Telegram bot implementation that uses methods from the 'iGo.py' module
in order to create a simple interface for users to get information about driving ways of Barcelona as well as
getting the shortest path to a desired place of the city."""

import iGo
import collections
import threading
from datetime import datetime, date, timedelta
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from staticmap import StaticMap, CircleMarker, IconMarker, Line
import osmnx as ox

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 1000
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/c97072a3-3619-4547-84dd-f1999d2a3fec/download/transit_relacio_trams_format_long.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

Location = collections.namedtuple('Location', 'lng lat')
Congestion = collections.namedtuple('Congestion', 'actual future')

graph = None
igraph = None
highways = None
congestions = None
congestions_download_datetime = None


def __boot():
    """..."""

    global graph, igraph, highways, congestions, congestions_download_datetime
    # Get OSMnx graph from Barcelona city. Save it as a global variable.
    if not iGo.exists_graph(GRAPH_FILENAME):
        graph = iGo.download_graph(PLACE)
        iGo.save_graph(graph, GRAPH_FILENAME)
    else:
        graph = iGo.load_graph(GRAPH_FILENAME)
    # Download Barcelona Highways. Save them as a global variable.
    highways = iGo.download_highways(HIGHWAYS_URL)
    # Download Barcelona Highways' congestions. Save them as a global variable.
    congestions = iGo.download_congestions(CONGESTIONS_URL)
    # Set global variable 'congestions_download_datetime' to current datetime.
    current_datetime = datetime.now()
    congestions_download_datetime = current_datetime
    # Build the intelligent graph.
    igraph = iGo.build_igraph(graph, highways, congestions)
    filename = 'congestions.png'
    iGo.plot_igraph_congestions(igraph, filename, SIZE, current=True)
    print('Ready to go!')


__boot()


def __need_refresh():
    """..."""

    current_datetime = datetime.now()
    difference = current_datetime - congestions_download_datetime
    seconds = difference.total_seconds()
    if seconds > 300:
        return True
    return False


def __refresh_igraph():
    """..."""

    global congestions, igraph, congestions_download_datetime
    # Update Barcelona Highways' congestions. Save them as a global variable.
    congestions = iGo.download_congestions(CONGESTIONS_URL)
    # Update global variable 'congestions_download_datetime' to current datetime.
    current_datetime = datetime.now()
    congestions_download_datetime = current_datetime
    # Update the intelligent graph.
    igraph = iGo.build_igraph(graph, highways, congestions)

    filename = 'congestions.png'
    os.remove(filename)
    iGo.plot_igraph_congestions(igraph, filename, SIZE, current=True)


def start(update, context):
    """..."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is iGo, the Telegram bot to get wherever you want, by car, in Barcelona...  at the speed of light!\n" +
        "Use /help command to know more about me.")


def help(update, context):
    """..."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I have the following commands:\n" +
        "- /author: shows the author/s of the project.\n" +
        "- /where: shows a map with your current position.\n" +
        "- /go destination: shows a map with the shortest path from your location to a given destination in Barcelona.\n" +
        "- /congestions: shows a map with live congestions of Barcelona's driving ways.")


def author(update, context):
    """..."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="My authors are Héctor Fortuño and Ramon Ventura.")


def congestions(update, context):
    """..."""

    filename = 'congestions.png'
    if __need_refresh():
        __refresh_igraph()
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filename, 'rb'))


def where(update, context):  # imprime la localizacion de origin
    """..."""

    try:
        context.user_data['location']  # si ya tenemos una ubicacion, la imprimimos
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Here is your current location.')
        lng, lat = context.user_data['location'].lng, context.user_data['location'].lat
        if update.effective_chat.username == None:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please set a username to your Telegram account.')
            return 0
        filename = update.effective_chat.username + '.png'
        map = StaticMap(500, 500)
        map.add_marker(IconMarker((lng, lat), './origin.png', 10, 10))
        image = map.render()
        image.save(filename)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(filename, 'rb'))
        os.remove(filename)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='In case this is not your current position, send me your new location.')

    except:  # cuando no tenemos la ubicacion
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your current location.')




def current_location(update, context):
    """..."""

    location = update.message.location
    context.user_data['location'] = (Location) (location.longitude, location.latitude)
    where(update, context)



def __place_to_coordinates(update, context, place):
    """...."""

    try: int(place[0])
    except: # The given string is the name of the place.
        try: ox.geocoder.geocode(f"{place}, {PLACE}")
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Not a valid location!')
            return 0
        geo = ox.geocoder.geocode(f"{place}, {PLACE}")
        coordinates = (Location) (geo[1], geo[0])
        return coordinates
    separated = place.split()
    first = float(separated[0])
    second = float(separated[1])
    # Revise which float is the latitude (bigger value than longitude) and which one is the longitude.
    if first > second:
        coordinates = (Location) (second, first)
    else:
        coordinates = (Location) (first, second)

    return coordinates


def __pos(update, context):
    """..."""

    context.user_data['location'] = __place_to_coordinates(update, context, update.message.text[5:])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Location updated!')


def go(update, context):
    """..."""

    destination = update.message.text[4:]
    if len(destination) == 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your destination and try again.')
        return 0
    destination_coordinates = __place_to_coordinates(update, context, destination)

    try: context.user_data['location']
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your current location and try again.')
        return 0
    origin_coordinates = context.user_data['location']

    if __need_refresh():
        __refresh_igraph()

    try: iGo.__get_3_best_ipaths(igraph, origin_coordinates, destination_coordinates)
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Im sorry, I was not able to find a path to your destination.')
        return 0
    best_ipath_current, best_ipath_future, k_ipaths = iGo.__get_3_best_ipaths(igraph, origin_coordinates, destination_coordinates)
    if update.effective_chat.username == None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please set a username to your Telegram account.')
        return 0
    filename = update.effective_chat.username + '.png'
    iGo.plot_k_ipaths(igraph, best_ipath_current, best_ipath_future, k_ipaths, filename, SIZE)
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filename, 'rb'))
    os.remove(filename)

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
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('pos', __pos))

# engega el bot
updater.start_polling()
