from rdflib import Graph, Namespace, RDF, RDFS, OWL
import networkx as nx
import matplotlib.pyplot as plt
import os

def read_owl_file(file_path):
    g = Graph()
    g.parse(file_path)
    return g

def get_subclasses(graph, class_uri):
    return list(graph.subjects(RDFS.subClassOf, class_uri))

def create_graph(graph, class_uri, nx_graph, level=0):
    nx_graph.add_node(class_uri, level=level)
    subclasses = get_subclasses(graph, class_uri)
    for subclass in subclasses:
        nx_graph.add_edge(class_uri, subclass)
        create_graph(graph, subclass, nx_graph, level + 1)

def visualize_graph(nx_graph, output_dir, output_filename):
    pos = nx.multipartite_layout(nx_graph, subset_key='level', align='vertical', scale=100)
    labels = {node: node.split("/")[-1].replace("_", " ") for node in nx_graph.nodes()}
    levels = nx.get_node_attributes(nx_graph, 'level')
    node_colors = [levels[node] for node in nx_graph.nodes()]
    
    # Add some space between nodes
    for node, coords in pos.items():
        pos[node] = (coords[0], -coords[1])
    
    fig, ax = plt.subplots(figsize=(20, 10))
    nx.draw_networkx_nodes(nx_graph, pos, node_color=node_colors, cmap=plt.cm.Blues, node_size=50, ax=ax)
    nx.draw_networkx_edges(nx_graph, pos, edge_color='gray', arrows=True, ax=ax)
    
    # Adjust label positions to be closer to the nodes
    label_pos = pos.copy()
    for node, coords in pos.items():
        label_pos[node] = (coords[0], coords[1] + 0.03)
    
    nx.draw_networkx_labels(nx_graph, label_pos, labels, font_size=10, ax=ax)
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save the visualization to a file
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path)
    
    plt.show()


# Read the OWL file
owl_file = "/home/tkv29/genai-ontology-event-abstraction/content/test.owl"
g = read_owl_file(owl_file)

# Create a NetworkX graph
nx_graph = nx.DiGraph()

# Populate the NetworkX graph with the ontology hierarchy
root_class = OWL.Thing
create_graph(g, root_class, nx_graph)

# Specify the output directory and filename
output_dir = "/home/tkv29/genai-ontology-event-abstraction/content"
output_filename = "ontology_visualization.png"

# Visualize the graph and save it to a file
visualize_graph(nx_graph, output_dir, output_filename)