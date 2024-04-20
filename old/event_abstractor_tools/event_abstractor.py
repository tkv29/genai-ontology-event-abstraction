import pm4py
import pandas as pd




def abstract(xes, ontology):
    dataframe = pm4py.read_xes(xes)
    dataframe = pm4py.format_dataframe(dataframe, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')

    return dataframe



def convert_owl_to_hierachy(ontology):
    
    
    
    
    
    return ontology 


