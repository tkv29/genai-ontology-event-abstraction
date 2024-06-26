# Standard Library Imports
import networkx as nx

# Third-Party Imports
from django.conf import settings
from pyvis.network import Network
from rdflib import Graph, RDFS, OWL
import pm4py

# Local Imports
from GOEA.logic import prompts as p
from GOEA.logic import utils as u

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
        self.data = None
        if xes_path and owl_path:
            self.xes_df = pm4py.read_xes(xes_path)
            self.ontology_graph = self._read_owl_file(owl_path)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            EventAbstractor()
        return cls._instance

    def get_xes_df(self):
        return self.xes_df

    def get_data(self):
        return self.data

    def _read_owl_file(self, file_path):
        ontology_graph = Graph()
        ontology_graph.parse(file_path)
        return ontology_graph

    def _get_subclasses(self, class_uri):
        return list(self.ontology_graph.subjects(RDFS.subClassOf, class_uri))

    def _get_class_depth(self, class_uri, depth=0):
        subclasses = self._get_subclasses(class_uri)
        if not subclasses:
            return depth
        return max(self._get_class_depth(subclass, depth + 1) for subclass in subclasses)

    def get_max_depth(self):
        root_class = OWL.Thing
        return self._get_class_depth(root_class)

    def _create_ontology_string(self, class_uri, processed_classes, selected_depth, current_depth=0, indent=""):
        ontology_string = ""
        if current_depth < selected_depth:
            if class_uri not in processed_classes:
                processed_classes.add(class_uri)
                subclasses = self._get_subclasses(class_uri)
                for subclass in subclasses:
                    ontology_string += self._create_ontology_string(
                        subclass, processed_classes, selected_depth, current_depth + 1, indent
                    )
        else:
            class_label = self._get_label(class_uri)
            ontology_string += indent + f"{current_depth}. " + class_label + "\n"
            if class_uri not in processed_classes:
                processed_classes.add(class_uri)
                subclasses = self._get_subclasses(class_uri)
                for subclass in subclasses:
                    ontology_string += self._create_ontology_string(
                        subclass, processed_classes, selected_depth, current_depth + 1, indent + " "
                    )
        return ontology_string

    def create_ontology_representation(self, selected_depth):
        root_class = OWL.Thing
        processed_classes = set()
        ontology_string = self._create_ontology_string(root_class, processed_classes, selected_depth)
        return ontology_string

    def _create_visualization_graph(self):
        visualization_graph = nx.DiGraph()
        root_class = OWL.Thing
        self._add_nodes_recursive(visualization_graph, root_class, 0)
        return visualization_graph

    def _add_nodes_recursive(self, graph, node, depth):
        node_label = self._get_label(node)
        graph.add_node(node_label, depth=depth)

        subclasses = list(self.ontology_graph.subjects(RDFS.subClassOf, node))
        for subclass in subclasses:
            subclass_label = self._get_label(subclass)
            graph.add_edge(node_label, subclass_label)
            self._add_nodes_recursive(graph, subclass, depth + 1)

    def _get_label(self, uri):
        label = self.ontology_graph.value(uri, RDFS.label)
        if label is None:
            label = uri.split("/")[-1].replace("_", " ")
        return str(label)

    def visualize_graph(self, abstraction_level):
        visualization_graph = self._create_visualization_graph()
        nodes_to_add = [node for node in visualization_graph.nodes() if str(node) != "owl#Thing"]

        net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
        net.from_nx(visualization_graph.subgraph(nodes_to_add))

        marked_nodes = {node for node, data in visualization_graph.nodes(data=True) if data['depth'] == abstraction_level}
        descendants = {descendant for node in marked_nodes for descendant in nx.descendants(visualization_graph, node)}

        for node in nodes_to_add:
            net_node = net.get_node(node)
            if node in marked_nodes:
                net_node['color'] = '#FF6A00'  # Orange color for target abstraction level
                net_node['size'] = 20
            elif node in descendants:
                net_node['color'] = '#0D6EFD'  # Blue for potential abstraction
            else:
                net_node['color'] = '#808080'  # Grey for not considered nodes

        for edge in net.edges:
            source, target = edge['from'], edge['to']
            if (source in marked_nodes and target in descendants) or (source in descendants and target in descendants):
                edge['color'] = '#0D6EFD'  # Blue for edges of potential abstraction
                edge['width'] = 2.5

        net.repulsion(node_distance=420, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)

        html_file = net.generate_html()
        modified_html = html_file.replace('lib/bindings/utils.js', f'{settings.STATIC_URL}js/utils.js')

        return modified_html

    def abstract(self, view, abstraction_level, custom_ontology_used):
        event_log_df = self.xes_df

        total_rows = len(event_log_df)
        event_log_df["medication"] = event_log_df.apply(lambda row: self._start_extraction_medication(row, view, total_rows), axis=1)

        event_log_df["normalized_medication"] = event_log_df.apply(lambda row: self._start_normalization_medication(row, view, total_rows), axis=1)
        ontology_string = self.create_ontology_representation(abstraction_level)
        total_rows = len(event_log_df)
        event_log_df["abstracted_medication"] = event_log_df.apply(
            lambda row: self._start_medication_abstraction(
                row, ontology_string, abstraction_level, custom_ontology_used, view, total_rows
            ),
            axis=1
        )

        self.data = event_log_df
        return event_log_df

    def _start_extraction_medication(self, row, view, total_rows):
        extracted_medication = self._extract_medication(row["activity"])
        row_number = row.name
        self._update_progress(view, row_number, total_rows, "Extracting Drug or Medicament of Activities")
        return extracted_medication
    
    def _start_normalization_medication(self, row, view, total_rows):
        normalized_medication = "N/A"
        if row["medication"] != "N/A":
            normalized_medication = self._normalize_medication(row["medication"])
        row_number = row.name
        self._update_progress(view, row_number, total_rows, "Normalizing Drug or Medicament of Extracted Medication")
        return normalized_medication
    
    def _start_medication_abstraction(self, row, ontology_string, abstraction_level, custom_ontology_used, view, total_rows):
        abstracted_medication = "N/A"
        medication = row["normalized_medication"]
        if medication != "N/A":
            abstracted_medication = self._abstract_medication(ontology_string, medication, abstraction_level, custom_ontology_used)
        row_number = row.name
        self._update_progress(view, row_number, total_rows, "Abstracting Drug Medicament on Target Abstraction Level")
        return abstracted_medication

    @staticmethod
    def _extract_medication(activity):
        extraction_messages = p.EXTRACTION_MESSAGES[:]
        extraction_messages.append(
            {
                "role": "user",
                "content": activity,
            }
        )
        extracted_medication = u.query_gpt(messages=extraction_messages)
        return extracted_medication
    
    @staticmethod
    def _normalize_medication(extracted_medication):
        extraction_messages = p.NORMALIZATION_MESSAGES[:]
        extraction_messages.append(
            {
                "role": "user",
                "content": extracted_medication,
            }
        )
        normalized_medication = u.query_gpt(messages=extraction_messages)
        return normalized_medication

    @staticmethod
    def _abstract_medication(ontology, medication, abstraction_level, custom_ontology_used):
        if custom_ontology_used:
            abstraction_messages = p.CUSTOM_ABSTRACTION_MESSAGES[:]
            abstraction_messages.extend([
                {
                    "role": "user",
                    "content": (
                        "Here the hierarchy you should use as reference: \n" + ontology +
                        "\n Classify the medication in one of the uppermost classes on the target abstraction level. "
                        "If it does not fit in any classes, return N/A. \n" +
                        "The target abstraction level should be: " + "'" + str(abstraction_level) + ".'"
                    ),
                },
                {
                    "role": "user",
                    "content": "In which category on abstraction level: " + str(abstraction_level) + " would " + medication + " fit in?",
                }
            ])
        else:
            abstraction_messages = p.ABSTRACTION_MESSAGES[:]
            abstraction_messages.extend([
                {
                    "role": "user",
                    "content": (
                        "Here the hierarchy you should use as reference: \n" + ontology +
                        "\n Check if the following medicine is part of the hierarchy and map them to the uppermost class on the target abstraction level. "
                        "If the term is not part of the hierarchy, return N/A. \n" +
                        "The target abstraction level should be: " + "'" + str(abstraction_level) + ".'"
                    ),
                },
                {
                    "role": "user",
                    "content": "What is the uppermost class of " + medication + " which is on the level: " + str(abstraction_level) + "?",
                }
            ])

        abstracted_medication = u.query_gpt(messages=abstraction_messages)
        return abstracted_medication

    def _update_progress(self, view, current_step, total_steps, status):
        """Update the progress of the extraction."""
        if view is not None:
            percentage = round((current_step / total_steps) * 100)
            view.request.session["progress"] = percentage
            view.request.session["status"] = status
            view.request.session.save()