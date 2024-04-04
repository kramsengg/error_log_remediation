from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import utils
from openai import OpenAI
import json
import logging

app = Flask(__name__)
CORS(app)

# Set up the logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")

# global DOCU_ASSISTANT_ID
DOCU_ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

@app.route("/")
def hello():
    try:
        print("Hello World!")
        logging.info("Hello World!")
        return "Hello World!"
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return "Error occurred"
    
@app.route("/filecheck")
def file_throw_error():
    try:
        # Attempt to open a non-existent file
        with open('non_existent_file.txt', 'r') as file:
            data = file.read()
        logging.info("File contents: " + data)
        return "File Exists"
    except FileNotFoundError as error:
        print('The file does not exist.')
        logging.error(str(error))
        return "File does not exist"

@app.route('/webhook', methods=['POST'])
def webhook():
    global DOCU_ASSISTANT_ID
    if DOCU_ASSISTANT_ID is None:
        DOCU_ASSISTANT_ID = utils.create_assistant_and_get_id(client)
        utils.create_environment_variable("ASSISTANT_ID", DOCU_ASSISTANT_ID)
        print("OS ENV VALUE: ", os.environ.get("ASSISTANT_ID")) 
    
    print("REQUEST : ", request)
    data = request.json
    print("Received alert:", data)
    query = request.json['body']
    print("BODY Content :", query)
    query1 = """
        [Sun Jul 09 03:25:02 2017] [notice] Apache/2.2.32 (Unix) DAV/2 configured -- resuming normal operations
        [Sun Jul 09 04:06:13 2017] [error] [client 1.2.3.4] File does not exist: /var/www/html/robots.txt
        [Mon Jul 10 20:24:52 2017] [error] (111)Connection refused: proxy: HTTP: attempt to connect to 127.0.0.1:8484 (localhost) failed
    """
    # Here you can add code to process the error logs and send them to OpenAI API
    response_data = utils.get_remediations_for_error(client,DOCU_ASSISTANT_ID, query)
    return jsonify(response_data)
    #return jsonify(success=True)

@app.route('/get_remediations', methods=['POST'])
def get_remediations_error_logs():
    print("REQUEST : ", request)
    data = request.json
    print("Received alert:", data)
    # Here you can add code to process the error logs and send them to OpenAI API
    # Your search logic here
    query = request.json['body']
    #Sample Error logs:
    query1 = """
        [Sun Jul 09 03:25:02 2017] [notice] Apache/2.2.32 (Unix) DAV/2 configured -- resuming normal operations
        [Sun Jul 09 04:06:13 2017] [error] [client 1.2.3.4] File does not exist: /var/www/html/robots.txt
        [Mon Jul 10 20:24:52 2017] [error] (111)Connection refused: proxy: HTTP: attempt to connect to 127.0.0.1:8484 (localhost) failed
    """
    print("BODY Content :", query)
    global DOCU_ASSISTANT_ID
    if DOCU_ASSISTANT_ID is None:
        DOCU_ASSISTANT_ID = utils.create_assistant_and_get_id(client)
        utils.create_environment_variable("ASSISTANT_ID", DOCU_ASSISTANT_ID)
        print("OS ENV VALUE: ", os.environ.get("ASSISTANT_ID"))        
    
        response_data = utils.get_remediations_for_error(client,DOCU_ASSISTANT_ID, query)
        # Serialize the data to JSON
        #json_data = json.dumps(serialized_data, indent=2)
        return jsonify(response_data)
        #return jsonify(success=True)


if __name__ == '__main__':
    app.run(port=6000, debug=True)