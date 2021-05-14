# initialize the framework.

import os

if os.path.exists('app'):
	# name /app->/framework
	parent = os.path.split(os.getcwd())[1]
	os.rename('app', parent+'_app')
	# edit app.bat file
	with open('app.bat', 'rt') as f:
		contents = f.read()
	contents = contents.replace('app/', parent+'_app/')
	with open('app.bat', 'wt') as f:
		f.write(contents)
