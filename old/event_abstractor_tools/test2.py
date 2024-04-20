from rdflib import Graph, RDFS, OWL
import utils as u
import prompts as p
import pm4py
import function_calls as fc
import networkx as nx
from pyvis.network import Network

OWL_FILE = "/home/tkv29/genai-ontology-event-abstraction/content/test.owl"
XES_FILE = "/home/tkv29/genai-ontology-event-abstraction/content/test.xes"

def read_owl_file(file_path):
    ontology_graph = Graph()
    ontology_graph.parse(file_path)
    return ontology_graph

def get_subclasses(ontology_graph, class_uri):
    return list(ontology_graph.subjects(RDFS.subClassOf, class_uri))

def get_class_depth(ontology_graph, class_uri, depth=0):
    subclasses = get_subclasses(ontology_graph, class_uri)
    if not subclasses:
        return depth
    return max(get_class_depth(ontology_graph, subclass, depth + 1) for subclass in subclasses)

def create_level_dictionary(ontology_graph, class_uri, level_dict, depth=0):
    if depth not in level_dict:
        level_dict[depth] = []
    level_dict[depth].append(class_uri)
    subclasses = get_subclasses(ontology_graph, class_uri)
    for subclass in subclasses:
        create_level_dictionary(ontology_graph, subclass, level_dict, depth + 1)

def create_ontology_string(level_dict, processed_classes, ontology_graph, indent=0):
    ontology_string = ""
    for level in sorted(level_dict.keys()):
        for class_uri in level_dict[level]:
            if class_uri not in processed_classes:
                processed_classes.add(class_uri)
                class_label = class_uri.split("/")[-1].replace("_", " ")
                ontology_string += " " * indent + "-" * bool(indent) + class_label + "\n"
                subclasses = get_subclasses(ontology_graph, class_uri)
                if subclasses:
                    ontology_string += create_ontology_string({level + 1: subclasses}, processed_classes, ontology_graph, indent + 1)
    return ontology_string

def create_ontology_representation(ontology_graph):
    root_class = OWL.Thing
    max_depth = get_class_depth(ontology_graph, root_class)
    print("Ontology depth:", max_depth)
    level_dict = {}
    create_level_dictionary(ontology_graph, root_class, level_dict)
    print("Level dictionary:", level_dict)
    processed_classes = set()
    ontology_string = create_ontology_string(level_dict, processed_classes, ontology_graph)
    print("Ontology string representation:")
    print(ontology_string)
    return ontology_string

def create_graph(ontology_graph):
    G = nx.DiGraph()
    for s, p, o in ontology_graph:
        if p == RDFS.subClassOf:
            G.add_edge(str(s), str(o))
    return G

def visualize_graph(G):
    net = Network(height='800px', width='100%', bgcolor='#222222', font_color='white')
    net.from_nx(G)
    net.repulsion(node_distance=420, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)
    net.show('ontology_graph.html')

def abstract(ontology_graph):
    ontology_string = create_ontology_representation(ontology_graph)
    dataframe = pm4py.read_xes(XES_FILE)
    activities = dataframe["activity"]
    print(activities)
    messages = [
        {"role": "system", "content": p.IDENTIFY_CONTEXT},
        {"role": "user", "content": p.IDENTIFY_PROMPT + "\n" + "\n".join(activities)},
    ]
    relevant_activities = u.query_gpt(messages=messages, tools=fc.TOOLS, tool_choice={"type": "function", "function": {"name": "extract_medication_rows"}})
    print(relevant_activities)
    for activity in relevant_activities:
        messages = [
            {"role": "system", "content": p.ABSTRACTION_CONTEXT},
            {"role": "user", "content": p.ABSTRACTION_PROMPT_1 + ontology_string + p.ABSTRACTION_PROMPT_2 + activity},
        ]
        answer = u.query_gpt(messages=messages)
        print(answer)
    
    # Create and visualize the graph
    G = create_graph(ontology_graph)
    visualize_graph(G)

if __name__ == "__main__":
    ontology_graph = read_owl_file(OWL_FILE)
    abstract(ontology_graph)