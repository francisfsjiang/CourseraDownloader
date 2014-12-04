# encoding: utf-8
import requests
import bs4
import os
from pickle import Pickler
from pprint import pprint
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, element




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


def generate_tasks(task_list, lecture_list, session, subtitles_lang):
    for i in lecture_list:
        # name = i.find(name='a', attrs='lecture-link')
        # name = name.contents[0].replace('\n', '')
        video_tag = i.find(title='Video (MP4)')
        video_view_url = i.find(attrs='lecture-link')['data-modal-iframe']
        if video_tag:
            video_page_url = video_tag['href']
            # print(video_page_url)
            resp = session.get(video_page_url, allow_redirects=False)
            video_url = resp.headers['Location']
            video_name = unquote(unquote(urlparse(resp.headers['Location']).query).replace(' ', '').split(';')[1][10:-1])
            task = {
                'name': video_name,
                'type': 'mp4',
                'url': video_url
            }
            task_list.append(task)
            pprint(task)

        resource = [('PDF', '.pdf'),
                    ('Lecture Notes', '.pdf'),
                    ('Slides', '.pdf'),
        ]
        for m, n in resource:
            tag = i.find(title=m)
            if tag:
                task = {
                    'name': video_name.replace('.mp4', n),
                    'type': n[1:],
                    'url': tag['href']
                }
                task_list.append(task)
                pprint(task)

        resp = session.get(video_view_url)
        soup = BeautifulSoup(resp.content.decode())
        subtitles = dict()
        for i in soup.video.source.source.descendants:
            if type(i) != element.NavigableString:
                subtitles[i['srclang']] = i['src']
                # print(i['src'], '+++++', i['srclang'])

        # pprint(subtitles)
        subtitles_chosen = None
        for i in subtitles_lang:
            # print(i)
            if i in subtitles:
                subtitles_chosen = subtitles[i]
                break
        if subtitles_chosen:
            print(subtitles_chosen)
        if subtitles_chosen:
            task = {
                'name': video_name.replace('.mp4', '.srt'),
                'type': 'srt',
                'url': subtitles_chosen
            }
            task_list.append(task)
            pprint(task)


if __name__ == '__main__':
    course_id = 'ml-007'
    # course_id = 'rprog-017'
    subtitles_lang = ['zh-cn', 'zh', 'cn', 'en']
    login_page_url = 'https://accounts.coursera.org/'
    lecture_list_url = 'https://class.coursera.org/%s/lecture' % course_id
    login_url = ''
    session = requests.Session()

    header = get_request_header()
    session.headers = header
    print('Getting Lecture List ...')
    response = session.get(lecture_list_url)
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
    print('get %d lectures' % len(lecture_list))


    task_list = []
    generate_tasks(task_list, lecture_list, session, subtitles_lang)

    task_file = open(course_id + ' task_list.dump', 'wb')
    Pickler(task_file).dump(task_list)
    task_file.close()

    for i in task_list:
        pprint(i)
    exit(0)

