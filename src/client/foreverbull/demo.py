from concurrent.futures import ThreadPoolExecutor, Future
import threading
import multiprocessing
import pynng

def callback(future: Future):
    print("Callback", future.result(), threading.get_ident())

class Worker(multiprocessing.Process):
    def __init__(self, in_q: multiprocessing.Queue, out_q: multiprocessing.Queue):
        self.in_q = in_q
        self.out_q = out_q
        super(Worker, self).__init__()

    def run(self):
        while True:
            try:
                item = self.in_q.get()
                if item is None:
                    return
                self.out_q.put(item * item)
            except Exception as e:
                print(e)


class WorkerHandler:
    def __init__(self):
        self.in_q = multiprocessing.Queue()
        self.out_q = multiprocessing.Queue()
        self.worker = Worker(self.in_q, self.out_q)
        self.worker.start()
        self._lock = threading.Lock()
    
    def locked(self) -> bool:
        return self._lock.locked()

    def acquire(self, blocking: bool = False, timeout: float = -1) -> bool:
        return self._lock.acquire(blocking=blocking, timeout=timeout)

    def release(self) -> None:
        return self._lock.release()

    def process(self, item: int):
        print("put)")
        self.in_q.put(item)
        print("get")
        x = self.out_q.get()
        print("recieved")
        return x

class WorkerPool:
    def __init__(self, length: int = 5):
        self.length = length
        self.workers = []
        for x in range(length):
            self.workers.append(WorkerHandler())

    def taredown(self):
        for worker in self.workers:
            worker.in_q.put(None)
        for worker in self.workers:
            worker.worker.join()

    def process(self, socket: pynng.Socket):
        while True:
            for worker in self.workers:
                if not worker.acquire(blocking=True, timeout=0.5):
                    continue
                try:
                    s = socket.new_context()
                    item = s.recv()
                    print("SERVER RECIEVED", item, flush=True)
                    x =  worker.process(item)
                    s.send(x)
                    return
                except Exception as e:
                    print(e)
                finally:
                    worker.release()
                return

thread_pool = ThreadPoolExecutor(max_workers=4)

import time
import pynng

running = True
def server():
    socket = pynng.Rep0(listen="tcp://127.0.0.1:5555")
    worker_pool = WorkerPool(1)
    while running:
        try:
            thread_pool.submit(worker_pool.process, socket)
        except Exception as e:
            print(e)

    thread_pool.shutdown()
    worker_pool.taredown()



def c(socket: pynng.Context):
    socket.send(2)
    print("HEY ", socket.recv(), flush=True)

if __name__ == "__main__":
    t = threading.Thread(target=server)
    t.start()

    client = pynng.Req0(dial="tcp://127.0.0.1:5555")
    with ThreadPoolExecutor(3) as pool:
        for x in range(10):
            print("SUBMIT")
            pool.submit(c, client)
    time.sleep(5)
    print("DONE")
    running = False
    t.join()

