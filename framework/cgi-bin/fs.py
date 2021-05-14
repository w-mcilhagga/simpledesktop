# cgi script to read get/post json data, as a common way to 
# interface to the host computer

import os
import sys
import json
import time

# dialogs to choose a file or directory

import tkinter as tk
from tkinter import filedialog as fd

def start_tk():
	# starts a background tk window to host the dialogs
	root = tk.Tk()
	root.attributes("-topmost", True)
	root.withdraw()
	
def get_filename(mode, dlg_options):
	# gets a file for opening or saving
	# mode='open' or 'save'
	# options is a dict
	options = {}
	for key in ['title', 'initialdir', 'initialfile', 'defaultextension', 'multiple', 'filetypes']:
		v = dlg_options.get(key)
		if v is not None:
			options[key] = v
	start_tk()
	if mode=='open':
		return fd.askopenfilename(**options)
	elif mode=='save':
		return fd.asksaveasfilename(**options)

def get_dirname(dlg_options):
	# gets a directory name
	options = {}
	for key in ['title', 'initialdir']:
		v = dlg_options.get(key)
		if v is not None:
			options[key] = v
	start_tk()
	return fd.askdirectory(**options)

# return false has to be changed, since the js file expects json

def handle_request(data):
	# handles the various requests that come through in json packages
	
	if data['request']=='getfile':
		# get a file from disk
		# get filename if not specified
		fname = data.get('filename')
		if fname is None:
			fname = get_filename('open', data.get('dialog_options', {}))
		# if no filename, exit
		if fname=='':
			return False
		# otherwise, read the  file if it's the right type
		# and return it
		result = {'filename':fname}
		with open(fname, 'rt') as f:
			ext = os.path.splitext(fname)[1]
			if ext in ['.txt', '.text', '.csv', '.html', '.js', '.py', '.bat']+data.get('istext',[]):
				result['contents'] = f.read()
			elif ext=='.json':
				result['contents'] = json.load(f)
			else:
				pass # not a text file, need to do something else
		return result

	if data['request']=='putfile':
		# save file to disk
		fname = data.get('filename')
		if fname is None:
			fname = get_filename('save', data.get('dialog_options', {}))
		# if no filename, exit
		if fname=='':
			return False
		if data.get('contents',False):
			with open(fname, 'wt') as f:
				f.write(data['contents'])
		elif data.get('blob',False):
			with open(fname, 'wb') as f:
				f.write(data['blob'])
		return {'filename':fname} # for the saveas case, ignore when just saving

	if data['request']=='getdir':
		# list a directory
		dirname = data.get('directory')
		if dirname is not None:
			dirname = os.path.abspath(dirname)
		else:
			# find the directory
			dirname = get_dirname(data.get('dialog_options', {}))
		# list the directory
		from datetime import datetime
		dlist = []
		for name in os.listdir(dirname):
			fullname = os.path.join(dirname, name)
			props = {'name':name, 
				'time': datetime(*time.gmtime(os.path.getmtime(fullname))[:6]).isoformat(), 
				'isfile':os.path.isfile(fullname)}
			dlist.append(props)
		return {'directory':dirname, 'listing':dlist}

	if data['request']=='delfile':
		# remove a file
		fname = data.get('filename')
		try:
			os.remove(fname)
			return {'filename':fname, 'deleted':True}
		except:
			return {'filename':fname, 'deleted':False}

	if data['request']=='deldir':
		# remove a directory
		dirname = data.get('directory')
		try:
			if data.get('recursive') is True:
				import shutil
				shutil.rmtree(dirname)
			else:
				os.rmdir(fname)
			return {'directory':dirname, 'deleted':True}
		except:
			return {'directory':dirname, 'deleted':False}
			
	if data['request']=='mkdir':
		# make a directory
		os.mkdir(data['directory'])
		return {'directory':data['directory']}
		
	if data['request']=='copy':
		fname = shutil.copy(data['source'], data['dest'])
		return {'filename':fname}
				
	return False 
		
		
		
# read the json
content_len = os.environ.get('CONTENT_LENGTH', '0')
content_type = os.environ.get('CONTENT_TYPE', '0')

if content_type!='application/json':
	# do something here
	pass
	
body = sys.stdin.read(int(content_len))
data = json.loads(body)

# process the json based on data['request']
print("Content-Type: application/json")
print()
print(json.dumps(handle_request(data)))