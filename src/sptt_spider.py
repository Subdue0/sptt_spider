import os
import sys
import time

import ssl
from urllib import request
from urllib import error
from bs4 import BeautifulSoup

import threading
from concurrent.futures import ThreadPoolExecutor



############################################################################################################################################################
# 主方法
def main():
	init()
	if connection_check() == True:
		print('\n\nNetwork status  -------------------->  Normal\n\n')
		crawl_all()
	else:
		print('\n\nNetwork status  -------------------->  Abnormal')
		os.system('pause')
		
		
		
def init():
	# os.system('color 0a')
	# print('########################################################################################################################', end='')
	# print('#                                                                                                                      #', end='')
	# print('#                                       A Spider Of WebSite Called ShiPinTianTang                                      #', end='')
	# print('#                                                                                                                      #', end='')
	# print('########################################################################################################################', end='')
	
	os.system('color 0a')
	print('●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●', end='')
	print('●                                                                                                                    ●', end='')
	print('●                                   The Spider Of A WebSite Called ShiPinTianTang                                    ●', end='')
	print('●                                                                                                                    ●', end='')
	print('●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●', end='')


	
	
# 检测网络状态	
def connection_check():
	try:
		url = 'http://www.offer4u.cn/ping'
		req = request.Request(url)
		req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36')
		res = request.urlopen(req)
		
		
		if res.status == 204:
			return True
		else:
			return False
			
			
	except Exception as e:
		print('connection_check():\n' + repr(e))
		return False
		
		
		
############################################################################################################################################################
# 以下两个方法频繁使用，所有的请求和写文件都用他们
# 发送网络请求
def get_res(url, timeout, return_object):
	trytimes = 0
	while True:
		try:
			req = request.Request(url)
			context = ssl._create_unverified_context()	
			req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36')
			res = request.urlopen(req, context = context, timeout = timeout).read()
			
			
			if return_object == 'res_text':
				return res.decode('utf-8')
			elif return_object == 'res_byte':
				return res
			else:
				soup = BeautifulSoup(res, 'html.parser')
				return soup
				
				
		except error.HTTPError:
			return False
			
			
		except Exception as e:
			trytimes += 1
			# 调试代码
			sys.stdout.write(' ' * 104 + '\r')
			sys.stdout.flush()
			# print('get_res():\n'+repr(e))
			# print('%s  -------------------->  Trytimes:%s  -------------------->  Current_threads:%s' % (threading.currentThread().getName(), trytimes, threading.activeCount()))
			
			
			
# 写数据到文件
def write_file(path, file_name, data, mode):
	try:
		if os.path.exists(path) == False:
			os.makedirs(path)
			if mode == 'wb':
				with open(path + file_name, 'wb') as f:
					f.write(data)
			else:
				with open(path + file_name, 'w', encoding='utf-8') as f:
					f.write(data)
		else:
			if mode == 'wb':
				with open(path + file_name, 'wb') as f:
					f.write(data)
			else:
				with open(path + file_name, 'w', encoding='utf-8') as f:
					f.write(data)
					
					
	except Exception as e:
		print('write_file():\n'+repr(e))
		sys.exit(-1)
		
		
		
############################################################################################################################################################
# 该方法用于抓取最近更新板块所有内容
def crawl_all():
	try:
		homepage_url = 'https://www.shipintiantang.com/'
		soup = get_res(homepage_url, 3, 'soup')
		tags = soup.select('body main section h2.h2.iconfont.icon_lastest')[0].parent.select('div div a')
		
		
		for tag in tags:
			name = get_video_info(tag)[0]
			
			
			info_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\sptt\\' + name + '\\'
			
			
			mp4_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\mp4\\'
			if can_download_mp4(mp4_path, name) == False:
				print(name + '\tCompleted')
				continue
				
				
			print('\n\nName:\t\t' + name)
			
			
			print('Write info\t-------------------->  Start')
			crawl_info(tag, info_path)
			print('Write info\t-------------------->  Completed')
			
			
			print('Download cover\t-------------------->  Start')
			crawl_cover(tag, info_path)
			print('Download cover\t-------------------->  Completed')
			
			
			ts_part_url, sum_ts_clips = get_write_ts_url(tag, info_path)
			if can_download_ts(ts_part_url, sum_ts_clips) == False:
				print('The video can\'t download, skip.')
				print('\n\n\n\n\n')
				continue
				
				
			print('Start download ts clips')
			ts_clips_path = info_path + 'ts\\'
			crawl_ts_clips(name, ts_part_url, sum_ts_clips, ts_clips_path)
			print('\nTs clips download completed')
			
			
			print('Merge mp4  -------------------->  Start')
			merge_mp4(mp4_path, name)
			print('Merge mp4  -------------------->  Completed')
			
			
			print('\n\n\n\n\n')
			
			
	except Exception as e:
		print('crawl_all():\n'+repr(e))
		sys.exit(-1)
		
		
		
