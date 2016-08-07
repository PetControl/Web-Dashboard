from flask import Flask, render_template, request, redirect
import twilio.twiml
from PIL import Image
import urllib2 as urllib
import cookielib
import io
import zbarlight
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

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
    item1 = getItem(0)
    item2 = getItem(1)
    item3 = getItem(2)
    return render_template('index.html', ebayTitleOne = item1.title, ebayTitleTwo = item2.title, ebayTitleThree = item3.title, ebayLocationOne = item1.location, ebayLocationTwo = item2.location, ebayLocationThree = item3.sellingStatus.currentPrice.value, ebayPriceOne = item1.sellingStatus.currentPrice.value, ebayPriceTwo = item2.sellingStatus.currentPrice.value, ebayPriceThree = item3.sellingStatus.currentPrice.value, ebayUrlOne = item1.viewItemURL, ebayUrlTwo = item2.viewItemURL, ebayUrlThree = item3.viewItemURL)

@app.route('/fuckinghell')
def getItem(num):
    try:
        api = Connection(domain='svcs.sandbox.ebay.com', appid='TristanW-PetContr-SBX-3577624e3-6f8339d7', config_file=None)
        response = api.execute('findItemsAdvanced', {'keywords': 'Dog Food'})

        assert(response.reply.ack == 'Success')
        assert(type(response.reply.timestamp) == datetime.datetime)
        assert(type(response.reply.searchResult.item) == list)

        item = response.reply.searchResult.item[num]

        assert(type(item.listingInfo.endTime) == datetime.datetime)
        assert(type(response.dict()) == dict)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())
    return item;

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