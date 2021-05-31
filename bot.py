# bot.py

"""bot.py

The bot.py Python file provides the Telegram bot implementation that uses methods from the 'iGo.py' module
in order to create a simple interface for users to get information about driving ways of Barcelona as well as
getting the shortest path to a desired place of the city."""

# authors: Héctor Fortuño and Ramon Ventura

import collections
from datetime import datetime, date, timedelta
import iGo
import os
import osmnx as ox
from staticmap import StaticMap, CircleMarker, IconMarker, Line
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import threading

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
    are the highways and congestions. Also, the intelligent graph is created."""

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

    # Plot and store the real-time congestions.
    filename = 'congestions.png'
    iGo.plot_igraph_congestions(igraph, filename, SIZE, current=True)
    print('Ready to go!')


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

    # Plot and store the real-time congestions once updated.
    filename = 'congestions.png'
    os.remove(filename)
    iGo.plot_igraph_congestions(igraph, filename, SIZE, current=True)


def start(update, context):
    """Method that welcomes the user."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is iGo, the Telegram bot to get wherever you want, by car, in Barcelona...  at the speed of light!\n" +
        "Use /help command to know more about me.")


def help(update, context):
    """Method that displays all the available commands in the bot."""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I have the following commands:\n" +
        "- /author: shows the author/s of the project.\n" +
        "- /where: shows a map with your current position.\n" +
        "- /go destination: shows a map with the shortest path from your location to a given destination in Barcelona.\n" +
        "- /congestions: shows a map with live congestions of Barcelona's driving ways.")


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

    # Image saved in '__refresh_igraph' method is sent to the user.
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filename, 'rb'))


def where(update, context):
    """Method that sends an image to the user of his current location."""

    # Check if we already have the location of the user, if this is the case,
    # an image is sent.
    try:
        context.user_data['location']
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Here is your current location.')

        lng, lat = context.user_data['location'].lng, context.user_data['location'].lat

        # Check if the user is registered with a username (if not, ask to do so).
        if update.effective_chat.username == None:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please set a username to your Telegram account.')
            return 0

        # Create a png file (unique per user).
        filename = update.effective_chat.username + '.png'

        # Create a map and place a marker in user's location.
        map = StaticMap(500, 500)
        map.add_marker(IconMarker((lng, lat), './origin.png', 10, 10))
        image = map.render()
        image.save(filename)

        # Send the image
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(filename, 'rb'))
        os.remove(filename)

        # In order to make sure the user is satisfied, we ask again for the
        # location in case the user didn't update it properly.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='In case this is not your current position, send me your new location.')

    except:
        # In case of not having the location, the user is asked to send it.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your current location.')


def current_location(update, context):
    """Method that stores and updates the user's current location."""

    # Obtain the location of the user.
    location = update.message.location

    # Store it.
    context.user_data['location'] = (Location)(location.longitude, location.latitude)

    # Call the 'where' method in order to proceed with the new location.
    where(update, context)


def __place_to_coordinates(update, context, place):
    """Private method that converts the name of a place into coordinates. Returns
    a location."""

    try:
        # Checks if the message given by the user are coordinates.
        int(place[0])
    except:
        # Execute if the message are not coordinates.
        try:
            # Check if we are given a valid place.
            ox.geocoder.geocode(f"{place}, {PLACE}")
        except:
            # In case we are given something that is not a place or a pair of
            # coordinates, the bot cancels the execution.
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Not a valid location!')
            return 0

        # Convert the name of the place into coordinates.
        geo = ox.geocoder.geocode(f"{place}, {PLACE}")
        coordinates = (Location)(geo[1], geo[0])
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
    context.user_data['location'] = __place_to_coordinates(update, context, update.message.text[5:])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Location updated!')


def go(update, context):
    """Method that sends an image to the user of the 3 shortest paths to the
    destination specified, highliting the fastest one in color"""

    destination = update.message.text[4:]

    # If we are given no message, we notify the user and cancel the execution of the request.
    if len(destination) == 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your destination and try again.')
        return 0

    # Convert the destination of the user into coordinates.
    destination_coordinates = __place_to_coordinates(update, context, destination)

    try:
        # Check if a location was already stored.
        context.user_data['location']
    except:
        # If a location wasn't already stored, ask for a location.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please send me your current location and try again.')
        return 0

    origin_coordinates = context.user_data['location']

    # Check if our data needs to update.
    if __need_refresh():
        __refresh_igraph()

    try:
        # Try finding the 3 best paths to the destination.
        iGo.__get_3_best_ipaths(igraph, origin_coordinates, destination_coordinates)
    except:
        # If not possible, notify our user that we were unable to find a path.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Im sorry, I was not able to find a path to your destination.')
        return 0

    # Find the 3 best paths to the destination.
    best_ipath_current, best_ipath_future, k_ipaths = iGo.__get_3_best_ipaths(igraph, origin_coordinates, destination_coordinates)

    # Check if the user is registered with a username (if not, ask to do so).
    if update.effective_chat.username == None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please set a username to your Telegram account.')
        return 0

    filename = update.effective_chat.username + '.png'

    # Plot and send the user the 3 best paths, highliting the best one in color.
    iGo.plot_k_ipaths(igraph, best_ipath_current, best_ipath_future, k_ipaths, filename, SIZE)
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
