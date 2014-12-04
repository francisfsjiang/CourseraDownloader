# encoding: utf-8
import os
import requests
from pickle import Unpickler
from multiprocessing import get_context
from pprint import pprint


def kubi_worker(queue, download_dir, header, subtitles_lang):
    while not queue.empty():
        item = queue.get()

        print("Start downloading " + file_path)


        print("Finish downloading " + file_path)
        queue.task_done()


def download_file(url, file_path, session=requests.Session()):
    print(url, file_path)
    if os.path.exists(file_path):
        return
    file_path = file_path + '.temp'
    r = session.get(url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*0x400):
            if chunk:
                print(file_path + ' downloaded 1MB')
                f.write(chunk)
                f.flush()
    os.rename(file_path, file_path.replace('.temp', ''))


if __name__ == '__main__':
    course_id = 'ml-007'
    file = open(course_id + ' task_list.dump','rb')
    task_list = Unpickler(file).load()
    file.close()
    pprint(task_list)
    exit(0)
    workers = []

    for i in range(4):
        p = contex.Process(target=kubi_worker, args=(task_queue, download_dir, header, subtitles_lang))
        p.start()
        workers.append(p)

    exit(0)

