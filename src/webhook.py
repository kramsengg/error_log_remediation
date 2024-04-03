from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/webhook', methods=['POST'])
def webhook():
    print("REQUEST : ", request)
    data = request.json
    print("Received alert:", data)
    # Here you can add code to process the error logs and send them to OpenAI API
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(port=6000, debug=True)