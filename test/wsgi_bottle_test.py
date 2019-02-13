import bottle


@bottle.route('/')
def hello_world():
    # return '<html><head></head><body>Hello world!</body></html>'
    return "Hello, world"


app = bottle.default_app()
