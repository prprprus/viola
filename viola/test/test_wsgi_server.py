from viola.event_loop import EventLoop
from viola.wsgi.server import WSGIServer
from viola.scheduler import Scheduler
from viola.test.test_wsgi_app import app


if __name__ == '__main__':
    event_loop = EventLoop.instance(Scheduler.instance())
    server = WSGIServer(event_loop, keepalive=False)
    server.set_handler(app)
    server.bind(host="10.211.55.25", port=2333)
    server.listen(9128)
    # server.start(os.cpu_count())
    server.start(1)
    event_loop.start()
