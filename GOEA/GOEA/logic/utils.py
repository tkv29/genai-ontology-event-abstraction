# Standard Library Imports
import json
import os

# Third-Party Imports
import pandas as pd
import pm4py
from django.conf import settings
from openai import OpenAI

# Local Imports
from GOEA.logic import function_calls

OAIK = os.environ.get("OPENAI_API_KEY")  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
TEMPERATURE_SUMMARIZING = 0
TEMPERATURE_CREATION = 1


def query_gpt(messages, max_tokens=MAX_TOKENS, temperature=TEMPERATURE_SUMMARIZING,
              tools=None, tool_choice="none", logprobs=False, top_logprobs=None):
    """Sends a request to the OpenAI API and returns the response."""
    tools = function_calls.TOOLS if tools is None else tools

    def make_api_call():
        """Queries the GPT engine."""
        client = OpenAI(api_key=OAIK)
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
        )
        return response

    response = make_api_call()

    if tool_choice != "none":
        api_response = response.choices[0].message.tool_calls[0].function.arguments
        output = json.loads(api_response)["output"]
    elif logprobs:
        top_logprobs = response.choices[0].logprobs.content[0].top_logprobs
        content = response.choices[0].message.content
        return content, top_logprobs
    else:
        output = response.choices[0].message.content
    return output


def dataframe_to_xes(df, name):
    """Conversion from dataframe to xes file."""
    # Convert 'start' and 'end' columns to datetime
    df["start_timestamp"] = pd.to_datetime(df["start_timestamp"])
    
    # Renaming columns for Disco
    df.rename(
        columns={
            "start_timestamp": "time:timestamp",  # Disco takes time:timestamp as timestamp key
            "medication_abstracted": "concept:name",  # We want Disco to take medications as activities
        },
        inplace=True,
    )
    
    # Sorting Dataframe by start timestamp
    df = df.sort_values("time:timestamp")
    
    # Converting DataFrame to XES
    parameters = {
        pm4py.objects.conversion.log.converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: "case:concept:name"
    }
    event_log = pm4py.objects.conversion.log.converter.apply(df, parameters=parameters)
    
    output_path = settings.BASE / "GOEA/content/"
    xes_file = output_path / name
    pm4py.write_xes(
        event_log,
        xes_file,
        activity_key="activity",
        case_id_key="case:concept:name",
        timestamp_key="time:timestamp",
    )
    
    return xes_file