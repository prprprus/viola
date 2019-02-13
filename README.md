# viola

[![build status](https://travis-ci.org/prprprus/viola.svg?branch=master)](https://travis-ci.org/prprprus/viola.svg?branch=master) [![pip version](https://img.shields.io/badge/pip-v18.1-blue.svg)](https://img.shields.io/badge/pip-v18.1-blue.svg) [![license](https://img.shields.io/dub/l/vibe-d.svg)](./LICENSE)

[中文](https://github.com/prprprus/viola/blob/master/README_CN.md)

viola is a WSGI server. Lightweight and efficient and has no dependencies other than the Python Standard Library. Usually used with Nginx.

Table of content:

- [Features](https://github.com/prprprus/viola#features)
- [Requirements](https://github.com/prprprus/viola#requirements)
- [Installation](https://github.com/prprprus/viola#installation)
- [Example](https://github.com/prprprus/viola#example)
- [Performance](https://github.com/prprprus/viola#performance)
- [TODO](https://github.com/prprprus/viola#todo)
- [Reference](https://github.com/prprprus/viola#reference)
- [License](https://github.com/prprprus/viola#license)
- [Contributing](https://github.com/prprprus/viola#contributing)

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

Package is uploaded on [PyPI](https://pypi.org/project/viola/)

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

The following nginx are load balanced with one WSGI server. Nginx configuration is consistent and the WSGI server response a string "Hello World".

```
CPU: 2.7 GHz Intel Core i5
MEM: 8 GB 1867 MHz DDR3
```

```
ab -n 10000 -c 500 http://10.211.55.25/
```

#### Nginx + Tornado(Tornado as both a WSGI server and Web framework. Tornado start one process.)

```
$ ab -n 10000 -c 500 http://10.211.55.25/
This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 10.211.55.25 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        nginx/1.15.8
Server Hostname:        10.211.55.25
Server Port:            80

Document Path:          /
Document Length:        12 bytes

Concurrency Level:      500
Time taken for tests:   31.186 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      2190000 bytes
HTML transferred:       120000 bytes
Requests per second:    320.65 [#/sec] (mean)
Time per request:       1559.316 [ms] (mean)
Time per request:       3.119 [ms] (mean, across all concurrent requests)
Transfer rate:          68.58 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   3.3      0      20
Processing:    13  797 3684.3    121   31161
Waiting:        9  797 3684.3    121   31161
Total:         28  798 3686.2    122   31170

Percentage of the requests served within a certain time (ms)
  50%    122
  66%    132
  75%    141
  80%    149
  90%    168
  95%   1002
  98%  15038
  99%  15135
 100%  31170 (longest request)
```

#### Nginx + Gunicorn(workers 4 and use sync mode by default) + bottle

```
$ ab -n 10000 -c 500 http://10.211.55.25/
This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 10.211.55.25 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        nginx/1.15.8
Server Hostname:        10.211.55.25
Server Port:            80

Document Path:          /
Document Length:        12 bytes

Concurrency Level:      500
Time taken for tests:   15.113 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      1690000 bytes
HTML transferred:       120000 bytes
Requests per second:    661.67 [#/sec] (mean)
Time per request:       755.662 [ms] (mean)
Time per request:       1.511 [ms] (mean, across all concurrent requests)
Transfer rate:          109.20 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   3.0      0      21
Processing:    13  407 1826.5     57   15085
Waiting:       13  407 1826.5     57   15085
Total:         30  408 1827.8     57   15091

Percentage of the requests served within a certain time (ms)
  50%     57
  66%     62
  75%     81
  80%     91
  90%    120
  95%   1063
  98%   7065
  99%  15056
 100%  15091 (longest request)
```

#### Nginx + viola(viola start one process) + bottle

```
$ ab -n 10000 -c 500 http://10.211.55.25/
This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 10.211.55.25 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        nginx/1.15.8
Server Hostname:        10.211.55.25
Server Port:            80

Document Path:          /
Document Length:        12 bytes

Concurrency Level:      500
Time taken for tests:   3.090 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      1290000 bytes
HTML transferred:       120000 bytes
Requests per second:    3236.64 [#/sec] (mean)
Time per request:       154.481 [ms] (mean)
Time per request:       0.309 [ms] (mean, across all concurrent requests)
Transfer rate:          407.74 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   3.0      0      22
Processing:     1  133 532.0     23    3042
Waiting:        1  133 532.0     23    3042
Total:          9  134 533.3     24    3053

Percentage of the requests served within a certain time (ms)
  50%     24
  66%     28
  75%     35
  80%     39
  90%     50
  95%     67
  98%   3016
  99%   3037
 100%   3053 (longest request)
```

## TODO

+ [ ] Improved WSGI protocol
+ [ ] Millisecond timer
+ [ ] HTTP POST method and more
+ [ ] Improved response module
+ [ ] Improved response module
+ [ ] Event driven for more platforms
+ [ ] Improved coverage

### Reference

- [EPOLL(7)](http://man7.org/linux/man-pages/man7/epoll.7.html)
- [How To Use Linux epoll with Python](http://scotdoyle.com/python-epoll-howto.html)
- [Python Standard Library](https://docs.python.org/3/library/index.html)
- [An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [RFC 2616 -- HTTP GET method](https://tools.ietf.org/html/rfc2616#section-9.3)
- [PEP 333](https://www.python.org/dev/peps/pep-0333/#environ-variables)
- [Tornado](https://www.tornadoweb.org/en/stable/#)
- [Gunicorn](http://docs.gunicorn.org/en/latest/index.html)

## License

viola is released under the MIT License. See [LICENSE](https://github.com/prprprus/viola/blob/master/LICENSE) for more information.

## Contributing

Thank you for your interest in contribution of viola, your help and contribution is very valuable. 

You can submit issue and pull requests, please submit an issue before submitting pull requests.
