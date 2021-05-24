# basic wsgi server to handle local apps.
# serves static files from the /app directory.
# serves fs.js from the /server directory
# runs python code for POST requests, based on the URI:
#   /fs/cmd - file system commands
#   /app/cmd - application commands (stop)

import os
import sys
import json
import time
import datetime
import mimetypes
import base64
import wsgiref.util as util
from wsgiref.simple_server import make_server
import tkinter as tk
from tkinter import filedialog as fd
import socket
import webbrowser

# use TK to open the dialogs. Here we open the tk window, put it
# in front, and then hide it, so all dialogs pop over the webpage

root = tk.Tk()
root.attributes("-topmost", True)
root.withdraw()

def getmtype(filepath):
	# guesses the mimetype from the file
	mtype, menc = mimetypes.guess_type(filepath)
	# correct mime types
	if filepath.endswith('.csv'):
		mtype='text/csv'
	if filepath.endswith('.md'):
		mtype='text/markdown'
	if mtype=='application/javascript':
		mtype='text/javascript' 
	return mtype
	
def istext(mtype):
	# returns true if this is a text mimetype
	if 'text' in mtype:
		return True
	if mtype=='application/json':
		return True
	if mtype.endswith('xml'):
		return True
	return False

def readfile(filepath):
	# reads a file guessing the mimetype
	# Attempt to work out the content-type.
	# returns headers, content
	mtype = getmtype(filepath)
	# Actually read the file & decode it to bytes.
	try:
		with open(filepath, "rb") as f:
			content = f.read()
		headers = []
		if mtype is not None:
			headers.append(('Content-Type', mtype))
		headers.append(('Content-Length', str(len(content))))
		return headers, content	
	except:
		return None, None

# /fs route handlers

def choosefile(options):
	# chooses a file and returns it if text.
	#
	# the options dict has the following properties:
	#  'dialog_options' - options to pass to the dialog, or {}
	#  'astext' - a list of file extensions to be considered text, or []
	#
	# returns a dict containing 
	#   filename - the name of the chosen file
	#   text - if it is a text file.
	fname = fd.askopenfilename(**options['dialog_options'])
	if fname == '': # nothing was chosen
		return False
	if os.path.splitext(fname)[1] in options['astext'] or istext(getmtype(fname)):
		# text file, return the file contents
		return getfile({'filename':fname, 'astext':True})
	else:
		# binary file, just return the name, client has to get the contents later
		return {'filename':fname}
	
def getfile(options):
	# read the file contents and return as a string or bytes
	# options contains
	#   filename - the name of the file
	#   astext - True to treat as text, regardless of mime type
	# returns a dict with filename and text or blob attributes
	fname = options['filename']
	try:
		headers, content = readfile(fname)
		# headers might not have a content type.
		ctype = headers[0][1]
		print(fname, ctype)
		if ctype=='application/json':
			return {'filename':fname, 'json': json.loads(content) }
		if 'text' in ctype or options.get('astext', False):
			return {'filename':fname, 'text': content.decode('utf-8') }
		else:
			return {'filename':fname, 'blob': content, 'Content-Type': ctype }
	except:
		return False
	
def choosedir(dialog_options):
	# open dialog to choose directory, then return it
	dirname = fd.askdirectory(**dialog_options)
	if dirname=='':
		return False
	else:
		return getdir(dirname)
	
def getdir(dirname):
	# list the directory
	dlist = []
	dirname = os.path.abspath(dirname).replace('\\','/')
	for name in os.listdir(dirname):
		fullname = os.path.join(dirname, name)
		props = {'name':name, 
			'time': datetime.datetime(*time.gmtime(os.path.getmtime(fullname))[:6]).isoformat(), 
			'isfile':os.path.isfile(fullname)}
		dlist.append(props)
	return {'directory':dirname, 'listing':dlist}

def putfileas(data):
	# save file to disk
	fname = fd.asksaveasfilename(**data.get('dialog_options',{}))
	# if no filename, exit
	if fname=='':
		return False
	data['filename'] = fname
	return putfile(data)

def putfile(data):
	fname = data['filename']
	if 'text' in data:
		with open(fname, 'wt') as f:
			f.write(data['text'])
		return {'filename':fname}
	if 'json' in data:
		with open(fname, 'wt') as f:
			JSON.dump(data['json'], f)
		return {'filename':fname}
	if 'blob' in data:
		with open(fname, 'wb') as f:
			f.write(data['blob'])	
		return {'filename':fname}
	return {'filename':fname}
	
