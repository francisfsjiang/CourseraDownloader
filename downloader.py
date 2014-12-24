#!/usr/local/bin/python3
# encoding: utf-8
import os
import sys
import time
from pickle import Unpickler
from requests import get
from threading import Thread, RLock
from queue import Queue

TASK_QUEUE = Queue()
TASK_LOCK = RLock()


class Worker(Thread):
    def __init__(self, id, download_dir):
        super().__init__()
        self.id = id
        self.download_dir = download_dir

    def run(self):
        while 1:
            with TASK_LOCK:
                if TASK_QUEUE.empty():
                    break
                item = TASK_QUEUE.get()

            file_path = os.path.join(download_dir, item['name'])
            self.download_file(item['url'], file_path)

            print("Finish downloading " + file_path)
            # queue.task_done()

    @staticmethod
    def download_file(url, file_path):
        if os.path.exists(file_path):
            return
        # print("Start downloading " + file_path)
        file_path += '.temp'
        r = get(url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*0x400):
                if chunk:
                    print(file_path + ' downloaded 1MB')
                    f.write(chunk)
                    f.flush()
        os.rename(file_path, file_path.replace('.temp', ''))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 downloader.py lecture_id')
        exit(0)
    course_id = sys.argv[1]
    task_file = open('dumps/' + course_id + ' task_list.dump', 'rb')
    task_list = Unpickler(task_file).load()
    task_file.close()

    download_dir = 'Lecture %s' % course_id
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    workers = []
    for i in task_list:
        TASK_QUEUE.put(i)
    for i in range(os.cpu_count()*2):
        p = Worker(i, download_dir)
        p.start()
        workers.append(p)

    for i in workers:
        i.join()
    exit(0)

