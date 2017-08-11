import graphs
import nodes
import networkx as nx
import matplotlib.pyplot as plt


G = nx.Graph()
G.add_nodes_from(nodes.node)
print G.nodes()

G = nx.complement(G)

print G.nodes()
print G.edges()
G.remove_node(nodes.node[1])
print G.nodes()
print G.edges()