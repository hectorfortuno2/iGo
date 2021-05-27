# iGo.py

"""
    ..."""

# authors: Héctor Fortuño and Ramón Ventura

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 1000
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/c97072a3-3619-4547-84dd-f1999d2a3fec/download/transit_relacio_trams_format_long.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

import collections
import osmnx as ox
import networkx as nx
from staticmap import StaticMap, CircleMarker, IconMarker, Line
import pickle
import urllib
import csv
from haversine import haversine

Location = collections.namedtuple('Location', 'lng lat')
Congestion = collections.namedtuple('Congestion', 'current future')

#OSM GRAPH
def exists_graph(graph_filename):
    """..."""

    try:
        with open(graph_filename, 'rb') as file:
            pickle.load(file)
    except:
        return False
    return True

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
            way_id, date, current_value, future_value = line
            congestion = (Congestion) (int(current_value), int(future_value))
            congestions[int(way_id)] = congestion
    return congestions
    #Returns a List in which position i contains the tuple related to Congestion in highway with way_id = i.

def plot_highways_congestions(highways_list, congestions_list, congestions_png, current, size):
    """..."""

    colors = [None, 'Green', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black']
    m = StaticMap(size, size)
    way_id = 0
    for way in highways_list:
        first = True
        for location in way:
            if not first:
                node_v = location
                if current:
                    if congestions_list[way_id] != None and congestions_list[way_id].current != 0 and congestions_list[way_id].current != 6:
                        line = Line((node_u, node_v), colors[congestions_list[way_id].current], 2)
                        m.add_line(line)
                else:
                    if current:
                        if congestions_list[way_id] != None and congestions_list[way_id].future != 0 and congestions_list[way_id].future != 6:
                            line = Line((node_u, node_v), colors[congestions_list[way_id].future], 2)
                            m.add_line(line)
                node_u = node_v
            else:
                node_u = location
                first = False
        way_id += 1
    image = m.render()
    image.save(congestions_png)


def __get_near_congestion(graph, node_u, node_v, current):
    """..."""

    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    edge_congestion = -1
    #Edges before our main edge
    for node in graph.predecessors(node_u):
        exists_congestion = True
        try: graph[node][node_u][key]
        except:
            exists_congestion = False
        if exists_congestion:
            near_edge_congestion = graph[node][node_u][key]
            #print("got congestion from another edge", near_edge_congestion)
            if near_edge_congestion != 6 and near_edge_congestion > edge_congestion: #La máxima de las congestiones cercanas?
                edge_congestion = near_edge_congestion
    #Edges after our main edge
    for node in graph.successors(node_v):
        exists_congestion = True
        try: graph[node_v][node][key]
        except:
            exists_congestion = False
        if exists_congestion:
            near_edge_congestion = graph[node_v][node][key]
            #print("got congestion from another edge", near_edge_congestion)
            if near_edge_congestion != 6 and near_edge_congestion > edge_congestion: #La máxima de las congestiones cercanas?
                edge_congestion = near_edge_congestion
    if edge_congestion == -1: #Any near edge has congestion
        edge_congestion = 2 #Por lo pronto, a las highways sin info les ponemos 2.

    return edge_congestion


def __define_edge_attributes(graph, node_u, node_v, congestion, current):
    """..."""
    #MAXSPEED
    try: graph[node_u][node_v]['maxspeed']
    except:
        graph[node_u][node_v]['maxspeed'] = '30'
    if isinstance(graph[node_u][node_v]['maxspeed'], str): #Single speed
        max_speed = (float(graph[node_u][node_v]['maxspeed'])*10)/36
    else: #List of speeds. Get the minimum?
        max_speed = float('inf')
        for speed in graph[node_u][node_v]['maxspeed']:
            ms_speed = (float(speed)*10)/36 #Speed in Meters/Second
            if ms_speed < max_speed:
                max_speed = ms_speed
    # LENGTH
    try: graph[node_u][node_v]['length']
    except:
        print('haversine')
        location1 = (Location) (graph.nodes[node_u]['x'], graph.nodes[node_v]['y'])
        location2 = (Location) (graph.nodes[node_u]['x'], graph.nodes[node_v]['y'])
        graph[node_u][node_v]['length'] = haversine(location1, location2, unit='m') #get length between nodes in meters.
    length = graph[node_u][node_v]['length']
    # CONGESTION
    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    if congestion == None:
            congestion = __get_near_congestion(graph, node_u, node_v, current)
    graph[node_u][node_v][key] = congestion
    return max_speed, length, congestion


def __expand_congestion_info(graph, way, way_congestion, current):
    """..."""

    speed_percentage_based_on_congestion = [None, 1, 0.85, 0.6, 0.4, 0.2, None]
    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    first_location = True
    for location in way: #Por cada segmento de la highway
        if not first_location:
            node_dest = ox.distance.nearest_nodes(graph, location.lng, location.lat)
            path = []
            try: path = ox.distance.shortest_path(graph, node_orig, node_dest, weight = 'length')
            except:
                try:
                    path = ox.distance.shortest_path(graph, node_dest, node_orig, weight = 'length')
                except:
                    pass #Unable to find any path from u to v or v to u
            first_node = True
            for node in path: # Por cada trozo del camino entre los nodos del segmento dentro del OSMnx graph
                if not first_node:
                    node_v = node
                    ## Definimos atributos
                    edge_max_speed, edge_length, edge_congestion = __define_edge_attributes(graph, node_u, node_v, way_congestion, current)
                    #iTIME
                    if edge_congestion == 6:
                        itime = float('inf')
                    else:
                        percentage = speed_percentage_based_on_congestion[edge_congestion]
                        itime = edge_length/(percentage*edge_max_speed)
                    #print('created itime for edge from', node_u, 'to', node_v, 'with value', itime)
                    graph[node_u][node_v][key] = itime
                    node_u = node_v
                else:
                    node_u = node
                    first_node = False
            node_orig = node_dest
        else:
            node_orig = ox.distance.nearest_nodes(graph, location.lng, location.lat)
            first_location = False
    return 0


def __complete_igraph_without_congestion(graph):
    """..."""

    speed_percentage_based_on_congestion = [None, 1, 0.85, 0.6, 0.4, 0.2, float('inf')]
    for node1 in graph:
        for node2 in graph.adj[node1]:
            try: graph[node1][node2]['current_itime']
            except: #current_itime not defined
                # Define Attributes
                edge_max_speed, edge_length, edge_congestion = __define_edge_attributes(graph, node1, node2, None, current=True)
                #Create current_itime
                #iTIME
                if edge_congestion == 6:
                    current_itime = float('inf')
                else:
                    percentage = speed_percentage_based_on_congestion[edge_congestion]
                    current_itime = edge_length/(percentage*edge_max_speed)
                #print('created current_itime for edge from', node1, 'to', node2, 'with value', current_itime)
                graph[node1][node2]['current_itime'] = current_itime
            try: graph[node1][node2]['future_itime']
            except: #future_itime not defined
                # Define Attributes
                edge_max_speed, edge_length, edge_congestion = __define_edge_attributes(graph, node1, node2, None, current=False)
                #Create future_itime
                if edge_congestion == 6:
                    future_itime = float('inf')
                else:
                    percentage = speed_percentage_based_on_congestion[edge_congestion]
                    future_itime = edge_length/(percentage*edge_max_speed)
                #print('created future_itime for edge from', node1, 'to', node2, 'with value', future_itime)
                graph[node1][node2]['future_itime'] = future_itime
    return 0

# iGRAPH
def build_igraph(graph, highways_list, congestions_list):
    """añadir el atributo itime, (angulos), (expandir), usar lo del tiempo futuro (ipath)"""

    way_id = 0
    for way in highways_list: #Por cada highway
        #print(way_id)
        if congestions_list[way_id] != None and congestions_list[way_id].current != 0: #Solo si hay congestion, sino luego.
            current_way_congestion = congestions_list[way_id].current
            __expand_congestion_info(graph, way, current_way_congestion, current=True)
        if congestions_list[way_id] != None and congestions_list[way_id].future != 0: #Solo si hay congestion, sino luego.
            future_way_congestion = congestions_list[way_id].future
            __expand_congestion_info(graph, way, future_way_congestion, current=False)
        way_id += 1
    # Añadir un itime base a todas las aristas del grafo que no contengan itime.
    __complete_igraph_without_congestion(graph)
    return graph

#iPath
def get_k_shortest_paths_with_itime(igraph, origin, destination, k, current):
    """buscar k=3 shortest paths y hacer el shortest path a secas, que nos dará el mas corto. Pintar este último de colores """

    node_origin = ox.distance.nearest_nodes(igraph, origin.lng, origin.lat)
    node_destination = ox.distance.nearest_nodes(igraph, destination.lng, destination.lat)
    #print('given origin', origin.lng, origin.lat)
    #print('given destination', destination.lng, destination.lat)
    #print('node origin', node_origin, igraph.nodes[node_origin]['y'], igraph.nodes[node_origin]['x'])
    #print('node destination', node_destination, igraph.nodes[node_destination]['y'], igraph.nodes[node_destination]['x'])
    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    try: ox.distance.k_shortest_paths(igraph, node_origin, node_destination, k, weight=key)
    except:
        raise SystemError("Unable to find paths to destination.")

    return ox.distance.k_shortest_paths(igraph, node_origin, node_destination, k, weight=key)


def get_shortest_path_with_itime(igraph, origin, destination, current):
    """..."""

    node_origin = ox.distance.nearest_nodes(igraph, origin.lng, origin.lat)
    node_destination = ox.distance.nearest_nodes(igraph, destination.lng, destination.lat)
    #print('given origin', origin.lng, origin.lat)
    #print('given destination', destination.lng, destination.lat)
    #print('node origin', node_origin, igraph.nodes[node_origin]['y'], igraph.nodes[node_origin]['x'])
    #print('node destination', node_destination, igraph.nodes[node_destination]['y'], igraph.nodes[node_destination]['x'])

    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    try: ox.distance.shortest_path(igraph, node_origin, node_destination, weight=key)
    except:
        raise SystemError("Unable to find a path to destination.")

    return ox.distance.shortest_path(igraph, node_origin, node_destination, weight=key)


def plot_k_ipaths(igraph, best_ipath, alternative_ipaths_list, ipath_png, size, current):
    """..."""

    # Draw alternative ipaths
    map = StaticMap(size, size)
    for path in alternative_ipaths_list:
        first = True
        for node in path:
            if not first:
                location_b = (Location) (igraph.nodes[node]['x'], igraph.nodes[node]['y'])
                line = Line((location_a, location_b), 'Gray', 3)
                map.add_line(line)
                location_a = location_b
            else:
                location_a = (Location) (igraph.nodes[node]['x'], igraph.nodes[node]['y'])
                first = False
    # Draw main ipath
    colors = [None, 'Green', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black']
    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    first = True
    for node in best_ipath:
        if not first:
            node_v = node
            location_b = (Location) (igraph.nodes[node]['x'], igraph.nodes[node]['y'])
            color = colors[igraph[node_u][node_v][key]]
            line = Line((location_a, location_b), color, 5)
            map.add_line(line)
            node_u = node_v
            location_a = location_b
        else:
            node_u = node
            location_a = (Location) (igraph.nodes[node]['x'], igraph.nodes[node]['y'])
            first = False
    image = map.render()
    image.save(ipath_png)


def plot_igraph_congestions(igraph, size, current):

    colors = [None, 'Green', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black']
    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    map = StaticMap(size, size)
    for node1 in igraph:
        location1 = (Location) (igraph.nodes[node1]['x'], igraph.nodes[node1]['y'])
        for node2 in igraph.adj[node1]:
            location2 = (Location) (igraph.nodes[node2]['x'], igraph.nodes[node2]['y'])
            line = Line((location1, location2), colors[igraph[node1][node2][key]], 1)
            map.add_line(line)
    image = map.render()
    image.save('igraph.png')
