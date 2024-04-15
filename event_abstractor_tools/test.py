from rdflib import Graph, RDFS, OWL
import utils as u
import prompts as p
import pm4py
import function_calls as fc

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

def create_ontology_string(level_dict, processed_classes, indent=0):
    ontology_string = ""
    for level in sorted(level_dict.keys()):
        for class_uri in level_dict[level]:
            if class_uri not in processed_classes:
                processed_classes.add(class_uri)
                class_label = class_uri.split("/")[-1].replace("_", " ")
                ontology_string += " " * indent + "-" * bool(indent) + class_label + "\n"
                subclasses = get_subclasses(g, class_uri)
                if subclasses:
                    ontology_string += create_ontology_string({level + 1: subclasses}, processed_classes, indent + 1)
    return ontology_string

# Read the OWL file
owl_file = "/home/tkv29/genai-ontology-event-abstraction/content/test.owl"
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
processed_classes = set()
ontology_string = create_ontology_string(level_dict, processed_classes)
print("Ontology string representation:")
print(ontology_string)



def abstract():
    # Read the OWL file
    owl_file = "/home/tkv29/genai-ontology-event-abstraction/content/test.owl"
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
    processed_classes = set()
    ontology_string = create_ontology_string(level_dict, processed_classes)
    print("Ontology string representation:")
    print(ontology_string)

    xes = "/home/tkv29/genai-ontology-event-abstraction/content/test.xes"

    dataframe = pm4py.read_xes(xes)
    activities = dataframe["activity"]
    print(activities)

    messages = [
        {"role": "system", "content": p.IDENTIFY_CONTEXT},
        {"role": "user", "content": p.IDENTIFY_PROMPT + "\n" + "\n".join(activities)},
    ]

    relevant_activities = u.query_gpt(messages=messages, tools=fc.TOOLS ,tool_choice={"type": "function", "function": {"name": "extract_medication_rows"}})
    print(relevant_activities)
    for activity in relevant_activities:
        messages = [
        {"role": "system", "content": p.ABSTRACTION_CONTEXT},
        {"role": "user", "content": p.ABSTRACTION_PROMPT_1 + ontology_string + p.ABSTRACTION_PROMPT_2 + activity},
    ]
        answer=u.query_gpt(messages=messages)
        print(answer)

abstract()

