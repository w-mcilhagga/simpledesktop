# A Simple Desktop App Framework.

There are a few ways of writing desktop apps using HTML, CSS, and Javascript, for example [Electron](https://www.electronjs.org/) and [nwjs](https://nwjs.io/). But these are quite complicated to set up, work with, and and distribute. They provide lots of services, but most of the time, we really only want access to the file system. 

File system access can be granted easy enough with a local server that runs cgi scripts. cgi also makes it easy to expand the capabilities of the local app beyond that if you need to. That's what this simple desktop app framework does.

A **lot** of the functionality in this framework is already provided (experimentally) by the [File System Access API](https://wicg.github.io/file-system-access/), but not all.

## Installation.

You'll need python 3+ installed to run the server. Most people already do.

To make a desktop app:
1. Download and save the `framework` folder.
2. Rename the framework folder to whatever app name you want.
4. Put your HTML, Javascript, and CSS files in the `/app` folder
5. Run the app.bat file by e.g. double clicking it. The index.html page will pop up and you're ready to go.

You can download any folder from the demos directory and run its app.bat file to see what can be done. Once you've built your app, distribution is as simple as copying the renamed `framework` folder.

## Filesystem Access.

To get access to the file system, just include the following line in your index.html file:
```html
<script src='server/fs.js'></script>
```
Then you can call the following (async) functions:

* `getfile(filename)` reads a named file from the local filesystem and returns it.
* `choosefile(options)` opens a dialog box to select a file, and returns it.
* `getdir(dirname)` reads a named directory listing
* `choosedir(options)` opens a dialog box to select a directory, and returns the listing
* `putfile(filename)` saves a file to the local filesystem with the given name
* `putfileas(options)` opens a save as dialog box and saves the file
* `delfile(filename)` deletes the file
* `deldir(dirname)` removes an empty directory; `deldir(dirname, true)` removes a directory recursively.
* `mkdir(dirname)` makes a directory
* `copy(source, dest)` copies a file
* `stop()` stops and closes the server

All these functions return a promise which resolves to an object. The properties of the object depends on the call. See [fs docs](docs/fs.md) for details.

## Any Drawbacks?

1. The command window doesn't go away when you close the application.
2. You only have access to the file system.
