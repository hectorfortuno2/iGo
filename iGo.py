PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 1000
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/c97072a3-3619-4547-84dd-f1999d2a3fec/download/transit_relacio_trams_format_long.csv'
HIGHWAYS_URL_SHORT = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

import collections
import osmnx as ox
import networkx as nx
from staticmap import StaticMap, CircleMarker, IconMarker, Line
import pickle
import urllib
import csv

Location = collections.namedtuple('Location', 'lng lat')
Highway = collections.namedtuple('Highway', 'start end') # Tram
Congestion = collections.namedtuple('Congestion', 'actual future')

#OSM GRAPH
def exists_graph(GRAPH_FILENAME):
    """..."""


def download_graph(PLACE):
    """..."""

    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    graph = ox.utils_graph.get_digraph(graph, weight='length')
    return graph


def save_graph(graph, GRAPH_FILENAME):
    """..."""

    with open(GRAPH_FILENAME, 'wb') as file:
        pickle.dump(graph, file)


def load_graph(GRAPH_FILENAME):
    """..."""

    if not exists_graph(GRAPH_FILENAME):
        TypeError()
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pickle.load(file)
    return graph


def plot_graph(graph):
    """..."""

    ox.plot_graph(graph, node_size=0, figsize=(100,100), show=False, save=True, filepath='Barcelona.png')


#HIGHWAYS
def download_highways(HIGHWAYS_URL):
    """..."""

    highways = [[] for i in range(550)]
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)
        for line in reader:
            way_id, way_component, description, lng, lat = line
            location = (Location) (float(lng), float(lat))
            highways[int(way_id)].append(location)
    return highways
    #Returns a List in which position i contains a List with all Locations that form the segments of the way with way_id = i.



def plot_highways(highways_list, highways_png_filename, size):
    """..."""

    m = StaticMap(size, size)
    for way in highways_list:
        first = True
        for location in way:
            if not first:
                node_b = location
                line = Line((node_a, node_b), 'red', 2)
                m.add_line(line)
                node_a = node_b
            else:
                node_a = location
                first = False
    image = m.render()
    image.save(highways_png_filename)

#CONGESTIONS
def download_congestions(CONGESTIONS_URL):
    """..."""
    congestions = [None] * 550
    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
        for line in reader:
            way_id, date, actual_value, future_value = line
            congestion = (Congestion) (int(actual_value), int(future_value))
            congestions[int(way_id)] = congestion
    return congestions
    #Returns a List in which position i contains the tuple related to Congestion in highway with way_id = i.

def plot_congestions(highways_list, congestions_list, congestions_png, size):
    """..."""

    m = StaticMap(size, size)
    way_id = -1
    for way in highways_list:
        way_id += 1
        #Podriamos hacer una función set_color
        if congestions_list[way_id] != None:
            if congestions_list[way_id].actual == 0:
                color = 'Aqua'
            if congestions_list[way_id].actual == 1:
                color = 'Lime'
            if congestions_list[way_id].actual == 2:
                color = 'Green'
            if congestions_list[way_id].actual == 3:
                color = 'OrangeRed'
            if congestions_list[way_id].actual == 4:
                color = 'Red'
            if congestions_list[way_id].actual == 5:
                color = 'DarkRed'
            if congestions_list[way_id].actual == 6:
                color = 'Black'
        else:
            color = 'Aqua'
        first = True
        for location in way:
            if not first:
                node_b = location
                line = Line((node_a, node_b), color, 2)
                m.add_line(line)
                node_a = node_b
            else:
                node_a = location
                first = False
    image = m.render()
    image.save(congestions_png)


# iGRAPH
def build_igraph(graph, highways, congestions):
    """..."""




def test():
    G = ox.graph_from_place(PLACE, network_type='drive')
    #orig=(41.39381904874148, 2.112099838906549)
    #orig_node = ox.get_nearest_node(G, orig)
    #dest=(41.40644790244836, 2.149560446321661)
    #dest_node = ox.get_nearest_node(G, dest)
    orig = list(G)[0]
    dest = list(G)[15]
    route = nx.shortest_path(G, orig, dest)
    fig, ax = ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')
