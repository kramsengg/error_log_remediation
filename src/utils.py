import os
import time
from openai import OpenAI
from flask import jsonify
import json

GPT_MODEL = "gpt-3.5-turbo"

client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")

prompt_for_error_log_remediation = "List out the best possible remediations for the following error logs: "

def display(*objs, **kwargs):
  """
  Prints objects to the console.

  Args:
    *objs: Objects to be printed.
    **kwargs: Additional keyword arguments for formatting (e.g., rich library).
  """

  print(*objs, **kwargs)

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

def create_assistant_and_get_id(client):
    return client.beta.assistants.create(
        name="ERROR Log Remediation",
        description="This assistant will help to find out the remediation for the error logs",
        model=GPT_MODEL,
        tools=[{"type": "code_interpreter"}]
    ).id

def submit_message(client,assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=prompt_for_error_log_remediation + user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(client,thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(client,DOCU_ASSISTANT_ID,user_input):
    thread = client.beta.threads.create()
    run = submit_message(client,DOCU_ASSISTANT_ID, thread, user_input)
    return thread, run

# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

# Waiting in a loop
def wait_on_run(client,run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def create_environment_variable(variable_name, variable_value):
    """
    Create a new environment variable.

    Args:
    - variable_name (str): Name of the environment variable.
    - variable_value (str): Value to assign to the environment variable.
    """
    os.environ[variable_name] = variable_value
    print(f"Created environment variable: {variable_name}={variable_value}")

def delete_environment_variable(variable_name):
    """
    Delete an existing environment variable.

    Args:
    - variable_name (str): Name of the environment variable to delete.
    """
    if variable_name in os.environ:
        del os.environ[variable_name]
        print(f"Deleted environment variable: {variable_name}")
    else:
        print(f"Environment variable {variable_name} does not exist.")


def get_remediations_for_error(client,DOCU_ASSISTANT_ID,query):
    # Emulating concurrent user requests
        thread, run = create_thread_and_run(client,DOCU_ASSISTANT_ID,
            query
        )
        # Wait for Run 1
        run = wait_on_run(client,run, thread)
        pretty_print(get_response(client,thread))

        data = get_response(client,thread)
        serialized_data = serialize_data(data)
        print("data RESPONSE ", serialized_data)

        return serialized_data

def serialize_data(data):
    # Convert the object to a JSON-serializable format
    serializable_data = {
        'data': [
            {
                'id': message.id,
                'assistant_id': message.assistant_id,
                'content': [
                    {
                        'text': content.text.value,
                        'type': content.type
                    } for content in message.content
                ],
                'created_at': message.created_at,
                'file_ids': message.file_ids,
                'metadata': message.metadata,
                'object': message.object,
                'role': message.role,
                'run_id': message.run_id,
                'thread_id': message.thread_id
            } for message in data.data
        ],
        'object': data.object,
        'first_id': data.first_id,
        'last_id': data.last_id,
        'has_more': data.has_more
    }

    return serializable_data