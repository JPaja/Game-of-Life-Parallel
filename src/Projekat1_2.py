from threading import Condition, Event, Lock, Semaphore, Thread
from queue import Queue, Empty
import numpy as np
import time
import threading

from numpy.core.defchararray import count


iterations = 15
n = 20
size = n**2
steps = np.zeros((iterations,n,n),dtype=bool)
#table = np.random.rand(size).reshape(n, n) > 0.5
table = np.zeros((n,n),dtype=bool)
table[0][1] = True
table[1][2] = True
table[2][0] = True
table[2][1] = True
table[2][2] = True

steps[0] = table

threads = np.zeros(table.shape,dtype=Thread)
queues = np.zeros(table.shape,dtype=Queue)

def printTable(table):
  for i in range(0,table.shape[0]):
    for j in range(0,table.shape[1]):
      print(1 if table[i][j] else 0 ,end='')
    print()

def getNeighborIndexes(i, j):
    neighbors = []
    for ii in range(-1,2):
        for jj in range(-1,2):
            if(ii == 0 and jj == 0):
                continue
            neighbors.append(((i+ii)%n, (j+jj)%n))
    return neighbors

lock = Lock()
counter = 0
def executeNode(i,j,initState):
    global iterations
    global queues
    global counter
    global n
    state = initState
    neighbors = getNeighborIndexes(i,j)
    iteration = 1
    while iteration < iterations:
        for (ii,jj) in neighbors:
            queues[ii][jj].put_nowait((state,iteration))

        aliveNeighbors = 0
        cachedneighbors = []

        for (ii,jj) in neighbors:
            while True:
              (neighborValue,neighborIteration) = queues[i][j].get()
              if(iteration != neighborIteration):
                cachedneighbors.append((neighborValue,neighborIteration))
                continue
              if(neighborValue):
                aliveNeighbors+=1
              break

        for cachedneighbor in cachedneighbors:
          queues[i][j].put_nowait(cachedneighbor)
        if aliveNeighbors == 3 or (aliveNeighbors == 2 and state):
            state = True
        else:
            state = False

        steps[iteration][i][j] = state
        iteration += 1


for i in range(0,table.shape[0]):
  for j in range(0,table.shape[1]):
    t = Thread(target=executeNode, args=(i,j,table[i][j]))
    threads[i][j] = t
    queues[i][j] = Queue()


for i in range(0,table.shape[0]):
  for j in range(0,table.shape[1]):
    threads[i][j].start()

for i in range(0,table.shape[0]):
  for j in range(0,table.shape[1]):
    threads[i][j].join()

printTable(steps[iterations-1])
print("Completed")
