# bot.py

"""bot.pry
The bot.py file """

# authors: Héctor Fortuño and Ramon Ventura

import iGo
import threading
import collections
from datetime import datetime, date, timedelta
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 1000
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/c97072a3-3619-4547-84dd-f1999d2a3fec/download/transit_relacio_trams_format_long.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

# Tuple used to represent a location with longitude and latitude coordinates.
Location = collections.namedtuple('Location', 'lng lat')
# Tuple used to represent the current and future congestion of a highway.
Congestion = collections.namedtuple('Congestion', 'actual future')

# Global variables declaration.
graph = None
igraph = None
highways = None
congestions = None
congestions_download_datetime = None


def __boot():
    """Private method that boots our bot. The OSMnx graph is downloaded and so
    are the highways and congestions. Also, igraph is created."""

    global graph, iGraph, highways, congestions, congestions_download_datetime
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
    iGo.build_igraph(graph, highways, congestions)
    print('Ready to work!')


__boot()


def __need_refresh():
    """Boolean type private method that returns True if a refresh in our data is needed.
    Otherwise, returns False."""

    # Find the current time.
    current_datetime = datetime.now()
    # Substract the time when the last refresh was done to the current one.
    difference = current_datetime - congestions_download_datetime
    seconds = difference.total_seconds()
    # If the difference exceeds a total of 5 minutes, return True. Otherwise, return False.
    if seconds > 300:
        return True
    return False


def __refresh_igraph():
    """Private method that refreshes the data used by re-downloading the real-time
    congestions and building again an igraph."""

    global congestions, igraph, congestions_download_datetime
    # Update Barcelona Highways' congestions. Save them as a global variable.
    congestions = iGo.download_congestions(CONGESTIONS_URL)

    # Update global variable 'congestions_download_datetime' to current datetime.
    current_datetime = datetime.now()
    congestions_download_datetime = current_datetime
    # Update the intelligent graph.
    igraph = iGo.build_igraph(graph, highways, congestions)

    # Plots and stores the real-time congestions once updated.
    filename = 'congestions.png'
    iGo.plot_congestions(highways, congestions, filename, SIZE)


def start(update, context):
    """Method that welcomes the user."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is iGo, the Telegram bot to get wherever you want in Barcelona...  at the speed of light!")


def help(update, context):
    """Method that displays all the available commands in the bot."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I have the following commands: /author, /go, /where, /congestions")


def author(update, context):
    """Method that shows the bot's creators."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="My authors are Héctor Fortuño and Ramon Ventura.")


def congestions(update, context):
    """Method that sends the user an image of the real-time congestions in different colors."""

    filename = 'congestions.png'
    # Checks if the congestions need to be updated.
    if __need_refresh():
        __refresh_igraph()
    # Image saved in __refresh_igraph method is sent to the user.
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filename, 'rb'))


def where(update, context):
    """Method that sends an image to the user of his current location."""

    try:  # QUITAR TRY EXCEPT?
        # Check if we already have the location of the user, if this is the case,
        # an image is sent.
        try:
            context.user_data['location']
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Here is your current location.')

            lng, lat = context.user_data['location'].lng, context.user_data['location'].lat
            filename = update.effective_chat.username + '.png'

            # Create a map and place a marker in user's location.
            map = StaticMap(500, 500)
            mapa.add_marker(CircleMarker((lng, lat), 'red', 10))  # AÑADIR MARCADOR NUEVO PNG
            imatge = mapa.render()
            imatge.save(filename)
            # Send the image
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=open(filename, 'rb'))
            # os.remove(filename) DESCOMENTAR!!!

            # In order to make sure the user is satisfied, we ask again for the
            # location in case the user didn't update it properly.
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='In case this is not your current position, send me your location.')

        except:
            # In case of not having the location, the user is asked to send it.
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please send me your current location.')
    except Exception as e:
        print(e)
        print('where')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')


def current_location(update, context):
    """Method that stores and updates the user's current location."""

    try:  # QUITAR TRY???
        # Obtain the location of the user.
        location = update.message.location
        # Store it.
        context.user_data['location'] = (Location)(location.longitude, location.latitude)
        # Call the 'where' method in order to proceed with the new location.
        where(update, context)

    except Exception as e:
        print(e)
        print('current location')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')


def __place_to_coordinates(place):
    """Private method that converts the name of a place into coordinates. Returns
    a location."""

    try:
        # Checks if the message given by the user are coordinates.
        int(place[0])
    except:
        # In case the given string is the name of the place, we convert it into coordinates.
        geo = ox.geocoder.geocode(f"{place}, {PLACE}")
        coordinates = (Location)(geo.lng, geo.lat)
        return coordinates

    # Convert string of coordinates into a tuple of floats.
    separated = place.split()
    first = float(separated[0])
    second = float(separated[1])
    # Revise which float is the latitude (bigger value than longitude) and which one is the longitude.
    if first > second:
        coordinates = (Location)(second, first)
    else:
        coordinates = (Location)(first, second)
    return coordinates


def __pos(update, context):
    """Private method that allows the user to manually change its current
    location by sending the name of a place or a pair of coordinates."""

    # In case the user sends the name of a place, convert it into coordinates.
    context.user_data['location'] = __place_to_coordinates(update.message.text[5:])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Location updated!')


def go(update, context):
    """Method that sends an image to the user of the 3 shortest paths to the destination specified."""

    # TIEMPO DEL MEJOR PATH???

    destination = update.message.text[4:]
    # Convert the destination of the user into coordinates.
    destination_coordinates = __place_to_coordinates(destination)

    try:
        # Check if a location was already stored.
        context.user_data['location']
    except:
        # If a location wasn't already stored, ask for a location.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your current location and try again.')
        return 0

    # Check if our data needs to update.
    if __need_refresh():
        __refresh_igraph()

    origin_coordinates = context.user_data['location']
    # Find the 3 best paths to the destination.
    best_ipath_current, best_ipath_future, k_ipaths = iGo.__get_3_best_ipaths(
        igraph, origin_coordinates, destination_coordinates)
    filename = update.effective_chat.username + '.png'
    # Plot and send the user the 3 best paths, highliting the best one in color.
    plot_k_ipaths(igraph, best_ipath_current, best_ipath_future, k_ipaths, filename, SIZE)
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filename, 'rb'))
    os.remove(filename)


# Declares a constant with the access token given in 'token.txt'.
TOKEN = open('token.txt').read().strip()

# Creates objects to work with Telegram.
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Indicates which function needs to be executed when the user uses a command.
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(MessageHandler(Filters.location, current_location))
dispatcher.add_handler(CommandHandler('congestions', congestions))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('pos', __pos))

# Starts the bot.
updater.start_polling()
