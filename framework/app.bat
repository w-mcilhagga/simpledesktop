start /B py -m http.server --bind localhost --cgi 8000
py -m webbrowser http://localhost:8000/app/index.html