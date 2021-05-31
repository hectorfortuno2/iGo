# iGo.py

"""iGo.py

The iGo.py python file provides the implementation for manipulating data related to the
highways and their congestion of the city of Barcelona, Catalonia.
It also provides methods to get shortest paths between two locations and plot them
in a map."""

# authors: Héctor Fortuño and Ramon Ventura

import collections
import osmnx as ox
import networkx as nx
from staticmap import StaticMap, CircleMarker, IconMarker, Line
import pickle
import urllib
import csv
from haversine import haversine

Location = collections.namedtuple('Location', 'lng lat') # Tuple used to represent a location with longitude and latitude coordinates.
Congestion = collections.namedtuple('Congestion', 'current future') # Tuple used to represent the current and future congestion of a highway.

# Open Street Maps Graph
def exists_graph(graph_filename):
    """Method that returns True if a graph, whose filename is given as a parameter,
    exists in the working directory. Otherwise, return False."""

    try: open(graph_filename, 'rb')
    except:
        return False # Graph with graph_filename does not exist.
    return True


def download_graph(place):
    """Method that downloads an OSMnx graph of the place (City, Country...) given as a parameter, transforms it into
    a directed graph, and returns it.
    The downloaded graph takes into account the driving networks only, and the weight attribute used to
    get the directe version is the length of each edge."""

    graph = ox.graph_from_place(place, network_type='drive', simplify=True)
    graph = ox.utils_graph.get_digraph(graph, weight='length') # Get the directed graph version of the previously downloaded graph.

    return graph


def save_graph(graph, graph_filename):
    """Method that saves a graph in the current working directory, with filename passed as a parameter,
    or in a different location if the path is given instead of a single filename."""

    with open(graph_filename, 'wb') as file:
        pickle.dump(graph, file)


def load_graph(graph_filename):
    """Method that returns an existing graph in the current working directory or in the location
    specified by a path given in the filename parameter.
    Precondition: The graph with given path and filename exists in that location."""

    if not exists_graph(graph_filename): #Check the precondition.
        TypeError()
    with open(graph_filename, 'rb') as file:
        graph = pickle.load(file)

    return graph


def plot_graph(graph, graph_png_filename, size):
    """Method that plots a given graph in a png image with size specified by the third parameter.
    The image will not be shown but saved with given filename and path (2nd parameter)."""

    ox.plot_graph(graph, node_size=0, figsize=(size,size), show=False, save=True, filepath=graph_png_filename)

# Highways
def download_highways(HIGHWAYS_URL):
    """Specific method created to download the highways of the city of Barcelona.
    In addition, the function converts the downloaded csv file into a csv.reader to finally put the most important
    information in a list of lists.
    The returned list contains in position 'i' the highway with way_id 'i'.
    Each highway is defined as a list of Locations (tuple of longitud and latitude coordinates),
    in which every Location creates a segment of the highway with the following one."""

    highways = [[] for i in range(550)] # Needed defined list to contain all highways. There is extra space in case provided data is increased.
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"') # Get csv.reader file.
        next(reader)
        for line in reader:
            way_id, way_component, description, lng, lat = line
            location = (Location) (float(lng), float(lat))
            highways[int(way_id)].append(location) # Append Location into the position of the list containing the path of its highway.

    return highways


def plot_highways(highways_list, highways_png_filename, size):
    """Method that creates a map, using StaticMap library, of some highways passed as a list.
    The created map, with defined size, is saved into a location passed as a second parameter.
    Each highway (=way) is defined as a list of Locations (tuple of longitud and latitude coordinates),
    in which every Location creates a segment of the highway with the following one, used to
    draw the lines in the map."""

    m = StaticMap(size, size)
    for way in highways_list:
        first = True
        for location in way:
            if not first:
                node_v = location
                line = Line((node_u, node_v), 'red', 2) # Add to the map the line of the relevant segment of the way.
                m.add_line(line)
                node_u = node_v
            else:
                node_u = location
                first = False
    image = m.render()
    image.save(highways_png_filename)

# Congestions
def download_congestions(CONGESTIONS_URL):
    """Specific method created to download the congestion of the highways of the city of Barcelona.
    In addition, the function converts the downloaded csv file into a csv.reader to finally put the most important
    information in a list.
    The returned list contains in position 'i' the Congestion of the highway with way_id 'i'.
    Congestion is a tuple formed by the current congestion and the expected future congestion in 15 minutes time.

    Congestion values: 0 = No info, 1 = Very fluid, 2 = Fluid, 3 = Dense, 4 = Very dense, 5 = Traffic congestion, 6 = Closed way"""

    congestions = [None] * 550 # Needed defined list to contain all Congestions. There is extra space in case provided data is increased.
    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"') # Get csv.reader file.
        for line in reader:
            way_id, date, current_value, future_value = line
            congestion = (Congestion) (int(current_value), int(future_value))
            congestions[int(way_id)] = congestion # Insert Congestion of the highway with way_id 'i into position 'i' of the list.

    return congestions


