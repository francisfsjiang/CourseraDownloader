# encoding: utf-8
import requests
import bs4
import os
from pprint import pprint
from multiprocessing import get_context
# from multiprocessing import get_context,Process
# from multiprocessing.queues import JoinableQueue

from bs4 import BeautifulSoup, element


def kubi_worker(queue, download_dir, header, subtitles_lang):
    while not queue.empty():
        item = queue.get()

        # pprint(item)
        file_name = str(item['id']) + ' - ' + item['name'] + '.' + item['type']
        file_path = os.path.join(download_dir, file_name)
        print("Start downloading " + file_path)
        if item['type'] == 'mp4':
            session = requests.Session()
            session.headers = header
            download_video(item['url'], file_path, session, subtitles_lang)
        else:
            download_file(item['url'], file_path)


        queue.task_done()


def download_video(url, file_path, header, subtitles_lang):
    response = session.get(url, verify=True)
    # print(response.request.headers)
    # print(dict(response.headers))
    # print(response.content.decode())
    soup = BeautifulSoup(response.content.decode())
    video_address = soup.video.source['src']
    print(video_address)
    download_file(video_address, file_path, session)
    #
    # subitles = soup.video.source.source.descendants
    subtitles = dict()
    for i in soup.video.source.source.descendants:
        if type(i) != element.NavigableString:
            subtitles[i['srclang']] = i['src']
            # print(i['src'], '+++++', i['srclang'])

    subtitles_chosen = None
    for i in subtitles_lang:
        if i in subtitles:
            subtitles_chosen = subtitles[i]
    if subtitles_chosen:
        print(subtitles_chosen)
        download_file(subtitles_chosen, file_path.replace('.mp4', '.srt'))


def download_file(url, file_path, session=requests.Session()):
    if os.path.exists(file_path):
        return
    file_path = file_path + '.temp'
    r = session.get(url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=0x100000):
            if chunk:
                print(file_path + ' downloaded 1MB')
                f.write(chunk)
                f.flush()
    os.rename(file_path, file_path.replace('.temp', ''))


def get_request_header():
    file = open('request_header.txt', 'r')
    header = dict()
    for i in file.readlines():
        i = i.replace('\n', '')
        i = i.split(': ')
        # print(i)
        key, item = i[0], i[1]
        # print(key, item)
        if key in ['User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding', 'Cookie', 'Connection']:
            header[key] = item
    return header


def generate_tasks(task_queue, lecture_list):
    id = 0
    for i in lecture_list:
        name = i.find(name='a', attrs='lecture-link')
        name = name.contents[0].replace('\n', '')
        # print(name)
        # pdf_tag = i.find(title='PDF')
        # ppt_tag = i.find(title='PPT')
        video_tag = i.find(name='a', attrs='lecture-link')
        # if pdf_tag:
        #     task = {
        #         'id': id,
        #         'name': name,
        #         'type': 'pdf',
        #         'url': pdf_tag['href']
        #     }
        #     id += 1
        #     task_queue.put(task)
        # if ppt_tag:
        #     task = {
        #         'id': id,
        #         'name': name,
        #         'type': 'pptx',
        #         'url': ppt_tag['href']
        #     }
        #     id += 1
        #     task_queue.put(task)
        if video_tag:
            task = {
                'id': id,
                'name': name,
                'type': 'mp4',
                'url': video_tag['data-modal-iframe']
            }
            id += 1
            task_queue.put(task)
        if id > 5:
            return


if __name__ == '__main__':
    course_id = 'ml-007'
    subtitles_lang = ['zh-cn', 'zh', 'en']
    login_page_url = 'https://accounts.coursera.org/'
    lecture_list_url = 'https://class.coursera.org/%s/lecture' % course_id
    login_url = ''
    session = requests.Session()

    header = get_request_header()
    session.headers = header
    # pprint('SESSION HEADER\n')
    # pprint(dict(session.headers))

    response = session.get(lecture_list_url)
    # pprint(dict(response.headers))
    # pprint('SESSION HEADER\n')
    # pprint(dict(session.headers))
    # pprint('SESSION COOKIE\n')
    # pprint(dict(session.cookies))
    # pprint(dict(response.headers))
    # pprint(response.content.decode())

    soup = bs4.BeautifulSoup(response.content.decode())
    lecture_sections = soup.find_all(name='ul', attrs='course-item-list-section-list')
    lecture_list = []
    for i in lecture_sections:
        for j in i.children:
            lecture_list.append(j)
    download_dir = 'Lecture %s' % course_id
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    contex = get_context('fork')
    task_queue = contex.JoinableQueue()
    generate_tasks(task_queue, lecture_list)
    # print(task_queue.qsize())

    workers = []
    for i in range(2):
        p = contex.Process(target=kubi_worker, args=(task_queue, download_dir, header, subtitles_lang))
        p.start()
        workers.append(p)
    while True:
        pprint(task_queue.get())
    # while True:
    #     kubi_worker(task_queue, download_dir, session, subtitles_lang)

    task_queue.join()
    exit(0)
