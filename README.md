CourseraDownloader
==================

CourseraDownloader - A downloader for Coursera lecture and subtitles, based on requests and multiprocessing lib

**Usage:**

First, put your cookie of coursera.org in `request_header.txt`

Then the file should looks like this

	User-Agent: Mozilla/5.0 (Macintosh; Inte.....
	Accept: text/html,application/xhtml+xm.....
	Accept-Language: zh-cn,zh;q=0.8,e....
	Accept-Encoding: gzip, deflate
	Cookie: csrf_token=.....
	Connection: keep-alive

You can copy your request header of coursera.org in firebug or other browser-buildin devtools


Then, Get start.

	python3 main.py lecture_id


###Notice

**What is `lecture_id` ?**

Enter the course page and the the url looks like this

	https://class.coursera.org/ml-007
	
`ml-007` is your course id

**About language of srt**

Change the priority list in the front of the `generate_tasks.py`.

In this case, the 'zh-ch' srt will be download first, then is 'zh'

	#change the order of this list to change the best str lang to download
	subtitles_lang = ['zh-cn', 'zh', 'en']
