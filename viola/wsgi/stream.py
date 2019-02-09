from viola.stream import TCPStream
from viola.exception import ViolaEventException
from viola.event_loop import EventLoop


class WSGIStream(TCPStream):
    def __init__(self, c_socket, event_loop, wsgi_handler, env, start_response,
                 keepalive=False):
        super(WSGIStream, self).__init__(c_socket, event_loop, keepalive)
        self.wsgi_handler = wsgi_handler
        self.env = env
        self.start_response = start_response

    def handle_event(self, fd, event):
        if event & EventLoop.READ:
            # print(1)
            self.handle_read()
            # 将读写处理完毕的 stream 丢给 `wsgi_handler()`
            if self.read_buffer or self.wrough_rebuff:
                self.read_from_buffer(self.read_buffer)
                # 暂时写死 wsgi handler
                resp_data = self.wsgi_handler(self.env, self.start_response)
                [self.write_buffer.append(x) for x in resp_data]
                # self.write_buffer.append(resp_data)
                # 设置写感兴趣事件
                self.event_loop.update_handler(self.c_socket.fileno(),
                                               EventLoop.WRITE)
                # 消费
                self.wrough_rebuff.popleft()
            # 由于读数据时是采取尽可能多的读, 尽量减少通知次数, 降低 CPU 使用. 没有使用把请求分开一个一个地读,
            # 所以当请求的数据量远远小于 chunk_size 时, 很容易会发生一次读就读了若干个请求数据, 剩下的读就绪事件没数据可以读,
            # 就会造成读就绪事件饥饿. 这里的 `break` 就是为了防止读就绪事件饥饿.
            # (现象就是大量饥饿的读就绪事件造成 CPU 飙高, 从而造成服务器无法处理后续的请求. 可以通过连续疯狂 ab 来重现这个现象)
            else:
                self.release()
        elif event & EventLoop.WRITE:
            # print(2)
            self.handle_write()
        # 怎么处理?
        elif event & EventLoop.ERROR:
            # print("epoll error, close it")
            self.release()
            raise
        else:
            self.release()
            raise ViolaEventException
