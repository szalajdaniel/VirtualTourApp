from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Ścieżka do folderu, w którym znajdują się zdjęcia
photos_folder = os.path.expanduser("~/OneDrive/Dokumenty/SZKOŁA/pracadyplomowa/static")

# Pobranie listy nazw zdjęć z folderu
photos = sorted([filename for filename in os.listdir(photos_folder) if filename.endswith('.jpg')])
print(photos)
@app.route('/')
def index():
    return render_template('index.html', photos=photos)

if __name__ == '__main__':
    app.run(debug=True)
