from flask import Flask
# from flask import request


app = Flask(__name__)


resp_data = b"""
HTTP/1.1 200 OK
Server: viola

<h1>ok</h1>
"""


@app.route('/')
def hello_world():
    # print(request.path)
    # print(request.method)
    return resp_data
