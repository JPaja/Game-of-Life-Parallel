from threading import Condition, Event, Lock, Semaphore, Thread
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
brojaciSuseda = np.zeros(table.shape,dtype=int)
brojaciSusedaLocks = np.zeros(table.shape,dtype=object)
semafori = np.zeros(table.shape,dtype=Semaphore)
kondicijal = Condition()
lock = Lock()
brojac = 0


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
            if(i+ii < 0 or i+ii >= table.shape[0]):
                continue
            if(j+jj < 0 or j+jj >= table.shape[1]):
                continue
            neighbors.append((i+ii,j+jj))
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

def executeNode(i,j):
    global table
    global iterations
    global brojaciSuseda
    global semafori
    global brojaciSusedaLocks
    global lock
    global brojac
    global size
    neighbors = getValidNeighborIndexes(i,j)
    iteration = 0
    while iteration < iterations:

        aliveNeighbors = 0
        for (ii,jj) in neighbors:
            brojaciSusedaLocks[ii][jj].acquire()
            if table[ii][jj]:
                aliveNeighbors += 1
            brojaciSuseda[ii][jj]+= 1
            if(brojaciSuseda[ii][jj] == len(getValidNeighborIndexes(ii,jj))): #8): u slucaju ivica ne racunamo ne postojece nodove
                brojaciSuseda[ii][jj] = 0
                semafori[ii][jj].release()
            brojaciSusedaLocks[ii][jj].release()

        semafori[i][j].acquire()
        
        state = table[i][j]
        table[i][j] = False
        if aliveNeighbors == 3 or (aliveNeighbors == 2 and state):
            table[i][j] = True
        steps[iteration][i][j] = table[i][j]
        iteration += 1
        lock.acquire()
        brojac+= 1
        kondicijal.acquire()
        if(brojac == size):
          brojac = 0
          print()
          print()
          printTable(table)
          kondicijal.notifyAll()
          lock.release()
        else:
          lock.release()
          kondicijal.wait()
        kondicijal.release()


for i in range(0,table.shape[0]):
  for j in range(0,table.shape[1]):
    t = Thread(target=executeNode, args=(i,j))
    threads[i][j] = t
    brojaciSusedaLocks[i][j] = Lock()
    semafori[i][j] = Semaphore(0)


for i in range(0,table.shape[0]):
  for j in range(0,table.shape[1]):
    threads[i][j].start()

for i in range(0,table.shape[0]):
  for j in range(0,table.shape[1]):
    threads[i][j].join()

printTable(table)
print("Completed")
