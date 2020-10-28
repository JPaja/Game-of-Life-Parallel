from threading import Condition, Event, Lock, Semaphore, Thread
from queue import Queue, Empty
import numpy as np
import threading

from numpy.core.defchararray import count


iterations = 3
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
      neighbors.append((i+ii,j+jj))
  return neighbors

def getValidNeighborIndexes(i, j):
    neighbors = []
    for ii in range(-1,2):
        for jj in range(-1,2):
            if(ii == 0 and jj == 0):
                continue
            # if(i+ii < 0 or i+ii >= table.shape[0]):
            #     continue
            # if(j+jj < 0 or j+jj >= table.shape[1]):
            #     continue
            # neighbors.append((i+ii,j+jj))
            neighbors.append(((i+ii)%n, (j+jj)%n))
    return neighbors

def getNeighbors(table, i, j):
  neighbors = []
  for neighbor in getNeighborIndexes(i,j):
    ii = neighbor[0]
    jj = neighbor[1]
    if(ii < 0 or ii >= table.shape[0]):
      neighbors.append(False)
      continue
    if(jj < 0 or jj >= table.shape[1]):
      neighbors.append(False)
      continue
    neighbors.append(table[ii][jj])
  return neighbors

def gameOfLife(table):
  newTable = np.zeros(table.shape,dtype=bool)
  for i in range(0,table.shape[0]):
    for j in range(0,table.shape[1]):
      aliveNeighbors = sum(getNeighbors(table,i,j))
      if aliveNeighbors == 3 or (aliveNeighbors == 2 and table[i][j]):
        newTable[i][j] = True
  return newTable

def executeNode(i,j,initState):
    global iterations
    global queues
    global n
    state = initState
    neighbors = getValidNeighborIndexes(i,j)
    iteration = 1
    while iteration < iterations:
        for (ii,jj) in neighbors:
            queues[ii][jj].put_nowait(state)

        aliveNeighbors = 0
        for (ii,jj) in neighbors:
            neighborValue = queues[i][j].get()
            if(neighborValue):
              aliveNeighbors+=1
            queues[i][j].task_done()
        if aliveNeighbors == 3 or (aliveNeighbors == 2 and state):
            state = True
        else:
            state = False

        steps[iteration][i][j] = state
        iteration += 1
        for ii in range(0,n): 
          for jj in range(0,n):
            queues[ii][jj].join()
        print(iteration)


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

printTable(steps[1])
print("Completed")
