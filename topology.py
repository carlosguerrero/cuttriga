# -*- coding: utf-8 -*-
import logging
import matplotlib.pyplot as plt
import numpy as np
import random as rnd


import networkx as nx

from networkx.drawing.nx_agraph import write_dot, graphviz_layout


class Entity:
    """
    Different type of entities that there is in an environment. It is the abstract function that a node of the topology has.
    """
    ENTITY_CLUSTER = "CLUSTER"
    " A node who is a cluster"
    # ENTITY_SOURCE = "SOURCE"


    # ENTITY_EDGE = "EDGE"
    # "Only nodes where clients requests SERVICEs are tagged as EDGE device"
    ENTITY_DEV = "DEVICE"
    "Simple connection devices with sensor and actuator function"

    ENTITY_FOG = "FOG"
    "By default, all nodes are FOG Entities. All nodes can run a SERVICE"

"""
matplotlib.markers
# https://matplotlib.org/api/markers_api.html
"""
SHAPE_CLUSTER = "p"
SHAPE_EDGE = ">"
SHAPE_FOG = "o"

DRAW_ENTITY_TYPE = "ENTITY_TYPE"


class Topology:
    """
    This class unifies the functions to deal with **Complex Networks** as a network topology within of the simulator. In addition, it facilitates its creation, and assignment of attributes.
    """

    LINK_BW = "BW"
    "Link feature: Bandwidth"

    LINK_PR = "PR"
    "Link feauture:  Propagation delay"

    # LINK_LATENCY = "LATENCY"
    # " A edge or a network link has a Bandwidth"

    NODE_IPT = "IPT"
    "Node feature: IPS . Instructions per Simulation Time "

    NODE_RAM = "RAM"
    "Node feature: RAM Capacity of a node"

    NODE_COST = "COST"
    "Node feature: Cost per unit time"


    def __init__(self, logger=None):

        self.__idNode = -1
        self.G = None
        #G is a networkx graph

        self.nodeAttributes = {}
        self.clusterNodes = []
        #A simple *cache* to have all cluster nodes

        self.logger = logger or logging.getLogger(__name__)

    def __update_centrality(self):
        return nx.closeness_centrality(self.G)


    def __init_uptimes(self):
        for key in self.nodeAttributes:
            self.nodeAttributes[key]["uptime"] = (0, None)


    def get_edges(self):
        """
        Returns:
            list: a list of graph edges, i.e.: ((1,0),(0,2),...)
        """
        return self.G.edges

    def get_edge(self,key):
        """
        Args:
            key (str): a edge identifier, i.e. (1,9)
        Returns:
            list: a list of edge attributes
        """
        return self.G.edges[key]

    def get_nodes(self):
        """
        Returns:
            list: a list of all nodes features
        """
        return self.G.nodes

    def get_node(self, key):
        """
        Args:
            key (int): a node identifier
        Returns:
            list: a list of node features
        """
        return self.G.node[key]


    def get_info(self):
        return self.nodeAttributes

    def create_topology_from_graph(self, G):
        """
        It generates the topology from a NetworkX graph
        Args:
             G (*networkx.classes.graph.Graph*)
        """
        if isinstance(G, nx.classes.graph.Graph):
            self.G = G
            self.__idNode = len(G.nodes)
        else:
            raise TypeError

    def create_random_topology(self, nxGraphGenerator, params):
        """
        It generates the topology from a Graph generators of NetworkX
        Args:
             nxGraphGenerator (function): a graph generator function
        Kwargs:
            params (dict): a list of parameters of *nxGraphGenerator* function
        """
        try:
            self.G = nxGraphGenerator(*params)
            for node in self.G.nodes:
                self.G.node[node]["shape"] = SHAPE_FOG
                self.G.node[node]["type"] = Entity.ENTITY_FOG
            self.__idNode = len(self.G.node)
        except:
            raise Exception

    def load(self, data):
        """
            It generates the topology from a JSON file
            Args:
                 data (str): a json
        """
        self.G = nx.Graph()
        for edge in data["link"]:
            transmit = 1.0 / edge[self.LINK_BW]
            propagation = edge[self.LINK_PR]
            latency_link = transmit + propagation
            self.G.add_edge(edge["s"], edge["d"],weight=latency_link, BW=edge[self.LINK_BW],PR=edge[self.LINK_PR])
        # The node is created in edge creation


        #TODO
        for node in data["entity"]:
            self.G.node[node["id"]]["type"] = node["type"]
            self.nodeAttributes[node["id"]] = node
            self.G.node[node["id"]]["model"] = node["model"]
            # For drawing purporses
            if node["type"] == Entity.ENTITY_FOG:
                self.G.node[node["id"]]["shape"] = SHAPE_FOG
            elif node["type"] == Entity.ENTITY_CLUSTER:
                self.G.node[node["id"]]["shape"] = SHAPE_CLUSTER
                self.clusterNodes.append(node["id"])
        self.__idNode = len(self.G.nodes)
        self.__init_uptimes()

    def load_graphml(self,filename):
        self.G = nx.read_graphml(filename)
        attEdges = {}
        for k in self.G.edges():
            attEdges[k] = {"BW": 1, "PR": 1}
        nx.set_edge_attributes(self.G, values=attEdges)
        attNodes = {}
        for k in self.G.nodes():
            attNodes[k] = {"type": Entity.ENTITY_FOG, "model": "D", "IPT": 1, "RAM": 1, "COST": 1}
        nx.set_node_attributes(self.G, values=attNodes)
        for k in self.G.nodes():
            self.nodeAttributes[k] = self.G.node[k] #it has "id" att. TODO IMPROVE

    def set_cluster_nodes_centrality(self, density=0.1):
        """
        It selects a percentage of nodes as a Entity.Cluster according with network centrality
        Args:
            density (float): a percentage of nodes
        """
        centrality = self.__update_centrality()
        centrality = sorted(centrality.iteritems(), key=lambda (k, v): (v, k))
        self.clusterNodes = list(np.array(centrality[-int(density * self.size()):])[:, 0])
        for node in self.clusterNodes:
            self.G.node[node]["type"] = Entity.ENTITY_CLUSTER
            self.G.node[node]["shape"] = SHAPE_CLUSTER

    def set_cluster_nodes_fix(self, nodes=[]):
        """
        Defines a list of nodes as a Entity.cluster
        Args:
            nodes (list): a list of nodes' identifiers
        """
        self.clusterNodes = nodes
        for node in self.clusterNodes:
            self.G.node[node]["type"] = Entity.ENTITY_CLUSTER
            self.G.node[node]["shape"] = SHAPE_CLUSTER


    def set_cluster_nodes_random(self, prob=0.1, min=1, max=-1, seed=1):
        """
        Randomly chooses a number of nodes as cluster entities
        Args:
            prob (float): probability of selecting a node as a cluster
            min (int): minimum number of cluster nodes, by default, one
            max (int): maximum number of cluster nodes, by default, (-1) those that arise
            seed (int): random seed
        """
        self.clusterNodes = []
        rnd.seed(seed)
        if min <= 0: raise Exception
        while len(self.clusterNodes) < min:
            for idNode in self.G.nodes:
                if rnd.random() <= 0.1:
                    self.clusterNodes.append(idNode)
                if len(self.clusterNodes) == max:
                    break

        for node in self.clusterNodes:
            self.G.node[node]["type"] = Entity.ENTITY_CLUSTER
            self.G.node[node]["shape"] = SHAPE_CLUSTER



    def set_edges_NonUniformAtt(self, attr, values, p, seed=0):
        """
        Assigns one attribute to edges the values according with a non uniform distribution  (list of probabilities-values)
        Args:
            attr (str): attribute identifier
            values (list): a list of possible values
            p (list): a list of
            seed (int): random seed, by default 0
        """
        np.random.seed(seed)
        edge_speed = np.random.choice(values, len(self.G.edges), p)
        # nx.set_edge_attributes(self.G, 'speed', dict(zip(self.G.edges.keys(),edgeSpeed)))
        ## NOTE: It is a networkx bug -- TypeError: unhashable type: 'dict'
        # ALTERNATIVE
        for idx, edge in enumerate(self.G.edges):
            self.G[edge[0]][edge[1]][attr] = edge_speed[idx]

    def set_nodes_NonUniformAtt(self, attr, fogp, clusterp=[], seed=0):
        """
        Assigns models of devices to nodes according with non uniform distribution
        Args:
            attr (dict)
            fogp (list) odds of choosing one of fogs devices
            clusterp (list) odds of choosing one of cluster devices
            seed (int): random seed, by default 0
        """

        np.random.seed(seed)
        node_fog_pos = np.random.choice(range(len(attr[Entity.ENTITY_FOG])), len(self.G.nodes), fogp)
        node_cloud_pos = np.random.choice(range(len(attr[Entity.ENTITY_CLUSTER])), len(self.G.nodes), clusterp)
        for idx, node in enumerate(self.G.nodes):
            if self.G.node[node]["type"] == Entity.ENTITY_FOG:
                self.nodeAttributes[idx] = attr[Entity.ENTITY_FOG][node_fog_pos[idx]]
                self.nodeAttributes[idx]["type"] = Entity.ENTITY_FOG
            elif self.G.node[node]["type"] == Entity.ENTITY_CLUSTER:
                self.nodeAttributes[idx] = attr[Entity.ENTITY_CLUSTER][node_cloud_pos[idx]]
                self.nodeAttributes[idx]["type"] = Entity.ENTITY_CLUSTER

        self.__init_uptimes()

    def get_nodes_att(self):
        """
        Returns:
            A dictionary with the features of the nodes
        """
        return self.nodeAttributes

    def find_IDs(self,value):
        """
        Search for nodes with the same attributes that value
        Args:
             value (dict). example value = {"model": "m-"}. Only one key is admitted
        Returns:
            A list with the ID of each node that have the same attribute that the value.value
        """
        keyS = value.keys()[0]

        result = []
        for key in self.nodeAttributes.keys():
            val = self.nodeAttributes[key]
            if keyS in val:
                if value[keyS] == val[keyS]:
                    result.append(key)
        return result


    def size(self):
        """
        Returns:
            an int with the number of nodes
        """
        return len(self.G.nodes)

    def add_node(self, nodes, edges=None):
        """
        Add a list of nodes in the topology
        Args:
            nodes (list): a list of identifiers
            edges (list): a list of destination edges
        """
        self.__idNode = + 1
        self.G.add_node(self.__idNode)
        self.G.add_edges_from(zip(nodes, [self.__idNode] * len(nodes)))

        #self.__updateCentrality()
        #TODO
        return self.__idNode

    def remove_node(self, id_node):
        """
        Remove a node of the topology
        Args:
            id_node (int): node identifier
        """
        #TODO
        self.G.remove_node(id_node)
        #        self.__updateCentrality()
        return self.size()



    def get_centrality(self):
        """
        This function returns the centrality of each node.
        It is an example of how to obtain topological features of the network.
        """
        return self.__update_centrality()


    def draw(self,disable_color=False,colors=None,labels_edge=None,nodes_dev=None):
        """
        Draw the network using matplotlib library
        Default Color is based on Centrality Value. Depending on the complexity of the network, this value can be expensive to obtain and the color option can be disabled.
        Args:
            disable_color (boolean): Disables the coloring of the nodes.
        """
        node_color = None
        if not disable_color and not colors:
            node_color = self.__update_centrality()
        elif colors:
            node_color = colors

        # TODO define specific att.labels
        labels = dict(zip(range(self.size()), range(self.size())))
        # print labels
        for id in labels:
            # model = self.nodeAttributes[id]["model"]
            labels[id] = id
            # labels[id]="%i %s"%(id,"")#model)


        # pos = nx.spring_layout(self.G)
        pos = graphviz_layout(self.G)

        nx.draw(self.G, pos=pos, node_color=node_color.values() if not disable_color else None, cmap=plt.cm.Blues)


        nx.draw_networkx_labels(self.G, pos, labels, font_size=8)
        try:
            nx.draw_networkx_nodes(self.G, pos, nodelist=self.clusterNodes,
                                   node_shape=SHAPE_CLUSTER)  # LA shape puede ser especial
        except:
            None

        if labels_edge is None:
            nx.draw_networkx_edge_labels(self.G, pos=pos, font_size=6)
        else:
            nx.draw_networkx_edge_labels(self.G, pos=pos, font_size=6,edge_labels=labels_edge)

        pos2 = pos
        if nodes_dev:
            for n in nodes_dev:
                pos2[n] = (pos2[n][0], pos2[n][1] - 20.0)

            nx.draw_networkx_nodes(self.G, pos2, nodelist=nodes_dev, node_shape="^", node_color=(0.5, 0.5, 0.5),
                                   node_size=100)  # LA shape puede ser especial



        plt.savefig("network.pdf", bbox_inches="tight",dpi=300)
        # plt.show()
        # plt.clf()

    def write(self,path):
        nx.write_gexf(self.G, path)