Hi guys, viola is a epoll-based event loop http server.

# httpserver.py
1. 建立服务端 socket
2. 提供 handler 函数
3. 将 ss 注册到 event_loop  => event_loop.add_handler(ss, events, handler)

# event_loop.py
1. 提供 epoll_ctl 增删改的再次封装
2. 事件循环. 处理就绪的 fd  => self.handlers[fd](fd, events)