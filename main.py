# encoding: utf-8
import requests
import bs4
import os
from multiprocessing import get_context
# from multiprocessing import get_context,Process
# from multiprocessing.queues import JoinableQueue

from pprint import pprint


def kubi_worker(queue, download_dir):
    while not queue.empty():
        item = queue.get()

        pprint(item)

        queue.task_done()


def get_request_header():
    file = open('request_header.txt', 'r')
    header = dict()
    for i in file.readlines():
        i = i.replace('\n', '')
        i = i.split(': ')
        # print(i)
        key, item = i[0], i[1]
        # print(key, item)
        if key in ['User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding', 'Referer', 'Cookie', 'Connection', 'Cache-Control']:
            header[key] = item
    return header


def generate_tasks(task_queue, lecture_list):
    for i in lecture_list:
        name = i.find(name='a', attrs='lecture-link')
        name = name.contents[0].replace('\n', '')
        print(name)
        pdf_tag = i.find(title='PDF')
        ppt_tag = i.find(title='PPT')
        video_tag = i.find(title='Video (MP4)')
        if pdf_tag:
            task = {
                'name': name,
                'type': 'pdf',
                'url': pdf_tag['href']
            }
            task_queue.put(task)
        if ppt_tag:
            task = {
                'name': name,
                'type': 'ppt',
                'url': ppt_tag['href']
            }
            task_queue.put(task)
        if video_tag:
            task = {
                'name': name,
                'type': 'video',
                'url': video_tag['href']
            }
            task_queue.put(task)

if __name__ == '__main__':
    course_id = 'ai-001'
    srt_lang = 'zh'
    login_page_url = 'https://accounts.coursera.org/'
    lecture_list_url = 'https://class.coursera.org/%s/lecture' % course_id
    login_url = ''
    session = requests.Session()

    header = get_request_header()
    session.headers = header
    pprint('SESSION HEADER\n')
    pprint(dict(session.headers))

    response = session.get(lecture_list_url)
    # pprint(dict(response.headers))
    # pprint('SESSION HEADER\n')
    # pprint(dict(session.headers))
    # pprint('SESSION COOKIE\n')
    # pprint(dict(session.cookies))
    pprint(dict(response.headers))
    # pprint(response.content.decode())

    soup = bs4.BeautifulSoup(response.content.decode())
    lecture_list = soup.find_all(name='li', attrs='viewed')

    download_dir = 'Lecture %s' % course_id
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    contex = get_context('fork')
    task_queue = contex.JoinableQueue()
    generate_tasks(task_queue, lecture_list)
    # print(task_queue.qsize())
    workers = []
    for i in range(os.cpu_count()):
        p = contex.Process(target=kubi_worker, args=(task_queue, download_dir))
        p.start()
        workers.append(p)

    task_queue.join()
    exit(0)
