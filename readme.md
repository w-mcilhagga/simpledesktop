# A Simple Desktop App Framework.

There are a few ways of writing desktop apps using HTML, CSS, and Javascript, for example [Electron](https://www.electronjs.org/) and [nwjs](https://nwjs.io/). However, these are quite complicated to set up, work with, and and distribute. They provide lots of services, but most of the time, we really only want access to the file system. 

File system access can be granted easy enough with a local server that runs cgi scripts. cgi also makes it easy to expand the capabilities of the local app beyond that if you need to. That's what this simple desktop app framework does.

## Installation.

You'll need python 3+ installed. Most people already do.

To make a desktop app:
1. Download and save the framework folder from here.
2. Rename the framework folder to whatever you want.
3. Run `init.py` (e.g. at command prompt type `py init.py`) to rename some folders. This is to avoid caching problems with the browser. You can delete `init.py` after this.
4. Put your HTML, Javascript, and CSS app files in the folder ending with `_app`
5. Run the app.bat file by e.g. double clicking it. The index.html page will pop up and you're ready to go.

You can download any folder from the demos directory and run its app.bat file to see what can be done. Once you've built your app, distribution is as simple as copying the renamed framework folder.

## Filesystem Access.

To get access to the file system, just include the following line in your index.html file:
```html
<script src='../scripts/fs.js'></script>
```
Then you can call the following (async) functions:

* `getfile(filename)` reads a named file from the local filesystem and returns it.
* `choosefile(options)` opens a dialog box to select a file, and returns it.
* `getdir(dirname)` reads a named directory listing
* `choosedir(options)` opens a dialog box to select a directory, and returns the listing
* `putfile(filename)` saves a file to the local filesystem with the given name
* `putfileas(options)` opens a save as dialog box and saves the file
* `delfile(filename)` deletes the file
* `deldir(dirname)` removes the directory, if empty; `deldir(dirname, true)` removes the directory recursively.
* `mkdir(dirname)` makes a directory
* `copy(source, dest)` copies a file.

All these functions return a promise which resolves to an object. The properties of the object depends on the call. See [fs docs](docs/fs.md) for details.

## Any Drawbacks?

1. The command window doesn't go away when you close the application.
2. You only have access to the file system; if you want to do anything else with the operating system, you'll have to write a cgi script in python, put it in the cgi-bin directory, and write your own fetch call.
3. You might run into cache problems while developing. With Chrome, hit ctrl+F5 to flush the cache and reload.
