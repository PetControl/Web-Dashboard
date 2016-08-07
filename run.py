from flask import Flask, render_template, request, redirect
import twilio.twiml
from PIL import Image
import urllib2 as urllib
import cookielib
import io
import zbarlight

app = Flask(__name__)
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def notifyOwner(petID):
    number = getInfo(petID, "ownerNumber")
    #Figure out how to send a text to a number here
    #Text owner whatever is in the "text" variable

def petExits(petID):
    #TODO: Have this communicate to the DB and get a real answer
    return True

def parseQRCode(imageURI):
    req = urllib2.Request(imageURI, headers=hdr)

    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()

    fd = urllib2.urlopen(page.url)
    image_file = io.BytesIO(fd.read())
    image = Image.open(image_file)
    image.load()

    codes = zbarlight.scan_codes('qrcode', image)
    print('QR codes: %s' % codes)
    return codes[0]

def get_redirected_url(url):
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

def getInfo(petID, key):
    #TODO: Have this connect to the DB lmao
    return ""

@app.route('/')
def main():
    return render_template('index.html')

@app.route("/text_in", methods=['GET', 'POST'])
def direct_request():

    resp = twilio.twiml.Response()
    # Get the pet id
    petID = None
    if str(request.form.get('NumMedia')) == '1':
        #need to parse the qr code to get the dog id
        print("yeeee")
        petID = parseQRCode(request.form.get('MediaUrl0'));
    else:
        #assume the body contains the pet id
        petID = request.body

    if petExits(petID):
        if notifyOwner(petID, "Your dog has been scanned."):
            resp.sms("The owner was contacted! Thank you!")
        else:
            resp.sms("The owner could not be reached. Please try again :(")
    else:
        resp.sms("This QR code is either incorrect or this pet is not registered.")
    
    return str(resp)

@app.route("/text_in/error", methods=['GET', 'POST'])
def handle_errors():
    resp = twilio.twiml.Response()
    resp.sms("bruh")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)