# iGo

iGo is a Telegram bot for moving around the city of Barcelona, Catalonia, in the fastest possible way, by motor vehicle.

## Overview

>iGo project consists in a simple and user-friendly Telegram bot that allows users to get information about the driving ways
of the city of Barcelona, their live congestion and the shortest path they need to follow in order to go from their location
to the place of the city that they want.
In order to make a proper implementation of the project, two files have been created:

>`iGo.py` is the main Python module that contains all methods related to the managing of the data of the ways and congestions of
Barcelona, their insertion in graph structures, the calculation of paths between locations and the creation of beautiful and colored
maps.

>`bot.py` is the Python file containing the implementation of a Telegram Bot that uses the `iGo` module in order to offer users a simple
interface between their instructions and methods needed to get the desired and correct output.

## Requirements

This project requires a series of Python libraries to be installed so that it can run with no errors.
You can actually download all necessary libraries running command `pip install -r requirements.txt` or
`pip3 install -r requirements.txt`, in your terminal, in the `requirements.txt` file directory.

## iGo Python module

The `iGo.py` python file provides the implementation for manipulating data related to the
highways and their congestion of the city of Barcelona, Catalonia.
It also provides methods to get shortest paths between two locations and plot them
in a map.

### Methods

The module contains several methods that can be divided in different groups:

1. `Open Street Maps`: methods to download the OSMnx graph of the city of Barcelona, look if it already exists, or plot it
into a PNG image.
2. `Highways`: methods related to the download and manipulation of the Highways data of Barcelona.
3. `Congestions`: methods related to the download and manipulation of the Congestions data of the Highways of Barcelona.
4. `iGraph`: methods to insert the previously downloaded data into the OSMnx graph of Barcelona, and also complete the edges
without given information using several functions and algorithms. Head to the `iGo.py` file to know more about them.
There is also a function to plot each way congestion into a map saved as a PNG image file.
5. `iPath`: methods to calculate the best or k paths from an origin to a destination location and print it in a map saved
as a PNG image file. Head to the `iGo.py` file to know more about them.

## Telegram bot

The `bot.py` Python file provides the Telegram bot implementation that uses methods from the `iGo.py` module
in order to create a simple interface for users to get information about driving ways of Barcelona as well as
getting the shortest path to a desired place of the city.

### Commands

Here are the available commands of the iGo Telegram bot:

- `/start`: conversation with the bot gets started.
- `/help`: assists the user with information of the available commands.
- `/author`: shows the author/s of the project.
- `/where`: shows a map with the user current position.
- `/go destination`: shows a map with the shortest path from the user location to a given destination in Barcelona.
   In addition, the map shows some alternative paths to follow in order to arrive to the same point.
   Examples:
   - `/go Camp Nou`
   - `/go Sagrada Familia`
- `/congestions`: shows a map with live congestions of Barcelona's driving ways.

### Installation

These are the steps you need to follow in order to use the `iGo` bot by yourself:

1. Create a directory in your computer where you will save all needed files. Name it, for example, `iGo_files`.
2. Download the 'iGo.py' and the `bot.py` files and save them with the same names in your previously created directory.
3. Install the [Telegram App](https://desktop.telegram.org/) in your computer.
4. Create a new Telegram bot with the help of [`@BotFather`](https://t.me/botfather) and save the Token in a file named
`token.txt` inside the working directory.
5. Install all Python libraries required, specified in the `requirements.txt` text file. Pay attention to their version.
6. Being in your created directory, run the `bot.py` in Python. Head to your bot in the Telegram app and... ready to go!

### Slow Performance Issue

As you may notice when using the bot, the performance is not as good as one expects. Basically, there are two reasons that lead to this:

>First one is that, we (the authors) do not have enough knowledge to design a multi-threading code or to implement other type
of methods in order to achieve a better performance time. At least, not yet... but we will soon!

>Second one is that the `networkx` library is quite slow. The performance time of their methods are big and, as we have a big graph
as the Barcelona driving ways one, time increases a lot. In addition, data provided by the Barcelona town hall is not complete and
does not have a good format, so managing that data is difficult and time-costing.

## Authors

Héctor Fortuño and Ramon Ventura, freshmen of the Computer Science Degree in Data Science and Engineering
at the Universitat Politècnica de Catalunya (UPC).
