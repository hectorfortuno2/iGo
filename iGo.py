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

Location = collections.namedtuple('Location', 'lat lng')
#Highway = collections.namedtuple('Highway', '...') # Tram
#Congestion = collections.namedtuple('Congestion', '...')

#OSM GRAPH
def exists_graph(GRAPH_FILENAME):
    """..."""


def download_graph(PLACE):
    """..."""

    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    """for node1, info1 in graph.nodes.items():
        print(node1, info1)
        # for each adjacent node and its information...
        for node2, edge in graph.adj[node1].items():
            print('    ', node2)
            print('        ', edge)"""
    #graph = ox.utils_graph.get_digraph(graph, weight='length')
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

    ox.plot_graph(graph, node_size=30, bgcolor = 'white', node_color = 'red', edge_color = 'black', figsize=(100,100), show=False, save=True, filepath='Barcelona.png')


#HIGHWAYS
def download_highways(HIGHWAYS_URL):
    """..."""

    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        return reader


def plot_highways(highways, highways_png, SIZE):
    """..."""

    next(highways)  # ignore first line with description
    m = StaticMap(SIZE, SIZE)
    current_way_id = 0
    node_a, node_b = (float(0), float(0))
    for line in highways:
        way_id, way_component, description, lng, lat = line
        if way_id == current_way_id:
            node_b = (float(lng), float(lat))
            line = Line((node_a, node_b), 'red', 2)
            m.add_line(line)
            node_a = node_b
        else:
            current_way_id = way_id
            node_a = (float(lng), float(lat))
    image = m.render()
    image.save(highways_png)


#CONGESTIONS
def download_congestions(CONGESTIONS_URL):
    """..."""

    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
        return reader


def plot_congestions(highways, congestions, congestions_png, SIZE):
    """..."""

    actual_status=[0 for i in range(600)]
    future_status=[0 for i in range(600)]
    for line in congestions:
        way_id, date, actual_value, future_value = line
        actual_status[int(way_id)] = int(actual_value)
        future_status[int(way_id)] = int(future_value)

    next(highways)  # ignore first line with description
    m = StaticMap(SIZE, SIZE)
    current_way_id = 0
    node_a, node_b = (float(0), float(0))
    for line in highways:
        way_id, way_component, description, lng, lat = line
        way = int(way_id)
        if way == current_way_id:
            node_b = (float(lng), float(lat))
            if actual_status[way] == 0:
                line = Line((node_a, node_b), 'Aqua', 3)
            if actual_status[way] == 1:
                line = Line((node_a, node_b), 'Lime', 3)
            if actual_status[way] == 2:
                line = Line((node_a, node_b), 'Green', 3)
            if actual_status[way] == 3:
                line = Line((node_a, node_b), 'OrangeRed', 3)
            if actual_status[way] == 4:
                line = Line((node_a, node_b), 'Red', 3)
            if actual_status[way] == 5:
                line = Line((node_a, node_b), 'DarkRed', 3)
            if actual_status[way] == 6:
                line = Line((node_a, node_b), 'Black', 3)
            m.add_line(line)
            node_a = node_b
        else:
            current_way_id = way
            node_a = (float(lng), float(lat))
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
