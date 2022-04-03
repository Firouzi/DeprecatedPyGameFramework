from time import time
import random

MAX_SIZE = 5000000

class A:
    def __init__(self):
        self.data=random.randint(-10000,10000)

    def update(self):
        self.data=random.randint(-10000,1000)


alist = list()
adict = dict()

i = 0
while i <MAX_SIZE:
    alist.append(A())
    adict[i] = A()
    i+=1


start_time = time()
for val in alist:
    val.update()
stop_time = time()

list_speed = stop_time - start_time

start_time = time()
for key, val in adict.items():
    val.update()
stop_time = time()

dict_items_speed = stop_time - start_time

start_time = time()
for val in adict.values():
    val.update()
stop_time = time()

dict_val_speed = stop_time - start_time

print("list_speed:       " + str(list_speed))
print("dict_items_speed: " + str(dict_items_speed))
print("dict_val_speed:   " + str(dict_val_speed))