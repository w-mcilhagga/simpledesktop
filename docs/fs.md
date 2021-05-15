## `fs`

To get access to the file system in your app, include the following line in your index.html file:
```html
<script src='../scripts/fs.js'></script>
```

The following functions are then available to you:

### `getfile(filename)` 
Read a named file from the local filesystem and return it. The filename is a string giving the absolute or relative path to the file. `getfile` returns a promise which resolves to an object with two properties if it succeeds:
* `filename`: the name of the file
* one of:
  - `contents` if the file is a text file, or
  - `blob` if the file is a binary file (not actually implemented yet)

If it fails, it resolves to `false`. 
### `choosefile(options)` 
Open a dialog box to select a file, and return the file. `options`, if present,  controls the dialog box. It may have the following properties:
* `title` - (string) the dialog box title
* `initialdir` - (string) the initial directory to open the dialog box in
* `defaultextension` - (string) the default extension in the open dialog
* `multiple` - true or false, not currently used
* `filetypes` - an array of file types allowed. Each filetype is a pair of `[type description, extensions]`.
            extensions is a space separated list of allowed extensions. For example:
           `[['Image files', '*.jpg *.png'], ['All files', '*.*']]`

If it fails or is cancelled, it resolves to `false`. 
### `getdir(dirname)` 
List files and folders in the given `dirname`. The function returns a promise which resolves to an object with the following properties:
* `directory` - the absolute directory path. 
* `list` an array of  `{name, isfile, date}` objects which give the file or directory name, a boolean `isfile`, and the creation `date` as an ISO **datetime** string (i.e in the GMT timezone).

If it fails, it resolves to `false`.	
### `choosedir(options)` 
Open a Select Folder dialog box to select a directory, and resolve to the directory listing, or `false` if it fails. 
### `putfile(filename)` 
Save a file to the local filesystem with the given name.
### `putfileas(options)` 
Open a save as dialog box and saves the file. `options`, if present,  controls the dialog box. It may have the following properties:
* `title` - (string) the dialog box title
* `initialdir` - (string) the initial directory to open the dialog box in
* `defaultextension` - (string) the default extension in the open dialog

### `delfile(filename)` 
Deletes the file.
### `deldir(dirname)` 
Removes the directory, if empty. If you want to remove a directory recursively, call `deldir(dirname, true)`.
### `mkdir(dirname)` 
Makes a directory.
### `copy(source, dest)` 
Copies a file. `dest` may be either a full filename or a directory name. 