from flask import Flask, render_template
from PIL import Image
import urllib2 as urllib
import io
import zbarlight

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')
