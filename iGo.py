# iGo.py

"""
    ..."""

# authors: Héctor Fortuño and Ramón Ventura

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 1000
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/c97072a3-3619-4547-84dd-f1999d2a3fec/download/transit_relacio_trams_format_long.csv'
#HIGHWAYS_URL_SHORT = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
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


def save_graph(graph, graph_filename):
    """..."""

    with open(graph_filename, 'wb') as file:
        pickle.dump(graph, file)


def load_graph(graph_filename):
    """..."""

    if not exists_graph(graph_filename):
        TypeError()
    with open(graph_filename, 'rb') as file:
        graph = pickle.load(file)
    return graph


def plot_graph(graph):
    """..."""

    ox.plot_graph(graph, node_size=0, figsize=(100,100), show=False, save=True, filepath='Barcelona.png')


#HIGHWAYS
def download_highways(highways_url):
    """..."""

    highways = [[] for i in range(550)]
    with urllib.request.urlopen(highways_url) as response:
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
                node_v = location
                line = Line((node_u, node_v), 'red', 2)
                m.add_line(line)
                node_u = node_v
            else:
                node_u = location
                first = False
    image = m.render()
    image.save(highways_png_filename)


#CONGESTIONS
def download_congestions(congestions_url):
    """..."""
    congestions = [None] * 550
    with urllib.request.urlopen(congestions_url) as response:
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
    way_id = 0
    for way in highways_list:
        way_id += 1
        colors = ['Aqua', 'Lime', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black']
        first = True
        for location in way:
            if not first:
                node_v = location
                if congestions_list[way_id] != None:
                    line = Line((node_u, node_v), colors[congestions_list[way_id].actual], 2)
                else:
                    line = Line((node_u, node_v), colors[0], 2)
                m.add_line(line)
                node_u = node_v
            else:
                node_u = location
                first = False
    image = m.render()
    image.save(congestions_png)


# iGRAPH
def build_igraph(graph, highways_list, congestions_list):
    """añadir el atributo itime, (angulos), (expandir), usar lo del tiempo futuro (ipath)"""
    #cojo las locations de un segmento, encuentro los nodos, obtengo el shortest path, por cada edge entre nodos del path: itime
    way_id = -1
    speed_percentage_based_on_congestion = [None, 1, 0.85, 0.6, 0.4, 0.2, float('inf')]
    for way in highways_list: #Por cada highway
        way_id += 1
        print(way_id)
        ###
        if congestions_list[way_id] != None and congestions_list[way_id].actual != 0:
            way_congestion = congestions_list[way_id].actual
        else:
            way_congestion = 1 #Por lo pronto, a las highways sin info les ponemos 1.
        first_location = True
        for location in way: #Por cada segmento de la highway
            if not first_location:
                node_dest_id = ox.distance.nearest_nodes(graph, location.lng, location.lat)
                path = []
                try: path = ox.distance.shortest_path(graph, node_orig_id, node_dest_id, weight = 'length')
                except:
                    try:
                        path = ox.distance.shortest_path(graph, node_dest_id, node_orig_id, weight = 'length')
                    except:
                        pass
                ### Meter esto en una función llamada expand_congestion(graph, edges_list, way_congestion)
                first_node = True
                for node_id in path: # Por cada trozo del camino entre los nodos del segmento dentro del OSMnx graph
                    if not first_node:
                        node_v_id = node_id
                        ## Cambiamos atributos
                        length = float(graph[node_u_id][node_v_id]['length'])
                        try: graph[node_u_id][node_v_id]['maxspeed']
                        except: graph[node_u_id][node_v_id]['maxspeed'] = '30'
                        if isinstance(graph[node_u_id][node_v_id]['maxspeed'], str): #Single speed
                            max_speed = (float(graph[node_u_id][node_v_id]['maxspeed'])*10)/36
                        else: #List of speeds. Get the minimum?
                            max_speed = float('inf')
                            for speed in graph[node_u_id][node_v_id]['maxspeed']:
                                ms_speed = (float(speed)*10)/36 #Speed in Meters/Second
                                if ms_speed < max_speed:
                                    max_speed = ms_speed
                        percentage = speed_percentage_based_on_congestion[way_congestion]
                        #print('length', length, 'speed', max_speed, 'percentage', percentage)
                        itime = length/(percentage*max_speed)
                        print('created itime for edge from', node_u_id, 'to', node_v_id, 'with value', itime)
                        graph[node_u_id][node_v_id]['itime'] = itime
                        ##
                        node_u_id = node_v_id
                    else:
                        node_u_id = node_id
                        first_node = False
                node_orig_id = node_dest_id
            else:
                node_orig_id = ox.distance.nearest_nodes(graph, location.lng, location.lat)
                first_location = False
    return graph

def test():
    orig = list(G)[0]
    dest = list(G)[15]
    route = nx.shortest_path(G, orig, dest)
    fig, ax = ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')
