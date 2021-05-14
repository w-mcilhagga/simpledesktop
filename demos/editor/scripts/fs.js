// routines to communicate with the local server

let path_to_cgi = '../cgi-bin/' // adjust this as needed


async function cgi_request(progname, body) {
	// path_to_cgi gives the relative path from the webpage making the
	// request to the cgi folder. For example, '../'
	return await fetch(path_to_cgi+progname, {
			method:'post', 
			body: JSON.stringify(body),
			headers: new Headers({'Content-Type': 'application/json'})
		}).then(response=>response.json()).catch(()=>false)
}

function fs_request(body) {
	// path_to_cgi gives the relative path from the webpage making the
	// request to the cgi folder. For example, '../'
	return cgi_request('fs.py', body)
}

async function getfile(filename) {
	// returns a promise which resolves to a {filename, contents} object
	return fs_request({
			request:'getfile',
			filename
		})	
}

async function choosefile(dialog_options, istext) {
	// pops up a dialog to choose a file, and returns a promise which resolves to 
	// a {filename, contents} object
	//
	// dialog_option properties are:
	// title - the dialog box title
	// initialdir - the initial directory to open the dialog box in
	// defaultextension - the default extension in the open dialog
	// multiple - true or false, not currently used
	// filetypes - an array of file types allowed. Each filetype is a pair of [type description, extensions]
	//             extensions is a space separated list of allowed extensions. For example:
	//             [['Image files', '*.jpg *.png'], ['All files', '*.*']]
	//
	// istext - an array of file extensions that are treated as text in addition to the defaults
	//
	// The promise resolves to false if something went wrong, or to an object. If it is a text file,
	// the promise resolves to {filename, contents} where contents is a string. If a json file, the promise
	// resolves to {filename, contents} where contents is an object.
	
	istext = istext || []
	return fs_request({
			request:'getfile',
			dialog_options,
			istext
		})
}

async function getdir(directory) {
	// returns a promise that resolves to a list of the files and 
	// folders in the given directory
	// The promise resolves to false if something went wrong, or to an object 
	// {directory, list}. directory contains the absolute directory path. list is a list of
	// {name, isfile, date} objects which give the file or directory name, a boolean isfile,
	// and the creation date as an ISO datetime string (i.e in the GMT timezone).	
	
	return fs_request({
			request: 'getdir',
			directory
		})	
}

async function choosedir(dialog_options) {
	// pops up a dialog to choose the directory, using the properties
	// in the options object. Option properties are:
	// title - the dialog box title
	// initialdir - the initial directory to open the dialog box in
	// 

	return fs_request({
			request: 'getdir',
			dialog_options
		})		
}

async function putfile(filename, contents) {
	// saves a file, no dialog
	return fs_request({
			request: 'putfile',
			filename,
			contents
		})	
}

async function putfileas(filename, contents, options) {
	// saves a file, popping up a dialog to choose it. options can have
	// the following properties:
	// title - the dialog box title
	// initialdir - the initial directory to open the dialog box in
	// initialfile - the initial filename to use
	return fs_request({
			request: 'putfile',
			contents,
			dialog_options: Object.assign({initialfile: filename}, options)
		})
}

async function delfile(filename) {
	// deletes a file
	return fs_request({
			request: 'delfile',
			filename,
		})
}

async function deldir(directory, recursive) {
	// deletes a directory and (possibly) all files and directories within
	return fs_request({
			request: 'deldir',
			directory,
			recursive
		})
}

async function mkdir(directory) {
	// creates a directory
	return fs_request({
			request: 'mkdir',
			directory,
		})
}

async function copy(source, dest) {
	// copies a file in the os; dest can be a directory
	return fs_request({
			request: 'copy',
			source,
			dest
		})
}

