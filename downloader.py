# encoding: utf-8
import os
import sys
import time
from pickle import Unpickler
from multiprocessing import get_context
from pprint import pprint
from requests import get


def kubi_worker(queue, download_dir):
    while not queue.empty():
        item = queue.get()

        file_path = os.path.join(download_dir, item['name'])
        # print("Start downloading " + file_path)
        download_file(item['url'], file_path)

        print("Finish downloading " + file_path)
        queue.task_done()


def download_file(url, file_path):
    if os.path.exists(file_path):
        return
    # print(file_path)
    file_path = file_path + '.temp'
    r = get(url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=10*0x400):
            if chunk:
                print(file_path + ' downloaded 10KB')
                f.write(chunk)
                f.flush()
    os.rename(file_path, file_path.replace('.temp', ''))


if __name__ == '__main__':
    # course_id = 'ml-007'
    # course_id = 'ai-001'
    # course_id = 'datascitoolbox-017'
    #course_id = 'rprog-017'
    course_id = sys.argv[1]
    task_file = open('dumps/' + course_id + ' task_list.dump', 'rb')
    task_list = Unpickler(task_file).load()
    task_file.close()
    # pprint(task_list)

    download_dir = 'Lecture %s' % course_id
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    workers = []
    context = get_context()
    task_queue = context.JoinableQueue()
    for i in task_list:
        print(i)
        task_queue.put(i)
    # for i in range(os.cpu_count()*4):
    for i in range(1):
        p = context.Process(target=kubi_worker, args=(task_queue, download_dir))
        p.start()
        workers.append(p)

    while not task_queue.empty():
        time.sleep(5)
    exit(0)