############################################################################################################################################################
# 抓视频信息
def crawl_info(tag, path):
	try:
		info = get_video_info(tag)[1]
		write_file(path, 'info.txt', info, 'w')
		
		
	except Exception as e:
		print('crawl_info():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 抓取封面
def crawl_cover(tag, path):
	try:
		cover_url = get_video_info(tag)[2]
		download_cover(cover_url, path)
		
		
	except Exception as e:
		print('crawl_cover():\n'+repr(e))
		sys.exit(-1)			
		
		
		
# 抓取ts视频片段
def crawl_ts_clips(name, ts_part_url, sum_ts_clips, ts_clips_path):
	try:
		clean_ts_clips(name)
		
		
		ts_part_url_list = [ts_part_url for _ in range(sum_ts_clips)]
		path_list = [ts_clips_path for _ in range(sum_ts_clips)]
		name_list = ['%03d' %_ for _ in range(sum_ts_clips)]
		
		
		thread_progress_bar = threading.Thread(target=progress_bar, args=(sum_ts_clips, ts_clips_path))
		thread_progress_bar.start()
		
		
		with ThreadPoolExecutor(max_workers=50, thread_name_prefix='Ts_clips') as executor_map:
			executor_map.map(download_ts_clips, ts_part_url_list, path_list, name_list)
			
			
		thread_progress_bar.join()
		
		
	except Exception as e:
		print('crawl_ts_clips():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 合成mp4		
def merge_mp4(mp4_path, mp4_name):
	try:
		ts_clips_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\sptt\\' + mp4_name + '\\ts\\'
		
		
		if os.path.exists(mp4_path) == False:
			os.makedirs(mp4_path)
			os.system('copy /b "%s*.ts" "%s%s.mp4" > nul' %(ts_clips_path, mp4_path, mp4_name))
		else:
			os.system('copy /b "%s*.ts" "%s%s.mp4" > nul' %(ts_clips_path, mp4_path, mp4_name))
			
			
	except Exception as e:
		print('merge_mp4():\n'+repr(e))
		sys.exit(-1)
		
		
		
############################################################################################################################################################
# 下载封面
def download_cover(cover_url, path):
	try:
		res = get_res(cover_url, 5, 'res_byte')
		write_file(path, 'cover.jpg', res, 'wb')
		
		
	except Exception as e:
		print('download_cover():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 下载ts视频片段
def download_ts_clips(ts_part_url, path, name):
	try:
		ts_url = ts_part_url + name + '.ts'
		
		
		file_name = name + '.ts'
		
		
		res = get_res(ts_url, 10, 'res_byte')
		if res:
			write_file(path, file_name, res, 'wb')
			return True
		else:
			return False
			
			
	except Exception as e:
		print('download_ts_clips():\n'+repr(e))
		sys.exit(-1)
		
		
		
############################################################################################################################################################		
# 获取视频的的信息，比如播放量，发布时间。。。。。。
def get_video_info(tag):
	try:
		name = tag.select('div div.img_wapper img')[0]['alt']
		cover_url = tag.select('div div.img_wapper img')[0]['src']
		video_url = 'https://www.shipintiantang.com'+ '/' + tag['href']
		
		
		info_name = '名称：\t\t' + name + '\n'
		info_play_volume = '播放量：\t\t' + tag.select('div div.sub_des span')[0].get_text() + '\n'
		info_release_time = '发布时间：\t' + tag.select('div div.sub_des span')[1].get_text() + '\n'
		info_cover_url = '封面地址：\t' + cover_url + '\n'
		info_video_url = '视频地址：\t' + video_url
		
		
		info = info_name + info_play_volume + info_release_time + info_cover_url + info_video_url
		
		
		return (name, info, cover_url, video_url)
		
		
	except Exception as e:
		print('get_video_info():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 获取视频的地址
def get_video_url(play_url):
	try:
		soup = get_res(play_url, 3, 'soup')
		
		
		tags = soup.select('body main div div.master div script')[1].get_text()
		
		
		video_url = tags.split('video:\'')[1].split('\'//视频地址')[0]
		return video_url
		
		
	except Exception as e:
		print('get_video_url():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 获取ts视频片段的信息，比如ts的前缀，片段数量
def get_ts_info(m38u_first_part_url, m38u_second_part_url):
	try:
		m38u_url = m38u_first_part_url + m38u_second_part_url
		
		
		res = get_res(m38u_url, 3, 'res_text')
		ts_second_part_url = res.split('\n')[-3][:-6]
		
		
		ts_first_part_url = m38u_first_part_url
		ts_part_url = ts_first_part_url + ts_second_part_url
		
		
		ts_first = len(res.split('\n')[5])
		ts_last = len(res.split('\n')[-3])
		
		
		if ts_first == ts_last:
			sum_ts_clips = int(res.split('\n')[-3].split('/')[-1].split('.')[0][-3:]) + 1
			return (ts_part_url, sum_ts_clips)
		else:
			sum_ts_clips = int(res.split('\n')[-3].split('/')[-1].split('.')[0][-4:]) + 1
			return (ts_part_url, sum_ts_clips)
			
			
	except Exception as e:
		print('get_ts_info():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 获取m38u地址
def get_m38u_url(video_url):
	try:
		m38u_first_part_url = video_url.split('/')[0]+'//'+video_url.split('/')[2]
		
		
		res = get_res(video_url, 3, 'res_text')
		m38u_second_part_url = res.split('\n')[-2]
		
		
		return (m38u_first_part_url, m38u_second_part_url)
		
		
	except Exception as e:
		print('get_m38u_url():\n'+repr(e))
		sys.exit(-1)
		
		
		
# 获得ts路径并且写入到文件
def get_write_ts_url(tag, path):
	try:
		play_url = get_video_info(tag)[3]
		video_url = get_video_url(play_url)
		m38u_first_part_url, m38u_second_part_url = get_m38u_url(video_url)
		ts_part_url, sum_ts_clips = get_ts_info(m38u_first_part_url, m38u_second_part_url)
		
		
		txt_ts_sum_ts_clips = '视频片段数量：\t' + str(sum_ts_clips) + '\n'
		txt_ts_part_url = 'ts视频片段的前缀：\t' + ts_part_url
		ts = txt_ts_sum_ts_clips + txt_ts_part_url
		write_file(path, 'ts.txt', ts, 'w')
		
		
		return (ts_part_url, sum_ts_clips)
		
		
	except Exception as e:
		print('get_write_ts_url():\n'+repr(e))
		sys.exit(-1)	
		
		
		
############################################################################################################################################################	
# 以下三个方法都用于，下载ts视频片段
# 突然中断程序导致下载不完全，清除残留的视频文件
def clean_ts_clips(name):
	try:
		ts_clips_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\sptt\\' + name + '\\ts\\'
		if os.path.exists(ts_clips_path) == True:
			breakpoint = len(os.listdir(ts_clips_path))
			if breakpoint != 0:
				ts_clips_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\sptt\\' + name + '\\ts\\'
				os.system('del /q "%s*.ts" > nul' % ts_clips_path)
				
				
	except Exception as e:
		print('clean_ts_clips():\n'+repr(e))
		sys.exit(-1)	
		
		
		
# 进度条实现
def progress_bar(sum_ts_clips, ts_clips_path):
	try:
		while True:
			if os.path.exists(ts_clips_path) == False:
				time.sleep(1)
				continue
				
				
			count = 0
			for file_name in os.listdir(ts_clips_path):
				if file_name.split('.')[-1] == 'ts':
					count += 1
					
					
			i = int((count / sum_ts_clips) * 50)
			percentage = '{:.0%}'.format(count / sum_ts_clips)
			
			
			sys.stdout.write('▉' * i + '%s\r' % (percentage))
			# sys.stdout.write('●' * i + '%s\r' % (percentage))
			sys.stdout.flush()
			
			
			time.sleep(0.5)
			
			
			if i == 50:
				return
				
				
	except Exception as e:
		print('progress_bar():\n' + repr(e))
		sys.exit(-1)
		
		
		
# 判断要下载的对象是不是已经存在	
def can_download_mp4(mp4_path, name):
	try:		
		if os.path.exists(mp4_path) == False:
			return True
			
			
		if len(os.listdir(mp4_path)) == 0:
			return True
			
			
		for mp4 in os.listdir(mp4_path):
			if os.path.isfile(mp4_path + mp4) == True:
				if mp4.split('.')[-2] == name:
					return False
					
					
		return True
		
		
	except Exception as e:
		print('can_download_mp4():\n' + repr(e))
		sys.exit(-1)
		
		
		
# 检测ts能不能下载，不能下载就直接跳过视频
def can_download_ts(ts_part_url, sum_ts_clips):
	try:
		name = '%03d' %int(sum_ts_clips / 2)
		
		
		ts_url = ts_part_url + name + '.ts'
		
		
		if get_res(ts_url, 10, 'res_byte') == False:
			return False
		else:
			return True
		
		
	except Exception as e:
		print('can_download_ts():\n' + repr(e))
		sys.exit(-1)
		
		
		
############################################################################################################################################################		
if __name__ == '__main__':
	main()