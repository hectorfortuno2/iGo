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


## iGo Python module



## Telegram bot

### Commands


### Installation

These are the steps you need to follow in order to use the `iGo` bot by yourself:

1. Create a directory in your computer where you will save all needed files. Name it, for example, `iGo_files`.
2. Download the 'iGo.py' and the `bot.py` files and save them with the same names in your previously created directory.
3. Install the [Telegram App] (https://desktop.telegram.org/) in your computer.
4. Create a new Telegram bot with the help of [`@BotFather`](https://t.me/botfather) and save the Token in a file named
`token.txt` inside the working directory.
5. Install all Python libraries required, specified in the `requirements.txt` text file. Pay attention at the version.
6. Being in your created directory, run the `bot.py` in Python. Head to your bot in the Telegram app and... ready to go!


## Authors

Héctor Fortuño and Ramon Ventura, freshmen of the Computer Science Degreee in Data Science and Engineering
at the Universitat Politècnica de Catalunya (UPC).
