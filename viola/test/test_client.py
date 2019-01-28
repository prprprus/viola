import socket
import time


address = ("10.211.55.25", 2333)
msg = """
GET /listNews HTTP/1.1
Connection: Keep-Alive
Host: 127.0.0.1:8080
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36
Accept: application/json
"""


def main():
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect(address)

    # loop
    # while True:
    #     print(cs)
    #     cs.sendall(b"hello")
    #     print(cs.recv(8192))
    #     time.sleep(1)

    # once
    # cs.sendall(b"hello")
    # print(cs.recv(8192))
    cs.sendall(msg.encode("utf8"))
    print(cs.recv(8192))

    # cs.sendall(msg.encode("utf8"))
    # print(cs.recv(8192))


if __name__ == '__main__':
    main()
