from threading import Lock
import multiprocessing
from multiprocessing import Process, Value, Queue, Array
import numpy as np
import time

iterations = 5
n = 10


def getNeighborIndexes(i, j):
  neighbors = []
  for ii in range(-1,2):
    for jj in range(-1,2):
      if(ii == 0 and jj == 0):
        continue
      neighbors.append(((i+ii)%n, (j+jj)%n))
  return neighbors

def executeNode(i,j,state,serviceQueue,queues):
    global iterations
    neighbors = getNeighborIndexes(i,j)
    serviceQueue.put((0,i,j,state))
    for it in range(iterations - 1): 
        iteration = it + 1 
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
            state = 1
        else:
            state = 0
        serviceQueue.put((iteration,i,j,state))

def executeService(serviceQueue,tableData):
    global iterations
    global n
    for _ in range(iterations * n**2):
        (iteration,i,j,state) = serviceQueue.get()
        tableData[iteration * n**2 + i * n + j] = state

if __name__ == "__main__":
    tableData = Array('i',np.zeros(iterations * n ** 2, dtype=int))
    serviceQueue = Queue()
    sharedProcess = Process(target=executeService, args=(serviceQueue,tableData))

    sharedProcess.start()

    table = np.zeros((n,n),dtype=int)
    table[0][1] = 1
    table[1][2] = 1
    table[2][0] = 1
    table[2][1] = 1
    table[2][2] = 1


    queues = np.zeros((n,n),dtype=object)
    for i in range(n):
        for j in range(n):
            queues[i][j] = Queue()
    processes = []
    for i in range(n):
        for j in range(n):
            processes.append(Process(target=executeNode, args=(i,j,table[i][j],serviceQueue,queues)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    sharedProcess.join()

    steps = np.zeros((iterations,n,n),dtype=int)
    for index in range(iterations * n**2):
        iteration = int(index / n**2)
        i = int((index / n) % n)
        j = int(index % n)
        steps[iteration][i][j] = tableData[index]
    
    print(steps[iterations-1])
