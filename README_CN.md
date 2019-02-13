# viola

[![build status](https://travis-ci.org/prprprus/viola.svg?branch=master)](https://travis-ci.org/prprprus/viola.svg?branch=master) [![pip version](https://img.shields.io/badge/pip-v18.1-blue.svg)](https://img.shields.io/badge/pip-v18.1-blue.svg) [![license](https://img.shields.io/dub/l/vibe-d.svg)](./LICENSE)

[英文](https://github.com/prprprus/viola/blob/master/README.md)

viola 是一个 WSGI 服务器. 轻量级、高效并且没有 Python 标准库之外的其他依赖. 通常以 Nginx 为反向代理搭配使用.

目录:

- [功能](https://github.com/prprprus/viola#features)
- [使用条件](https://github.com/prprprus/viola#requirements)
- [安装](https://github.com/prprprus/viola#installation)
- [例子](https://github.com/prprprus/viola#example)
- [性能](https://github.com/prprprus/viola#performance)
- [TODO](https://github.com/prprprus/viola#todo)
- [参考](https://github.com/prprprus/viola#resources)
- [License](https://github.com/prprprus/viola#license)
- [参与贡献](https://github.com/prprprus/viola#contributing)

## 功能

+ [x] 基于事件驱动模型的单线程, 非阻塞 I/O
+ [x] 简易版的服务端 WSGI 协议
+ [x] 秒级定时器
+ [x] 针对 HTTP GET 方法的解析器

## 使用条件

- Python
    - CPython >= 3.6
- Platform
    - Linux and kernel >= 2.6

## 安装

安装包已经上传到了 [PyPI](https://pypi.org/project/viola/)

你可以使用 pip 进行安装

```
$ pip install viola
```

## 例子

这样使用 viola:

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

就是这么简单.

## 性能

下面测试中的 Nginx 都是反向代理一个对应的 WSGI 服务器. Nginx 的配置文件一致并且 WSGI 服务器都是响应一个 "Hello World" 字符串.

```
CPU: 2.7 GHz Intel Core i5
MEM: 8 GB 1867 MHz DDR3
```

```
ab -n 10000 -c 500 http://10.211.55.25/
```

#### Nginx + Tornado(Tornado 同时作为 WSGI 服务器和 Web 框架. Tornado 以单进程形式启动)

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

#### Nginx + Gunicorn(启动 4 个 workers 并且使用默认的 sync 模式) + bottle

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

#### Nginx + viola(viola 以但进程形式启动) + bottle

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

+ [ ] 完善服务端的 WSGI 协议实现
+ [ ] 定时器从秒级升级到毫秒级
+ [ ] 解析 HTTP POST 方法等等
+ [ ] 完善响应功能模块
+ [ ] 支持更多平台的事件驱动模型
+ [ ] 提高测试覆盖率

## 参考

- [EPOLL(7)](http://man7.org/linux/man-pages/man7/epoll.7.html)
- [How To Use Linux epoll with Python](http://scotdoyle.com/python-epoll-howto.html)
- [Python Standard Library](https://docs.python.org/3/library/index.html)
- [An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [RFC 2616 -- HTTP GET method](https://tools.ietf.org/html/rfc2616#section-9.3)
- [PEP 333](https://www.python.org/dev/peps/pep-0333/#environ-variables)
- [Tornado](https://www.tornadoweb.org/en/stable/#)
- [Gunicorn](http://docs.gunicorn.org/en/latest/index.html)

## License

viola 遵循 MIT 开源协议. 详情参考 [LICENSE](https://github.com/prprprus/viola/blob/master/LICENSE).

## 参与贡献

非常感谢你对 viola 的关注, 你的关注和贡献是对于我来说非常宝贵的.

你可以通过提交 issue 和 pull requests 来参与其中, 但是请先提交 issue 再 pull requests.
