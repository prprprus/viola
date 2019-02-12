# viola

[![build status](https://travis-ci.org/prprprus/viola.svg?branch=master)](https://travis-ci.org/prprprus/viola.svg?branch=master)

viola is a WSGI server. Lightweight and efficient and has no dependencies other than the Python Standard Library. Usually used with Nginx.

Table of content

- Features
- Requirements
- Installation
- Example
- Performance
- TODO
- Resources
- License
- Contributing

## Features

+ [x] Single-thread, non-blocking I/O based on event-driven model
+ [x] Simplified WSGI protocol for server side
+ [x] Second timer
+ [x] A parser for HTTP GET method

## Requirements

- Python
    - CPython >= 3.6
- Platform
    - Linux and kernel >= 2.6

## Installation

Package is uploaded on [PyPI](https://pypi.org/project/pymysql-pooling/)

You can install with pip

```
$ pip install viola
```

## Example

Run viola as follows:

```python
from viola.core.event_loop import EventLoop
from viola.wsgi.server import WSGIServer
from viola.core.scheduler import Scheduler
# Import your APP in here


if __name__ == '__main__':
    event_loop = EventLoop.instance(Scheduler.instance())
    server = WSGIServer(event_loop)
    server.set_wsgi_app(APP)    # For example the APP argument is flask or bottle
    server.bind(host=HOST, port=PORT)   # Replace your real host and real port
    server.listen()
    server.start(1)
    event_loop.start()
```

That's all.

## Performance

#### Nginx + Tornado(Tornado as both a WSGI server and Web framework)

```
```

#### Nginx + viola + bottle

```
```

## TODO

+ [] Improved WSGI protocol
+ [] Millisecond timer
+ [] HTTP POST method and more
+ [] Improved response module

### Resources

- xxx

## License

viola is released under the MIT License. See LICENSE for more information.

## Contributing

Thank you for your interest in contribution of viola, your help and contribution is very valuable. 

You can submit issue and pull requests, please submit an issue before submitting pull requests.
