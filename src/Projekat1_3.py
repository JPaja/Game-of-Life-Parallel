from threading import Lock
import multiprocessing
from multiprocessing import Process, Value, Queue, Array
import numpy as np
import time


iterations = 15
n = 7
size = n**2


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


lock = Lock()
counter = 0
def executeNode(i,j,initState,queues,serviceQueue):
    global iterations
    global counter
    global n
    state = initState
    neighbors = getValidNeighborIndexes(i,j)
    iteration = 1
    while iteration < iterations:
        for (ii,jj) in neighbors:
            queues[ii][jj].put((state,iteration))

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
          queues[i][j].put(cachedneighbor)
        if aliveNeighbors == 3 or (aliveNeighbors == 2 and state):
            state = True
        else:
            state = False
        serviceQueue.put((i,j,state,iteration))
        iteration += 1


def executeService(serviceQueue,lista):
  global size
  for r in range(size):
    (i,j,state,iteration) = serviceQueue.get()
    index = iteration * (size) + i * n + j
    if(state):
      lista[index] = True
    else:
      lista[index] = False
    
  i = 1 
  # for(i in range(maxIter)):
  #   result.append(table[i])

if __name__ == "__main__":
  steps = np.zeros((iterations,n,n),dtype=bool)

  table = np.zeros((n,n),dtype=bool)
  table[0][1] = True
  table[1][2] = True
  table[2][0] = True
  table[2][1] = True
  table[2][2] = True



  threads = np.zeros(table.shape,dtype=Process)
  queues = np.zeros(table.shape,dtype=object)
  serviceQueue = Queue()

  for i in range(n):
      for j in range(n):
        queues[i][j] = Queue()

  for i in range(n):
    for j in range(n):
      t = Process(target=executeNode, args=(i,j,table[i][j],queues,serviceQueue))
      threads[i][j] = t
      
    lista = Array('i',np.zeros(n**2 * iterations,dtype=int))
    serivceProcess = Process(target=executeService, args=(serviceQueue,lista))
    serivceProcess.start()

  for i in range(n):
      for j in range(n):
        threads[i][j].start()

  for i in range(n):
      for j in range(n):
        threads[i][j].join()

  serivceProcess.join()
  print(len(lista))
  for it in range(iterations):
    for i in range(0,table.shape[0]):
      for j in range(0,table.shape[1]):
        steps[it][i][j] = lista[((it * (n * n))+i * n)+j]
  for step in steps:
    printTable(step)
    print("\n")
  print("Completed")
