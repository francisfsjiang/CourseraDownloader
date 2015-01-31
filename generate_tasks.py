#!/usr/local/bin/python3
# encoding: utf-8
import requests
import bs4
import os
import sys
from pickle import Pickler
from pprint import pprint
from urllib.parse import unquote, urlparse
import re

from bs4 import BeautifulSoup, element


#change the order of this list to change the best str lang to download
subtitles_lang = ['zh-cn', 'zh-tw', 'zh', 'cn', 'en']


def get_request_header():
    file = open('request_header.txt', 'r')
    header = dict()
    for i in file.readlines():
        if i == "\n":
            continue
        i = i.replace('\n', '')
        i = i.split(': ')
        key, item = i[0], i[1]
        if key in ['User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding', 'Cookie', 'Connection']:
            header[key] = item
    return header


def generate_tasks(task_list, lecture_list, session, subtitles_lang):
    for i in lecture_list:
        video_tag = i.find(title='Video (MP4)')
        video_view_url = i.find(attrs='lecture-link')['data-modal-iframe']
        if video_tag:
            video_page_url = video_tag['href']
            resp = session.get(video_page_url, allow_redirects=False)
            video_url = resp.headers['Location']
            video_name = unquote(unquote(urlparse(resp.headers['Location']).query).replace(' ', '').split(';')[1][10:-1])
            video_name = re.sub(r'[/\\:\?<>\|]', '_', video_name)
            task = {
                'name': video_name,
                'type': 'mp4',
                'url': video_url
            }
            task_list.append(task)
            pprint(task)
        else:
            continue

        resource = [('PDF', '.pdf'),
                    ('Lecture Notes', '.pdf'),
                    ('Slides', '.pdf'),
        ]
        # for m, n in resource:
        #     tag = i.find(title=m)
        #     if tag:
        #         task = {
        #             'name': video_name.replace('.mp4', n),
        #             'type': n[1:],
        #             'url': tag['href']
        #         }
        #         task_list.append(task)
        #         pprint(task)

        resp = session.get(video_view_url)
        soup = BeautifulSoup(resp.content.decode())
        subtitles = dict()
        for i in soup.video.source.source.descendants:
            if type(i) != element.NavigableString:
                subtitles[i['srclang']] = i['src']

        subtitles_chosen = None
        for i in subtitles_lang:
            if i in subtitles:
                subtitles_chosen = subtitles[i]
                break
        if subtitles_chosen:
            task = {
                'name': video_name.replace('.mp4', '.srt'),
                'type': 'srt',
                'url': subtitles_chosen
            }
            task_list.append(task)
            pprint(task)


if __name__ == '__main__':
    if not os.path.exists('request_header.txt'):
        print('request_header.txt not found.')
        exit(0)
    if len(sys.argv) < 2:
        print('Usage: python3 generate_tasks.py lecture_id')
        exit(0)
    course_id = sys.argv[1]
    lecture_list_url = 'https://class.coursera.org/%s/lecture' % course_id
    session = requests.Session()

    header = get_request_header()
    session.headers = header
    print('Getting Lecture List ...')
    response = session.get(lecture_list_url)

    soup = bs4.BeautifulSoup(response.content.decode())
    lecture_sections = soup.find_all(name='ul', attrs='course-item-list-section-list')
    lecture_list = []
    for i in lecture_sections:
        for j in i.children:
            lecture_list.append(j)
    print('get %d lectures' % len(lecture_list))

    task_list = []
    generate_tasks(task_list, lecture_list, session, subtitles_lang)

    if not os.path.exists(os.path.abspath('dumps')):
        os.mkdir('dumps')
    task_file = open('dumps/' + course_id + ' task_list.dump', 'wb')
    Pickler(task_file).dump(task_list)
    task_file.close()

    print('Generate successfully.')
    exit(0)

