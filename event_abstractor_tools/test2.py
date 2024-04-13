
from rdflib import Graph, Namespace, RDF, RDFS, OWL

def read_owl_file(file_path):
    g = Graph()
    g.parse(file_path)
    return g

def get_subclasses(graph, class_uri):
    return list(graph.subjects(RDFS.subClassOf, class_uri))

def get_class_depth(graph, class_uri, depth=0):
    subclasses = get_subclasses(graph, class_uri)
    if not subclasses:
        return depth
    return max(get_class_depth(graph, subclass, depth + 1) for subclass in subclasses)

def create_level_dictionary(graph, class_uri, level_dict, depth=0):
    if depth not in level_dict:
        level_dict[depth] = []
    level_dict[depth].append(class_uri)
    subclasses = get_subclasses(graph, class_uri)
    for subclass in subclasses:
        create_level_dictionary(graph, subclass, level_dict, depth + 1)

def create_ontology_string(level_dict, indent=0):
    ontology_string = ""
    for level in sorted(level_dict.keys()):
        for class_uri in level_dict[level]:
            class_label = class_uri.split("/")[-1].replace("_", " ")
            ontology_string += "  " * indent + "-" * bool(indent) + class_label + "\n"
            subclasses = get_subclasses(g, class_uri)
            if subclasses:
                ontology_string += create_ontology_string({level + 1: subclasses}, indent + 1)
    return ontology_string

# Read the OWL file
owl_file = "/home/tkv29/genai-ontology-event-abstraction/content/ontology-2024-02-11_14-35-51.owl"
g = read_owl_file(owl_file)

# Get the root class (owl:Thing)
root_class = OWL.Thing

# Determine the depth of the ontology
max_depth = get_class_depth(g, root_class)
print("Ontology depth:", max_depth)

# Create a dictionary with levels and elements
level_dict = {}
create_level_dictionary(g, root_class, level_dict)
print("Level dictionary:", level_dict)

# Create a string representation of the ontology
ontology_string = create_ontology_string(level_dict)
print("Ontology string representation:")
print(ontology_string)