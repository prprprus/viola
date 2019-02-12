# viola

[![build status](https://travis-ci.org/prprprus/viola.svg?branch=master)](https://travis-ci.org/prprprus/viola.svg?branch=master)

viola is a WSGI server. Single-thread, non-blocking I/O based on event-driven model and has no dependencies other than the Python Standard Library. Usually used with Nginx.

# httpserver.py
1. 建立服务端 socket
2. 提供 handler 函数
3. 将 ss 注册到 event_loop  => event_loop.add_handler(ss, events, handler)

# event_loop.py
1. 创建 epfd
2. 提供 epoll_ctl 增删改的再次封装
3. 事件循环. 处理就绪的 fd  => self.handlers[fd](fd, events)

# 手尾
- ET 和 LT 对编码难度的影响
- `print()` 对程序性能的影响非常大

# 参考
- HTTP request: https://tools.ietf.org/html/rfc2616#section-5
- HTTP response: https://tools.ietf.org/html/rfc2616#section-6

# 目标
- 事件驱动的并发模型. 压测通过
- 解析 HTTP GET 请求
- keep-Alive

# 回归测试
- 无 keep-Alive
    - 小数据量
        ```
        response.write(resp_data)
        ab -n 5000 -c 5000 http://10.211.55.25:2333/listNews
        ```
    - 大数据量
        ```
        response.write(resp_data + b'{"result": "ok"}'*9999999)
        ab -n 10 -c 10 http://10.211.55.25:2333/listNews
        ```
- 有 keep-Alive
    - 小数据量
        ```
        response.write(resp_data)
        ab -n 5000 -c 5000 -k http://10.211.55.25:2333/listNews
        ```
    - 大数据量
        pass
- 加了 Nginx
    - siege -b -t60S -c1000 http://10.211.55.25


# 总结
1、Web框架会极大影响性能
2、Nginx 的 proxy_pass 只有在应用服务器返回正确的 HTTP 响应格式时, 才会自动添加响应头