from flask import Flask
from flask import request


app = Flask(__name__)


resp_data = b"""
HTTP/1.1 200 OK

{"result": "ok"}
"""


@app.route('/listNews')
def hello_world():
    # print("fuxk")
    # print(request.path)
    # print(request.method)
    # print("fuxk")
    return resp_data
