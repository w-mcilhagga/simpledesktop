// routines to communicate with the local server

function decode_response(response) {
	// tries to decode a response received from the server.
	let ctype = response.headers.get('Content-Type')
	console.log(ctype)
	if (ctype=='application/json') {
		return response.json()
	}
	if (ctype.includes('text')) {
		return response.text()
	}
	return response.blob()
}

function do_post(url, body) {
	// body is either a json object or a formdata object
	if (body instanceof FormData) {
		return fetch(url, {
				method:'POST', 
				body
			}).then(decode_response) 		
	} else {
		return fetch(url, {
				method:'POST', 
				body: JSON.stringify(body),
				headers: {'Content-Type': 'application/json'}
			}).then(decode_response) 
	}
}

/*
POST URLs are:
/fs/getfile - reads file contents; returns json
/fs/choosefile - opens dialog to pick file, and reads it; returns json
/fs/putfile - writes file contents as json, text, or blob
/fs/putfileas - opens dialog to select file name, writes it  as json, text, or blob
/fs/getdir - gets contents of directory as json
/fs/choosedir - selects directory with dialog and returns contents as json
/fs/delfile, 
/fs/deldir - removes file or directory
/fs/copy - copies file
/app/stop - closes down the server
*/

function filterobj(obj, ...keys) {
	// only lets through keys in obj if in keys list, to remove invalid
	// tk dialog options
	let newobj = {}
	for (let k of Object.keys(obj)) if (keys.includes(k)) {
		newobj[k] = obj[k]
	}
	return newobj
}

async function getfile(filename, astext) {
	// get a file from the local file system.
	// takes:
	// filename:  the name of the file
	// astext: (optional) true if the file is to be treated as text, regardless
	//         of the mimetype
	// returns a json object with properties:
	//   filename: the name of the file (from the input)
	//   text: the file contents, if a text file
    //   blob: the file contents, if a binary file
	astext = !!astext
	let result = await do_post('/fs/getfile', {filename, astext})
	if (result instanceof Blob) {
		return {filename, blob:result}
	}
	if (typeof(result) == 'string') {
		// this may never happen
		return {filename, text:result}
	}
	return result
}

async function choosefile(dialog_options, astext) {
	// pops up a dialog to choose a file.
	// takes:
	// dialog_options: object with (optional) properties:
	//    title - the dialog box title
	//    initialfile - the initial filename to choose
	//    initialdir - the initial directory to open the dialog box in
	//    defaultextension - the default extension in the open dialog
	//    multiple - true or false, not currently used
	//    filetypes - an array of file types allowed. Each filetype is a pair of [type description, extensions]
	//             extensions is a space separated list of allowed extensions. For example:
	//             [('Image files', '*.jpg *.png'), ('All files', '*.*')]
	//
	// astext: an optional array of file extensions that are treated as text regardless
	//          existing known text file mimetypes; default is []	
	// returns a json object with properties:
	//   filename: the name of the file (from the input)
	//   text: the file contents, if a text file
    //   blob: the file contents, if a binary file
	// i.e. just the same as gettext
	dialog_options = filterobj(dialog_options || {}, 
						'title', 'initialfile', 'initialdir', 'defaultextension', 
						'multiple', 'filetypes'
					 )
	astext = astext || []
	let result = await do_post('/fs/choosefile', {dialog_options, astext})
	// if the file is binary, we need to do a separate getfile to get the file.
	if (result===false || result.text || result.json) {
		return result
	}
	// otherwise it's a binary file, get the contents
	return await getfile(result.filename)
}

async function getdir(directory) {
	// get a directory listing.
	// returns an object {directory, list} or to false if something went wrong. 
	// directory contains the absolute directory path. list is a list of
	// {name, isfile, date} objects which give the file or directory name, a boolean isfile,
	// and the creation date as an ISO datetime string (i.e in the GMT timezone).
	return await do_post('/fs/getdir', directory)	
}

async function choosedir(dialog_options) {
	// pops up a dialog to choose the directory, using the properties
	// in the options object. Option properties are:
	//    title: the dialog box title
	//    initialdir: the initial directory to open the dialog box in
	//    mustexist: can only select existing directories
	dialog_options = filterobj(dialog_options||{}, 'title', 'initialdir', 'mustexist')
	return await do_post('/fs/choosedir', dialog_options)		
}

async function putfile(filename, contents) {
	// saves a file. if the contents are a blob, turn this into formdata
	if (typeof(contents)=='string') {
		return await do_post('/fs/putfile', {filename, text:contents})
	}
	if (contents instanceof Blob) {
		let fd = new FormData()
		fd.append('filename', filename)
		fd.append('blob', contents)
		console.log(fd)
		return await do_post('/fs/putfile', fd)
	} 
	return await do_post('/fs/putfile', {filename, json:contents})
}

async function putfileas(contents, dialog_options) {
	// saves a file, popping up a dialog to choose it. options can have
	// the following properties:
	//    title - the dialog box title
	//    initialdir - the initial directory to open the dialog box in
	//    initialfile - the initial filename to use (overwritten by filename)
	dialog_options = filterobj(dialog_options||{}, 'title', 'initialdir', 'initialfile', 'defaultextension')
	if (typeof(contents)=='string') {
		return await do_post('/fs/putfileas', {text:contents, dialog_options})
	}
	if (contents instanceof Blob) {
		console.log('isblob')
		let result = await do_post('/fs/putfileas', {dialog_options})
		console.log(result)
		if (result) {
			return putfile(result.filename, contents) 
		}
	}
	return await do_post('/fs/putfileas', {json:contents, dialog_options})
}

async function delfile(filename) {
	// deletes a file
	return await do_post('/fs/delfile', {filename})		
}

async function deldir(directory, recursive) {
	// deletes a directory and (possibly) all files and directories within
	return await do_post('/fs/deldir', {directory, recursive})		
}

async function mkdir(directory) {
	// creates a directory
	return await do_post('/fs/mkdir', {directory})		
}

async function copy(source, dest) {
	// copies a file in the os; dest can be a directory
	return await do_post('/fs/copy', {source, dest })
}