def delfile(data):
	# remove a file
	fname = data.get('filename')
	try:
		os.remove(fname)
		return {'filename':fname, 'deleted':True}
	except:
		return {'filename':fname, 'deleted':False}

def deldir(data):
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
		{'directory':dirname, 'deleted':False}
			
def mkdir(dirname):
	# make a directory, and return the new directory name in a dict
	try:
		os.mkdir(dirname)
		return {'directory':dirname}
	except:
		return False
		
def copy(data):
	# copies a file data['source'] to a file or directory data['dest'] and
	# returns the copied filename in a dict
	try:
		fname = shutil.copy(data['source'], data['dest'])
		return {'filename':fname}
	except:
		return False

def stopserver(data):
	# stops the server loop
	srv.serving = False
	return True
	
routes = {
	'/fs/getfile': getfile,
	'/fs/choosefile': choosefile,
	'/fs/getdir': getdir,
	'/fs/choosedir': choosedir,
	'/fs/putfileas': putfileas,
	'/fs/putfile': putfile,
	'/fs/delfile': delfile,
	'/fs/deldir': deldir,
	'/fs/mkdir': mkdir,
	'/fs/copy': copy,
	'/app/stop': stopserver
}

import re

def parsemulti(b, boundary):
	# parses a multipart message
	b = b.split(b'--'+boundary.encode())
	out = {}
	name = re.compile(r'name="(\w*)"')
	for part in b:
		lines = part.replace(b'\r',b'').split(b'\n')
		prop = None
		value = None
		for i,line in enumerate(lines):
			if line.startswith(b'Content-Disposition'):
				line = line.decode("utf-8")
				m =name.search(line)
				if m is not None:
					prop = m.group(1)
					print(prop)
			elif len(line)==0 and prop is not None:
				# blank line between header and contents
				break
		try:
			value = lines[i+1]
		except:
			pass
		if prop is not None and value is not None:
			out[prop]=value
			if prop=='filename':
				out[prop] = out[prop].decode('utf-8')
	return out


def router(environ, start_response):
	# handles file system requests 
	# get the request data
	path = environ['PATH_INFO']
	length = int(environ.get('CONTENT_LENGTH', '0'))
	request = environ['wsgi.input'].read(length)
	ctype = environ.get('CONTENT_TYPE', '')
	if ctype=='application/json':
		request = json.loads(request.decode())
	else: # multipart
		m = re.compile('boundary=(.*)').search(ctype)
		request = parsemulti(request, m.group(1))
	# run the request
	body = routes[path](request)
	if type(body) is dict and 'blob' in body:
			# binary stream
			start_response('200 OK', [
				('Content-Type', body['Content-Type']), 
				('Content-Length', str(len(body['blob'])))])	
			return [body['blob']]
	else:
		# treat as a json object
		body = json.dumps(body).encode()
		start_response('200 OK', [
			('Content-Type', 'application/json'), 
			('Content-Length', str(len(body)))])
		return [body]

def serve_static(environ, start_response):
	# deals with *all* get requests by serving from the app 
	# directory. Maps path='/'  to file='app/index.html'
	# needs to fix up binary serving.
	path = environ['PATH_INFO']
	fname = ''
	if path=='/':
		fname = 'app/index.html'
	elif path=='/server/fs.js':
		fname = 'server/fs.js'
	else:
		# all app resources served from app/ folder, but no checks 
		# to see if this is really local.
		fname = 'app'+path
	headers, content = readfile(fname)
	if headers is None:
		start_response('404 Not Found', [])
		return []
	# make sure pages aren't cached
	headers.append(('Cache-Control', 'max-age=0'))
	start_response('200 OK', headers)
	return [content]


def myapp(environ, start_response):
	if environ['REQUEST_METHOD']=='GET':
		# serve static files from /app.
		return serve_static(environ, start_response)
	elif environ['REQUEST_METHOD']=='POST':
		# run one of the file system functions
		return router(environ, start_response)

def scanport():
	# find a free localhost port
	for port in range(8000, 8100):  
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(0.3)
		result = sock.connect_ex(('localhost', port))
		sock.close()
		if result != 0:
			return port
			
if __name__ == '__main__':
	port = scanport()
	srv = make_server('127.0.0.1', port, myapp)
	#srv.serve_forever() - this seems faster 
	srv.serving = True
	print('serving at localhost:'+str(port))
	webbrowser.open('http://localhost:'+str(port))
	while srv.serving:
		srv.handle_request()
