import multiprocessing
from multiprocessing import Pool, cpu_count
import numpy as np
import time

iterations = 5
n = 10
N = 20

def printTable(table):
  for i in range(0,table.shape[0]):
    for j in range(0,table.shape[1]):
      print(1 if table[i][j] else 0 ,end='')
    print()

def getNeighborIndexes(i, j):
  global n
  neighbors = []
  for ii in range(-1,2):
    for jj in range(-1,2):
      if(ii == 0 and jj == 0):
        continue
      neighbors.append(((i+ii)%n, (j+jj)%n))
  return neighbors

def executeNode(nodes,table):
    results = []
    for (i,j) in nodes:
      neighbors = getNeighborIndexes(i,j)
      aliveNeighbors = 0
      for (ii,jj) in neighbors:
        if table[ii][jj]:
              aliveNeighbors += 1
      if aliveNeighbors == 3 or (aliveNeighbors == 2 and table[i][j]):
          state = 1
      else:
          state = 0
      results.append((i,j,state))
    return results

#https://stackoverflow.com/a/2130035
def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

if __name__ == "__main__":
    table = np.zeros((n,n),dtype=int)
    table[0][1] = 1
    table[1][2] = 1
    table[2][0] = 1
    table[2][1] = 1
    table[2][2] = 1

    allNodes = []
    for i in range(n):
        for j in range(n):
            allNodes.append((i,j))
    nodes = chunkIt(allNodes,N)

    pool = Pool(cpu_count())
    steps = []
    steps.append(table.copy())
    for iteration in range(iterations):
        results = []
        for nodeChunk in nodes:
          results.append(pool.apply_async(executeNode,args=(nodeChunk,table)))

        for resultAsync in results:
          result = resultAsync.get()
          for (i,j,state) in result:
            table[i,j] = state
        steps.append(table.copy())

    pool.close()
    pool.join()

    for step in steps:
      printTable(step)
      print()
