IDENTIFY_MESSAGES = [
  {
    "role": "system",
    "content": """You are a medication identifier system. Your task is to take a table as input and return only the rows containing information related to medications. 
    A row is considered related to medications if it contains the name about a specific medication."""
  },   
  {
      "role": "user",
      "content": "Please extract only the rows which contain information about specifc mediactions. Discard all other rows. Here are the rows from the table:"
  }
]

EXTRACTION_MESSAGES = [
    {
        "role": "system",
        "content": "You are a medication extraction system. Your task is to take a sentence as input and return only the medication name mentioned in the sentence. If no medication is mentioned, return 'NA'."
    },
    {
        "role": "user",
        "content": "Please extract the medication name from the following sentence:"
    },
    {
        "role": "user",
        "content": "3 weeks I took Leflunomide."
    },
    {
        "role": "assistant",
        "content": "Leflunomide"
    },
    {
        "role": "user",
        "content": "Aspirin was prescribed to me"
    },
    {
        "role": "assistant",
        "content": "Aspirin"
    },
    {
        "role": "user",
        "content": "I combined some medications."
    },
    {
        "role": "assistant",
        "content": "N/A"
    },
]

ABSTRACTION_MESSAGES =[
    {
        "role": "system",
        "content": """You are an hierachy expert. Given a medication hierachy, a target abstraction level (number) and a medication, return the upper class on the target abstraction level of the given medication. 
        That means if the term is part of the hierachy map it to the target abstraction level in the hierachy. If the medication is not part of the hierachy, output 'N/A'.""",
    },
    {
        "role": "user",
        "content": """
        Here is the hierachy you should use as reference:
        2. Non-steroidal anti-inflammatory agent
          3. Ketorolac trometamol
          3. Mefenamate
          3. Meclofenamate
            4. Meclofenamate sodium
          3. Meclofenamic acid
          3. Ibuprofen
        2. Antineoplastic agent
          3. Methotrexate
        2. Immunosuppressant
          3. Azathioprine
          3. Ciclosporin
          3. Leflunomide
        2. Antirheumatic agent
          3. Hydroxychloroquine
          3. Penicillamine
          3. Sulfasalazine
        2. Adrenal cortex hormone
          3. Prednisone
          3. Methylprednisolone
          3. Triamcinolone

        Check if the following medicine is part of the hierarchy and map them to the uppermost class on the target abstraction level. If the term is not part of the hierarchy, return N/A.

        The target abstraction level should be: "2." """
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Ibuprofen?"
    },
    {
        "role": "assistant",
        "content": "Non-steroidal anti-inflammatory agent"
    
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Methotrexate?"
    },
    {
        "role": "assistant",
        "content": "Antineoplastic agent"
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Celecoxib?"
    },
    {
        "role": "assistant",
        "content": "N/A"
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Meclofenamic acid?"
    },
    {
        "role": "assistant",
        "content": "Non-steroidal anti-inflammatory agent"
    },
    {
        "role": "user",
        "content": """Here is hierachy you should use as reference:
          1. Drug or medicament
            2. Non-steroidal anti-inflammatory agent
              3. Bromfenac sodium
              3. Meclofenamate
                4. Meclofenamate sodium
                4. Meclofenamic acid
            2. Antineoplastic agent
              3. Methotrexate
            2. Immunosuppressant
              3. Azathioprine
              3. Ciclosporin
            2. Antirheumatic agent
              3. Hydroxychloroquine
              3. Sulfasalazine
            2. Adrenal cortex hormone
              3. Prednisone
        
        Check if the following medicine is part of the hierarchy and map them to the uppermost class on the target abstraction level. If the term is not part of the hierarchy, return N/A.

        The target abstraction level should be: "1." """
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Meclofenamic acid?"
    },
    {
        "role": "assistant",
        "content": "Drug or medicament"
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Prednisone?"
    },
    {
        "role": "assistant",
        "content": "Drug or medicament"
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Celecoxib?"
    },
    {
        "role": "assistant",
        "content": "N/A"
    },
    {
        "role": "user",
        "content": "What is the uppermost class of Non-steroidal anti-inflammatory agent?"
    },
    {
        "role": "assistant",
        "content": "Drug or medicament"
    },
]

CUSTOM_ABSTRACTION_MESSAGES = [
]