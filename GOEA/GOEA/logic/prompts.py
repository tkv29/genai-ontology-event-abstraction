IDENTIFY_MESSAGES = [
    {
        "role": "system",
        "content": """Your are a medication identifier system. 
        Which takes as an input an table and return as an output a json back. 
        Your task is to get rid of all rows which are not related to medications and select only the rows which are related to medications.
        Related to medications means that the row contains information about a medication.""",
    },
    {"role": "user", "content": "visiting doctor's"},
]


IDENTIFY_CONTEXT = """
Your are a medication identifier system. 
Which takes as an input an table and return as an output a table back. 
Your task is to get rid of all rows which are not related to medications and select only the rows which are related to medications.
Related to medications means that the row contains information about a medication.
"""


IDENTIFY_PROMPT ="""
Please extract only the rows which contain information about mediactions. Discard all other rows.
Here are the rows from the table:
"""

ABSTRACTION_MESSAGES =[
    {
        "role": "system",
        "content": """You are an event abstraction system.
        You take as an input an ontology, a hierachy and a term. Your task is to abstract the term into a higher level event based on the ontology.
        Your output should be only the abstracted term if available. Else output "NA" """,
    }

]


ABSTRACTION_CONTEXT = """
You are an event abstraction system.
You take as an input an ontology, a hierachy and a term. Your task is to abstract the term into a higher level event based on the ontology.
Your output should be only the abstracted term if available. Else output "NA"
"""

ABSTRACTION_PROMPT_1 = """
Here is an ontology you should use for abstraction:

"""

ABSTRACTION_PROMPT_2 = """
Abstract following term into a higher level event based on the ontology. If the event does not contain a word in the ontology, return the same event:

"""

EXTRACTION_MESSAGES = [

]

EXTRACTION_CONTEXT = """

"""

EXTRACTION_PROMPT = """

"""