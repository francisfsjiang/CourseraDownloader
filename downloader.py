#!/usr/local/bin/python3
# encoding: utf-8
import os
import sys
import time
from pickle import Unpickler
from multiprocessing import get_context
from requests import get


def kubi_worker(queue, download_dir):
    while not queue.empty():
        item = queue.get()

        file_path = os.path.join(download_dir, item['name'])
        download_file(item['url'], file_path)

        print("Finish downloading " + file_path)
        queue.task_done()


def download_file(url, file_path):
    if os.path.exists(file_path):
        return
    file_path = file_path + '.temp'
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
    context = get_context()
    task_queue = context.JoinableQueue()
    for i in task_list:
        print(i)
        task_queue.put(i)
    for i in range(os.cpu_count()*2):
        p = context.Process(target=kubi_worker, args=(task_queue, download_dir))
        p.start()
        workers.append(p)

    while not task_queue.empty():
        time.sleep(5)
    exit(0)

