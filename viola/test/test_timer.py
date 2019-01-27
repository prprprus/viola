from threading import Timer
import os


def hello():
    print("hello...")


Timer(3.0, hello).start()

for i in range(50):
    print(i)

os._exit(0)
