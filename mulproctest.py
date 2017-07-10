import multiprocessing
import time

def printchars(i):
    print "process:", multiprocessing.current_process().name, " saving char:", i
    print i

if __name__ == "__main__":
    tstart = time.time()

    procs = []
    for i in range(48):
        p = multiprocessing.Process(target=printchars, args=(i,))
        procs.append(p)
    # p1 = multiprocessing.Process(target=printchars, args=(chars, 0, 1))
    # p2 = multiprocessing.Process(target=printchars, args=(chars, 500, 1100))
    # p3 = multiprocessing.Process(target=printchars, args=(chars, 1000, 1500))
    # p4 = multiprocessing.Process(target=printchars, args=(chars, 1500, 2000))
    # p5 = multiprocessing.Process(target=printchars, args=(chars, 2000, 2500))
    # p6 = multiprocessing.Process(target=printchars, args=(chars, 2500, 3000))
    # p7 = multiprocessing.Process(target=printchars, args=(chars, 3000, 3500))



    print("The number of CPU is:" + str(multiprocessing.cpu_count()))
    for p in multiprocessing.active_children():
        print("child   p.name:" + p.name + "\tp.id" + str(p.pid))

    for p in procs:
        p.start();
    for p in procs:
        p.join();

    tend = time.time()
    print "Finished! Time used:", tend - tstart
