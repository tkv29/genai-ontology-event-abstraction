from rdflib import Graph, RDFS, OWL
from . import utils as u
from . import prompts as p
from . import function_calls as fc

class EventAbstractor:
    """Singleton class that abstracts events from a XES file using an ontology file."""

    _instance = None

    def __init__(self, xes_df=None, owl_content=None):
        self.set_xes_df(xes_df)
        self.set_owl_content(owl_content)

    def set_xes_df(self, xes_df):
        self.xes_df = xes_df
    
    def set_owl_content(self, owl_content):
        self.owl_content = owl_content

    def get_xes_df(self):
        return self.xes_df
    
    def get_owl_content(self):
        return self.owl_content
    
    @classmethod
    def get_instance(cls):
        return cls._instance
    

    def abstract(self):
        """Abstracts events from the XES file using the ontology file."""
        xes_df = self.get_xes_df()
        owl_content = self.get_owl_content()
        
        # Process the XES and OWL files
        # ...
        
        # Return the abstracted events
        return xes_df

    def read_owl_content(self, file_path):
        g = Graph()
        g.parse(file_path)
        return g

    def get_subclasses(self, graph, class_uri):
        return list(graph.subjects(RDFS.subClassOf, class_uri))

    def get_class_depth(self, graph, class_uri, depth=0):
        subclasses = self.get_subclasses(graph, class_uri)
        if not subclasses:
            return depth
        return max(self.get_class_depth(graph, subclass, depth + 1) for subclass in subclasses)

    def create_level_dictionary(self, graph, class_uri, level_dict, depth=0):
        if depth not in level_dict:
            level_dict[depth] = []
        level_dict[depth].append(class_uri)
        subclasses = self.get_subclasses(graph, class_uri)
        for subclass in subclasses:
            self.create_level_dictionary(graph, subclass, level_dict, depth + 1)

    def create_ontology_string(self, level_dict, processed_classes, indent=0):
        ontology_string = ""
        for level in sorted(level_dict.keys()):
            for class_uri in level_dict[level]:
                if class_uri not in processed_classes:
                    processed_classes.add(class_uri)
                    class_label = class_uri.split("/")[-1].replace("_", " ")
                    ontology_string += " " * indent + "-" * bool(indent) + class_label + "\n"
                    subclasses = self.get_subclasses(g, class_uri)
                    if subclasses:
                        ontology_string += self.create_ontology_string({level + 1: subclasses}, processed_classes, indent + 1)
        return ontology_string

    