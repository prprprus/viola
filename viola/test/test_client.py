import socket
import time


address = ("localhost", 2333)


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
    cs.sendall(b"hello")
    print(cs.recv(8192))


if __name__ == '__main__':
    main()
