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

    def __create_ontology_string(self, class_uri, processed_classes, selected_depth, current_depth=0, indent=""):
        ontology_string = ""
        if current_depth < selected_depth:
            if class_uri not in processed_classes:
                processed_classes.add(class_uri)
                subclasses = self.__get_subclasses(class_uri)
                for subclass in subclasses:
                    ontology_string += self.__create_ontology_string(subclass, processed_classes, selected_depth, current_depth + 1, indent)
        else:
            class_label = self.__get_label(class_uri)
            ontology_string += indent + f"{current_depth}. " + class_label + "\n"
            if class_uri not in processed_classes:
                processed_classes.add(class_uri)
                subclasses = self.__get_subclasses(class_uri)
                for subclass in subclasses:
                    ontology_string += self.__create_ontology_string(subclass, processed_classes, selected_depth, current_depth + 1, indent + " ")
        return ontology_string

    def create_ontology_representation(self, selected_depth):
        root_class = OWL.Thing
        processed_classes = set()
        ontology_string = self.__create_ontology_string(root_class, processed_classes, selected_depth)
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

    def visualize_graph(self, abstraction_level):
        visualization_graph = self.__create_visualization_graph()
        nodes_to_add = [node for node in visualization_graph.nodes() if str(node) != "owl#Thing"]
        
        net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
        net.from_nx(visualization_graph.subgraph(nodes_to_add))
        
        marked_nodes = set(node for node, data in visualization_graph.nodes(data=True) if data['depth'] == abstraction_level)
        descendants = set(descendant for node in marked_nodes for descendant in nx.descendants(visualization_graph, node))
        
        for node in nodes_to_add:
            net_node = net.get_node(node)
            if node in marked_nodes:
                net_node['color'] = '#8B0000'  # Red color for target abstraction level
            elif node in descendants:
                net_node['color'] = '#008000'  # Green for potential abstraction
        
        for edge in net.edges:
            source, target = edge['from'], edge['to']
            if (source in marked_nodes and target in descendants) or (source in descendants and target in descendants):
                edge['color'] = '#008000'  # Green for edges of potential abstraction
                edge['width'] = 3  
            else:
                edge['width'] = 1  
        
        net.repulsion(node_distance=420, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)
        html_file = net.generate_html()
        modified_html = html_file.replace('lib/bindings/utils.js', f'{settings.STATIC_URL}js/utils.js')
        
        return modified_html
    
    def abstract(self, view, abstraction_level):
        event_log_df = self.xes_df
        activities = event_log_df["activity"]

        self.update_progress(view, 0, "Identifying relevant activities related to medications")

        relevant_activities = self.__identify_relevant_activities(activities)
        relevant_activities_df = event_log_df[event_log_df["activity"].isin(relevant_activities)]

        self.update_progress(view, 1, "Extracting Medication Names from Relevant Activities")
        relevant_activities_df["medication"] = relevant_activities_df["activity"].apply(self.__extract_medication)

        self.update_progress(view, 2, "Abstracting medication names")
        ontology_string = self.create_ontology_representation(abstraction_level)
        relevant_activities_df["abstracted_medication"] = relevant_activities_df["medication"].apply(
            lambda medication: self.__abstract_medication(ontology_string, medication, abstraction_level)
        )

        self.update_progress(view, 3, "Finished")
        return relevant_activities_df


    @staticmethod
    def __identify_relevant_activities(activities):
        identify_messages = p.IDENTIFY_MESSAGES[:]
        identify_messages.append(
            {
                "role": "user",
                "content": activities.to_string(),
            }
        )
        relevant_activities = u.query_gpt(
            messages=identify_messages,
            tools=fc.TOOLS,
            tool_choice={"type": "function", "function": {"name": "extract_medication_rows"}}
        )
        return relevant_activities

    @staticmethod
    def __extract_medication(activity):
        extraction_messages = p.EXTRACTION_MESSAGES[:]
        extraction_messages.append(
            {
                "role": "user",
                "content": activity,
            }
        )
        medication = u.query_gpt(messages=extraction_messages)
        return medication
    
    @staticmethod
    def __abstract_medication(ontology, medication, abstraction_level):
        abstraction_messages = p.ABSTRACTION_MESSAGES[:]
        abstraction_messages.extend([
            {
                "role": "user",
                "content": "Here the hierachy you should use as reference: \n" + ontology + "\n Check if the following medicine is part of the hierarchy and map them to the uppermost class on the target abstraction level. If the term is not part of the hierarchy, return N/A. \n" + "The target abstraction level should be: " + "'" +str(abstraction_level) + ".'" ,
            },
            {
                "role": "user",
                "content": "What is the uppermost class of " + medication + "?",
            }
        ])

        abstracted_medication = u.query_gpt(messages=abstraction_messages)
        return abstracted_medication

    def update_progress(self, view, current_step, module_name):
        """Update the progress of the extraction."""
        if view is not None:
            percentage = round(
                (current_step / 3) * 100
            )
            view.request.session["progress"] = percentage
            view.request.session["status"] = module_name
            view.request.session.save()