def plot_highways_congestions(highways_list, congestions_list, congestions_png, current, size):
    """Method that plots either the current congestion or the future expected congestion, only of the highways given by a list,
    in a map created with StaticMap library. If current = True, method will work with with current congestions. Otherwise,
    current = False, it will use the future congestions.
    Congestions list are also need to be given as a parameter.
    The created map, with defined size, is saved into a location passed as a third parameter."""

    colors = [None, 'Green', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black'] # Used web colors to draw segments depending on highway congestion.
    m = StaticMap(size, size)
    way_id = 0
    for way in highways_list:
        first = True
        for location in way:
            if not first:
                node_v = location
                if current: # If desired congestion is the current one.
                    if congestions_list[way_id] != None and congestions_list[way_id].current != 0: # Highways with no inforamtion are not drawn.
                        line = Line((node_u, node_v), colors[congestions_list[way_id].current], 2) # Draw line with selected color.
                        m.add_line(line)
                else: # If desired congestion is the future one.
                    if congestions_list[way_id] != None and congestions_list[way_id].future != 0: # Highways with no inforamtion are not drawn.
                        line = Line((node_u, node_v), colors[congestions_list[way_id].future], 2) # Draw line with selected color.
                        m.add_line(line)
                node_u = node_v
            else:
                node_u = location
                first = False
        way_id += 1
    image = m.render()
    image.save(congestions_png)

# iGraph
def __compare_edge_congestion(graph, node_u, node_v, edge_congestion, key):
    """Auxilliary private function that looks for a congestion between two nodes and,
    if it exists and has bigger value than the current one of the studied edge
    in the main method, replaces it. Finally return the new congestion of the studied edge.
    Parameter 'key' defines wether to look at current or future congestion.
    IMPORTANT: 'Closed road' congestion (6) is not used."""

    exists_congestion = True
    try: graph[node_u][node_v][key]
    except:
        exists_congestion = False
    if exists_congestion:
        near_edge_congestion = graph[node_u][node_v][key]
        if near_edge_congestion != 6 and near_edge_congestion > edge_congestion: # Check and compare the congestion value of the edge.
            edge_congestion = near_edge_congestion

    return edge_congestion


def __get_near_congestion(graph, node_u, node_v, current):
    """Given a graph and two connected nodes of it, this private function looks at near edges to find
    a congestion in order to insert it in the segment between the two nodes, where no congestion is defined.
    If the current edge goes from 'u' to 'v', a near edge is defined as the 1-level proximity edges,
    being these the ones that arrive to node 'u' and the ones that exit from node 'v'.
    If more than one congestion is found, it returns the bigger one.
    If no near congestion is found, a default congestion (2 = Fluid) is returned.
    Method needs to be specified wether to study current congestions (current = True)
    or future ones (current = False).
    IMPORTANT: 'Closed road' congestion (6) is not expanded."""

    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    edge_congestion = -1
    # Look at edges that go from another node to node u.
    for node in graph.predecessors(node_u):
        edge_congestion = __compare_edge_congestion(graph, node, node_u, edge_congestion, key)
    # Look at edges that exit from node v to another node.
    for node in graph.successors(node_v):
        edge_congestion = __compare_edge_congestion(graph, node_v, node, edge_congestion, key)
    if edge_congestion == -1: # No near congestion is found.
        edge_congestion = 2 # Return default congestion value.

    return edge_congestion


def __define_edge_attributes(graph, node_u, node_v, congestion, current):
    """Private method that defines and returns the values of the maximum speed, the length and
    the current/future congestion of an edge between two given nodes of a graph.
    If no maximum speed is found, get a default '30' km/h speed.
    If more than one maximum speed is found, get the lowest one.
    If no length is found, calculate it with haversine library.
    If no congestion is passed as a parameter, look at near edges congestions with method '__get_near_congestion'.
    IMPORTANT: 'speed' is returned in meters/second and 'length' in meters."""

    # Maximum speed
    try: graph[node_u][node_v]['maxspeed']
    except: # Edge does not have a defined maximum speed.
        graph[node_u][node_v]['maxspeed'] = '30'
    if isinstance(graph[node_u][node_v]['maxspeed'], str): # Single speed found.
        max_speed = (float(graph[node_u][node_v]['maxspeed'])*10)/36 # Speed in meters/second.
    else: # A list of speeds is found. Get the lowest one.
        max_speed = float('inf')
        for speed in graph[node_u][node_v]['maxspeed']:
            ms_speed = (float(speed)*10)/36 # Speed in meters/second.
            if ms_speed < max_speed:
                max_speed = ms_speed
    # Length
    try: graph[node_u][node_v]['length']
    except: # Edge does not have a defined length.
        location1 = (Location) (graph.nodes[node_u]['x'], graph.nodes[node_v]['y'])
        location2 = (Location) (graph.nodes[node_u]['x'], graph.nodes[node_v]['y'])
        graph[node_u][node_v]['length'] = haversine(location1, location2, unit='m') # Insert calculated length in the graph's edge.
    length = graph[node_u][node_v]['length']
    # Congestion
    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    if congestion == None:
            congestion = __get_near_congestion(graph, node_u, node_v, current) # Look at near edges congestions.
    graph[node_u][node_v][key] = congestion # Insert congestion in the graph's edge.

    return max_speed, length, congestion


def __expand_congestion_info(graph, way, way_congestion, current):
    """Private method that, given a highway with his current/future congestion information,
    inserts that congestion in every edge of the graph belonging to the highway and creates adds the 'itime'
    attribute to every edge, too.
    As highways are given as a list of Locations, the nearest node of the graph for each Location is searched, and then
    the shortest path between two consecutive Loctions (now nodes) is found in order to insert the congestion and the 'itime'
    to all paths of the OSMnx graph that form a highway.
    The 'itime' attribute is defined as the time (seconds) to go through a way with defined 'length' and being able to
    reach a determined percentage of the 'maxspeed' depending on the congestion.
    Speed percentage: Congestion = 1 --> 100% speed, Congestion = 2 --> 85% speed, Congestion = 3 --> 60% speed
                      Congestion = 4 --> 40% speed, Congestion = 5 --> 20% speed."""

    speed_percentage_based_on_congestion = [None, 1, 0.85, 0.6, 0.4, 0.2, None]
    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    first_location = True
    for location in way:
        if not first_location:
            node_dest = ox.distance.nearest_nodes(graph, location.lng, location.lat) # Look for the nearest node in the OSMnx graph of a Location.
            path = []
            try: path = ox.distance.shortest_path(graph, node_orig, node_dest, weight = 'length') # Find shortest path between two nodes (Locations).
            except: # If not found, try the other way as data may be given reversed.
                try:
                    path = ox.distance.shortest_path(graph, node_dest, node_orig, weight = 'length')
                except:
                    pass # Unable to find any path from u to v or v to u
            first_node = True
            for node in path: # For every node that forms the path in the graph representing a segment of the highway:
                if not first_node:
                    node_v = node
                    # Define attributes
                    edge_max_speed, edge_length, edge_congestion = __define_edge_attributes(graph, node_u, node_v, way_congestion, current)
                    # Create itime
                    if edge_congestion == 6:
                        itime = float('inf') # Closed road
                    else:
                        percentage = speed_percentage_based_on_congestion[edge_congestion]
                        itime = edge_length/(percentage*edge_max_speed) # Definition of itime.
                    graph[node_u][node_v][key] = itime
                    node_u = node_v
                else:
                    node_u = node
                    first_node = False
            node_orig = node_dest
        else:
            node_orig = ox.distance.nearest_nodes(graph, location.lng, location.lat) # Look for the nearest node in the OSMnx graph of a Location.
            first_location = False


def __complete_itime(graph, node_u, node_v, current):
    """Auxilliary private method to the '__complete_igraph_without_congestion' function that,
    given an edge from nodes 'u' to 'v' of a graph, defines the edge attributes, including current/future congestion,
    and the current/future itime of it.
    If current=True, method will look for current itime and congestion. Otherwise will do the same but for the future attributes.
    The 'itime' attribute is defined as the time (seconds) to go through a way with defined 'length' and being able to
    reach a determined percentage of the 'maxspeed' depending on the congestion.
    Speed percentage: Congestion = 1 --> 100% speed, Congestion = 2 --> 85% speed, Congestion = 3 --> 60% speed
                      Congestion = 4 --> 40% speed, Congestion = 5 --> 20% speed."""

    speed_percentage_based_on_congestion = [None, 1, 0.85, 0.6, 0.4, 0.2, float('inf')]
    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    # Define Edge attributes
    edge_max_speed, edge_length, edge_congestion = __define_edge_attributes(graph, node_u, node_v, None, current)
    # Create current/future itime
    if edge_congestion == 6:
        itime = float('inf') # Closed road
    else:
        percentage = speed_percentage_based_on_congestion[edge_congestion]
        itime = edge_length/(percentage*edge_max_speed) # Definition of itime.
    graph[node_u][node_v][key] = itime


def __complete_igraph_without_congestion(graph):
    """Given a graph, this private method looks for the current/future itime of every edge of the graph
    that has not been given a current/future itime yet because there is not information."""

    for node1 in graph:
        for node2 in graph.adj[node1]:
            try: graph[node1][node2]['current_itime']
            except: # current_itime not defined
                __complete_itime(graph, node1, node2, current=True) # Define current itime for this edge.
            try: graph[node1][node2]['future_itime']
            except: # future_itime not defined
                __complete_itime(graph, node1, node2, current=False) # Define future itime for this edge.


def build_igraph(graph, highways_list, congestions_list):
    """Method that, given a graph, a list of highways and its congestions, defines the current and future itime for
    all edges in the graph.
    First, it inserts the itime and the congestion of all those highways that do have that
    information. After this, it does the same to all other edges of the graph that haven't been able to get
    some of the previous attributes because the lack of information."""

    way_id = 0
    for way in highways_list:
        if congestions_list[way_id] != None and congestions_list[way_id].current != 0: # If there is current congestion info for the edge:
            current_way_congestion = congestions_list[way_id].current
            __expand_congestion_info(graph, way, current_way_congestion, current=True) # Expand the info to edges in the graph.
        if congestions_list[way_id] != None and congestions_list[way_id].future != 0: # If there is future congestion info for the edge:
            future_way_congestion = congestions_list[way_id].future
            __expand_congestion_info(graph, way, future_way_congestion, current=False) # Expand the info to edges in the graph.
        way_id += 1
    __complete_igraph_without_congestion(graph) # Complete the graph. Will only modify edges with no current or future info.

    return graph


def plot_igraph_congestions(igraph, igraph_congestions_png, size, current):
    """Method that plots either the current congestion or the future expected congestion of all edges of the graph
    in a map created with StaticMap library.
    If current = True, method will work with with current congestions. Otherwise, current = False, it will use the future congestions.
    The created map, with defined size, is saved into a location passed as a parameter."""

    colors = [None, 'Green', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black'] # Used web colors.
    if current:
        key = 'current_congestion'
    else:
        key = 'future_congestion'
    map = StaticMap(size, size)
    for node1 in igraph:
        location1 = (Location) (igraph.nodes[node1]['x'], igraph.nodes[node1]['y']) # Get the node coordinates.
        for node2 in igraph.adj[node1]:
            location2 = (Location) (igraph.nodes[node2]['x'], igraph.nodes[node2]['y']) # Get the node coordinates.
            line = Line((location1, location2), colors[igraph[node1][node2][key]], 1) # Draw line in map.
            map.add_line(line)
    image = map.render(zoom = 13)
    image.save(igraph_congestions_png)

#iPath
def get_k_shortest_paths_with_itime(igraph, node_origin, node_destination, k, current):
    """Given a graph with current and future itime attributes defined for all edges,
    and given an origin and destination nodes of the graph, this method returns the k shortest
    paths from origin to destination looking at edges current/future itime.
    If current=True, method will look for current itime. Otherwise will do the same but for the future itime."""

    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    try: nx.algorithms.simple_paths.shortest_simple_paths(igraph, node_origin, node_destination, weight=key)
    except:
        print("Unable to find paths to destination.")
    generator = nx.algorithms.simple_paths.shortest_simple_paths(igraph, node_origin, node_destination, weight=key)
    ipaths = []
    for counter, path in enumerate(generator): # Get only the first k paths, which will be the shortest ones.
        ipaths.append(path)
        if counter == k-1:
            break

    return ipaths # Returns a list of paths, where every path is a list of nodes.


def get_shortest_path_with_itime(igraph, node_origin, node_destination, current):
    """Given a graph with current and future itime attributes defined for all edges,
    and given an origin and destination nodes of the graph, this method returns the shortest
    path from origin to destination looking at edges current/future itime.
    If current=True, method will look for current itime. Otherwise will do the same but for the future itime."""

    if current:
        key = 'current_itime'
    else:
        key = 'future_itime'
    try: ox.distance.shortest_path(igraph, node_origin, node_destination, weight=key)
    except:
        print("Unable to find a path to destination.")

    return ox.distance.shortest_path(igraph, node_origin, node_destination, weight=key) # The shortest path is a list of node ids.


def __get_3_best_ipaths(igraph, origin, destination):
    """Private method that, given a graph, an origin Location and a destination Location, finds the 3 best paths
    from origin node to destination node in the graph using 'itime' attributes.
    With the best shortest path, the path will be calculated using both current and future itimes, depending if the total time
    of the path arrives to 15 minutes in some point of it (as future congestion information referrs to congestion in 15 minutes)."""

    node_origin = ox.distance.nearest_nodes(igraph, origin.lng, origin.lat)
    node_destination = ox.distance.nearest_nodes(igraph, destination.lng, destination.lat)
    # Get best shortest path with current itime attribute.
    best_ipath = get_shortest_path_with_itime(igraph, node_origin, node_destination, current=True)
    # Look at the total time of the best path and, when bigger than 15 minutes, continue the path with future itime attribute.
    total_time = 0
    current_best_ipath = [] # Part of the best path calculated with current itime.
    origin_future_node = None # Origin node used to find the shortest path to destination using future itime.
    first = True
    for node in best_ipath:
        if not first:
            node_v = node
            total_time += igraph[node_u][node_v]['current_itime']
            if total_time > 900: # If the total amount of time till node is longer than 15 minutes:
                origin_future_node = node_u # Save origin node to find shortest path with future itime.
                break
            current_best_ipath.append(node) # Add node into current itime calculated path.
            node_u = node_v
        else:
            node_u = node
            current_best_ipath.append(node) # Add node into current itime calculated path.
            first = False
    future_best_ipath = []
    if origin_future_node != None:
        # Part of the best path calculated with future itime.
        future_best_ipath = get_shortest_path_with_itime(igraph, origin_future_node, node_destination, current=False)
    # Get 3 best shortest paths with current itime attribute.
    k_ipaths = get_k_shortest_paths_with_itime(igraph, node_origin, node_destination, 3, current=True)

    return current_best_ipath, future_best_ipath, k_ipaths


def __draw_path(igraph, map, path, color, width, key):
    """Private method that, given a graph, a map created with StaticMap and a path, draws the path with coloured lines
    in the map. The color and the width are also given as parameters. If no color is given, it will be obtained depending
    on the graph congestion attribute defined by the 'key' parameter."""

    colors = [None, 'Green', 'Green', 'OrangeRed', 'Red', 'DarkRed', 'Black'] # Used web colors.
    first = True
    for node in path:
        if not first:
            node_v = node
            location_b = (Location) (igraph.nodes[node]['x'], igraph.nodes[node]['y']) # Get the node coordinates.
            if color == None: # No color is given. Get the color depending on the graph attribute 'key' value.
                segment_color = colors[igraph[node_u][node_v][key]]
                line = Line((location_a, location_b), segment_color, width)
            else:
                line = Line((location_a, location_b), color, width)
            map.add_line(line)
            node_u = node_v
            location_a = location_b
        else:
            node_u = node
            location_a = (Location) (igraph.nodes[node]['x'], igraph.nodes[node]['y']) # Get the node coordinates.
            first = False


def plot_k_ipaths(igraph, best_ipath_current, best_ipath_future, alternative_ipaths_list, ipath_png, size):
    """Method that, given a graph, the part of the best path calculated with the current itime and the one
    with the future itime, and a list of alternative paths, plots them into a map.
    The map is created with StaticMap and has a size defined by a given parameter.
    Once all lines are drawn, the map is saved into a location passed as a parameter."""

    # Draw alternative ipaths
    map = StaticMap(size, size)
    for path in alternative_ipaths_list:
        __draw_path(igraph, map, path, 'SlateGray', 4, None) # Draw the alternative path with grey color.
    # Draw main ipath
    __draw_path(igraph, map, best_ipath_current, None, 5, 'current_congestion') # Draw the current part with color depending on current congestion value.
    __draw_path(igraph, map, best_ipath_future, None, 5, 'future_congestion') # Draw the future part with color depending on future congestion value.
    # Add markers
    origin_location = (Location) (igraph.nodes[best_ipath_current[0]]['x'], igraph.nodes[best_ipath_current[0]]['y'])
    if best_ipath_future == []:
        destination_location = (Location) (igraph.nodes[best_ipath_current[-1]]['x'], igraph.nodes[best_ipath_current[-1]]['y'])
    else:
        destination_location = (Location) (igraph.nodes[best_ipath_future[-1]]['x'], igraph.nodes[best_ipath_future[-1]]['y'])
    origin = IconMarker(origin_location, './origin.png', 10, 10)
    destination = IconMarker(destination_location, './destination.png', 10, 10)
    map.add_marker(origin)
    map.add_marker(destination)

    image = map.render()
    image.save(ipath_png)
