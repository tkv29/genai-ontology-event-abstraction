"""Module providing functions for using OpenAI function calling."""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extract_medication_rows",
            "description": "this function extracts only the relevant rows from a table which are related to medications",
            "parameters": {
                "type": "object",
                "properties": {
                    "output": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "a row from the table which is related to medications",
                        },
                    },
                },
                "required": ["output"],
            },
        },
    },
]