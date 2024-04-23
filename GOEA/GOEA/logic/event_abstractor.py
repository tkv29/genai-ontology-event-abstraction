from rdflib import Graph, RDFS, OWL
from . import utils as u
from . import prompts as p
import pm4py
from . import function_calls as fc
import networkx as nx
from pyvis.network import Network
from django.conf import settings
import random

class EventAbstractor:
    """Singleton class that abstracts events from a XES file using an ontology file."""
    
    _instance = None

    def __new__(cls, xes_path, owl_path):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, xes_path=None, owl_path=None):
        self.xes_path = xes_path
        print(xes_path)
        self.owl_path = owl_path
        self.data = None
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

    def __create_ontology_string(self, class_uri, processed_classes, depth, current_depth=0, indent=""):
        if current_depth > depth:
            return ""

        class_label = self.__get_label(class_uri)
        ontology_string = indent + class_label + "\n"

        if class_uri not in processed_classes:
            processed_classes.add(class_uri)
            subclasses = self.__get_subclasses(class_uri)
            for subclass in subclasses:
                ontology_string += self.__create_ontology_string(subclass, processed_classes, depth, current_depth + 1, indent + "  ")

        return ontology_string

    def create_ontology_representation(self, depth):
        root_class = OWL.Thing
        processed_classes = set()
        ontology_string = self.__create_ontology_string(root_class, processed_classes, depth)
        return ontology_string
    
    def __create_visualization_graph(self):
        visualization_graph = nx.DiGraph()
        root_class = OWL.Thing
        self.__add_nodes_recursive(visualization_graph, root_class, 0)
        return visualization_graph

    def __add_nodes_recursive(self, graph, node, depth):
        node_label = self.__get_label(node)
        graph.add_node(node_label, depth=depth)

        subclasses = list(self.ontology_graph.subjects(RDFS.subClassOf, node))
        for subclass in subclasses:
            subclass_label = self.__get_label(subclass)
            graph.add_edge(node_label, subclass_label)
            self.__add_nodes_recursive(graph, subclass, depth + 1)

    def __get_label(self, uri):
        label = self.ontology_graph.value(uri, RDFS.label)
        if label is None:
            label = uri.split("/")[-1].replace("_", " ")
        return str(label)

    def visualize_graph(self, depth):
        visualization_graph = self.__create_visualization_graph()

        # Filter the graph based on the selected depth
        filtered_nodes = [node for node, data in visualization_graph.nodes(data=True) if data['depth'] <= depth]
        filtered_graph = visualization_graph.subgraph(filtered_nodes)

        net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
        net.from_nx(filtered_graph)

        # Generate unique random colors for each depth level
        depth_colors = {}
        for node in filtered_graph.nodes():
            depth_level = filtered_graph.nodes[node]['depth']
            if depth_level not in depth_colors:
                while True:
                    color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
                    if color not in depth_colors.values():
                        depth_colors[depth_level] = color
                        break
            net_node = net.get_node(node)
            net_node['color'] = depth_colors[depth_level]

        net.repulsion(node_distance=420, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)
        html_file = net.generate_html()
        modified_html = html_file.replace('lib/bindings/utils.js', f'{settings.STATIC_URL}js/utils.js')
        return modified_html
    
    def abstract(self, depth):
        ontology_string = self.create_ontology_representation(depth)

        event_log_df = self.xes_df
        activities = event_log_df["activity"]

        messages = [
            {"role": "system", "content": p.IDENTIFY_CONTEXT},
            {"role": "user", "content": p.IDENTIFY_PROMPT + "\n" + "\n".join(activities)},
        ]
        relevant_activities = u.query_gpt(messages=messages, tools=fc.TOOLS, tool_choice={"type": "function", "function": {"name": "extract_medication_rows"}})
    
        filtered_df = event_log_df[event_log_df["activities"].isin(relevant_activities)]



        # for activity in relevant_activities:
        #     messages = [
        #         {"role": "system", "content": p.ABSTRACTION_CONTEXT},
        #         {"role": "user", "content": p.ABSTRACTION_PROMPT_1 + ontology_string + p.ABSTRACTION_PROMPT_2 + activity},
        #     ]
        #     answer = u.query_gpt(messages=messages)
        #     print(answer)

    def update_progress(self, view, current_step, module_name):
        """Update the progress of the extraction."""
        if view is not None:
            percentage = round(
                (current_step / len(self.get_configuration().modules)) * 100
            )
            view.request.session["progress"] = percentage
            view.request.session["status"] = module_name
            view.request.session.save()