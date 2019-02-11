from flask import Flask, render_template
# from flask import request


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("hello.tpl", name="tiger")
