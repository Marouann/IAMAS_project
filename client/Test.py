from multiprocessing import Process, Manager

def dothing(L, start, end):  # the managed list `L` passed explicitly.
    for i in range(start,end):
        L.append(i)

if __name__ == "__main__":
    with Manager() as manager:
        L = manager.list() # <-- can be shared between processes.
        processes = []
        for i in range(5):
            p = Process(target=dothing, args=(L,i*10 , i*10+5))  # Passing the list
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        print(type(L))
