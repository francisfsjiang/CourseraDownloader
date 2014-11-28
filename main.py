# encoding: utf-8
import requests
import multiprocessing
import bs4
import os

from pprint import pprint


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


if __name__ == '__main__':
    course_id = 'ai-001'
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
    for i in lecture_list:
        name = i.find(name='a', attrs='lecture-link')
        print(name.contents[0].replace('\n', ''))
        tag = i.find(title='PDF')
        if tag:
            print(tag['href'])

        pprint(i.find(title='Video (MP4)')['href'])

    os.mkdir('Lecture %s' % course_id)

