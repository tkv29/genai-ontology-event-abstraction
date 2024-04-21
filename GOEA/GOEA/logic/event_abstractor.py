from rdflib import Graph, RDFS, OWL
from . import utils as u
from . import prompts as p
import pm4py
from . import function_calls as fc
import networkx as nx
from pyvis.network import Network
from django.conf import settings

class EventAbstractor:
    """Singleton class that abstracts events from a XES file using an ontology file."""
    
    _instance = None

    def __new__(cls, xes_path, owl_path):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, xes_path=None, owl_path=None):
        self.xes_path = xes_path
        self.owl_path = owl_path
        if xes_path and owl_path:
            self.xes_df = pm4py.read_xes(xes_path)
            self.ontology_graph = self.__read_owl_file(owl_path)

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            EventAbstractor()
        return cls._instance

    def get_xes_df(self):
        return self.xes_df

    def __read_owl_file(self, file_path):
        ontology_graph = Graph()
        ontology_graph.parse(file_path)
        return ontology_graph

    def __get_subclasses(self, class_uri):
        return list(self.ontology_graph.subjects(RDFS.subClassOf, class_uri))

    def __get_class_depth(self, class_uri, depth=0):
        subclasses = self.__get_subclasses(class_uri)
        if not subclasses:
            return depth
        return max(self.__get_class_depth(subclass, depth + 1) for subclass in subclasses)
    
    def get_max_depth(self):
        root_class = OWL.Thing
        return self.__get_class_depth(root_class)

    def __create_level_dictionary(self, class_uri, level_dict, depth=0):
        if depth not in level_dict:
            level_dict[depth] = []
        level_dict[depth].append(class_uri)
        subclasses = self.__get_subclasses(class_uri)
        for subclass in subclasses:
            self.__create_level_dictionary(subclass, level_dict, depth + 1)

    def __create_ontology_string(self, level_dict, processed_classes, indent=0):
        ontology_string = ""
        for level in sorted(level_dict.keys()):
            for class_uri in level_dict[level]:
                if class_uri not in processed_classes:
                    processed_classes.add(class_uri)
                    class_label = class_uri.split("/")[-1].replace("_", " ")
                    ontology_string += " " * indent + "-" * bool(indent) + class_label + "\n"
                    subclasses = self.__get_subclasses(class_uri)
                    if subclasses:
                        ontology_string += self.__create_ontology_string({level + 1: subclasses}, processed_classes, indent + 1)
        return ontology_string

    def create_ontology_representation(self):
        root_class = OWL.Thing
        max_depth = self.__get_class_depth(root_class)
        print("Ontology depth:", max_depth)

        level_dict = {}
        self.__create_level_dictionary(root_class, level_dict)
        print("Level dictionary:", level_dict)

        processed_classes = set()
        ontology_string = self.__create_ontology_string(level_dict, processed_classes)

        return ontology_string
    
    def __create_visualization_graph(self):
        visualization_graph = nx.DiGraph()
        for s, p, o in self.ontology_graph:
            if p == RDFS.subClassOf:
                subject_depth = self.__get_class_depth(s)
                object_depth = self.__get_class_depth(o)
                visualization_graph.add_edge(str(s), str(o), depth=max(subject_depth, object_depth))
        return visualization_graph

    def visualize_graph(self, depth):
        visualization_graph = self.__create_visualization_graph()
        # Filter the graph based on the selected depth
        filtered_edges = [(u, v) for u, v, d in visualization_graph.edges(data=True) if d['depth'] <= depth]
        filtered_graph = nx.DiGraph(filtered_edges)

        net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
        net.from_nx(filtered_graph)
        net.repulsion(node_distance=420, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)
        html_file = net.generate_html()
        modified_html = html_file.replace('lib/bindings/utils.js', f'{settings.STATIC_URL}js/utils.js')
        return modified_html
    
    def abstract(self):
        ontology_string = self.create_ontology_representation()

        dataframe = pm4py.read_xes(self.xes_file)
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

    def update_progress(self, view, current_step, module_name):
        """Update the progress of the extraction."""
        if view is not None:
            percentage = round(
                (current_step / len(self.get_configuration().modules)) * 100
            )
            view.request.session["progress"] = percentage
            view.request.session["status"] = module_name
            view.request.session.save()