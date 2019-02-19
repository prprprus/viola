from viola.core.stream import TCPStream
from viola.exception import ViolaEventException
from viola.core.event_loop import EventLoop
from viola.http.parser import Parser
from viola.http.wrapper import Wrapper
import logging


class WSGIStream(TCPStream):
    def __init__(self, c_socket, event_loop, wsgi_handler, start_response):
        super(WSGIStream, self).__init__(c_socket, event_loop)
        self.wsgi_handler = wsgi_handler
        self.start_response = start_response

    def handle_event(self, fd, event):
        """Handle already event for connection socket"""
        if event & EventLoop.READ:
            self.handle_read()
            if self.read_buffer:

                # 是否已经读取了完整的请求? 是则往下执行
                pass

                # 为什么这里只消费了一个 HTTP 请求, 最终却能把所有的请求都处理完?
                # 因为 LT. 只有将所有请求都处理了(也就是将读就绪事件都改成写感兴趣), LT 才不会通知, 不然它会一直通知.
                # Parse request
                p = Parser(self.read_buffer, self.processed_buffer)
                env = p.get_environ()
                # Run wsgi handler
                resp_data = self.wsgi_handler(env, self.start_response)
                # Wrapper response
                [self.write_buffer.append(Wrapper(x, env).get_resp()) for x in resp_data]
                # Change listen event to write
                self.event_loop.update_handler(self.c_socket.fileno(),
                                               EventLoop.WRITE)
        elif event & EventLoop.WRITE:
            self.handle_write()
        elif event & EventLoop.ERROR:
            logging.error("class WSGIStream handle_event error, close it")
            self.release()
            raise
        else:
            self.release()
            raise ViolaEventException
