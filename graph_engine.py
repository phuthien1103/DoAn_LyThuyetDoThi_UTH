import networkx as nx
import numpy as np
import json

class GraphEngine:
    def __init__(self, is_directed=True):
        self.graph = nx.DiGraph() if is_directed else nx.Graph()

    def add_edge(self, u, v, weight=10):
        self.graph.add_edge(u, v, weight=weight)

    def get_conversions(self):
        matrix = nx.to_numpy_array(self.graph)
        adj_list = dict(self.graph.adjacency())
        edge_list = list(self.graph.edges(data=True))
        return matrix, adj_list, edge_list

    def get_bfs_edges(self, start=0):
        try: return list(nx.bfs_edges(self.graph, start))
        except: return []

    def get_dfs_edges(self, start=0):
        try: return list(nx.dfs_edges(self.graph, start))
        except: return []

    def is_bipartite(self):

        try: return nx.is_bipartite(self.graph)
        except: return False

    def get_prim_edges(self):
        try:
            undirected = self.graph.to_undirected()
            return list(nx.minimum_spanning_edges(undirected, algorithm='prim', data=True))
        except: return []

    def get_kruskal_edges(self):
        try:
            undirected = self.graph.to_undirected()
            return list(nx.minimum_spanning_edges(undirected, algorithm='kruskal', data=True))
        except: return []

    def get_max_flow_ff(self, s, t):
        try:
            flow_value = nx.maximum_flow_value(self.graph, s, t, capacity='weight')
            return flow_value
        except: return 0

    def get_euler_circuit(self):
        try: return list(nx.eulerian_circuit(self.graph))
        except: return []