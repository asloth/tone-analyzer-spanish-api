from flask import Flask
from flask import request
import json
from analysis import find_tendencies

app = Flask(__name__)

@app.route("/")
def home():
    return "Bienvenidos a mi API "

@app.route("/analysis",methods=['POST'])
def analysis():
    values = request.get_json()
    result = find_tendencies(values['data'])
    return  json.dumps(result, indent=2)

if __name__ == "__main__":
    app.run()