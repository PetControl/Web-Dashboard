from flask import Flask, render_template, request, redirect, json
import twilio.twiml
from twilio.rest import TwilioRestClient
from PIL import Image
import urllib2
import cookielib
import io
import zbarlight
import MySQLdb

app = Flask(__name__)

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

db = MySQLdb.connect(host="petfinderdb.c1y1gazlb9dv.us-east-1.rds.amazonaws.com",    # your host, usually localhost
                     user="AdamMc331",         # your username
                     passwd="PetFinder331",  # your password
                     db="petfinderdb") 

def notifyOwner(petID):
    print(petID)
    #TODO: FIX
    petInfo = json.loads(getInfo(petID))
    number = petInfo.get('owner').get('phone')

    client = TwilioRestClient()
    client.messages.create(
        to=number,
        from_="+15869913157",
        body="A user has scanned your pet!"
    )

    return True
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

    codes = zbarlight.scan_codes('qrcode', image)
    print('QR codes: %s' % codes)
    if codes is None:
        return None
    return codes[0]

def get_redirected_url(url):
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

def getInfo(petID):
    #TODO: Have this connect to the DB lmao
    cur = db.cursor()
    cur.execute("SELECT p.id AS petId, p.name, p.breed, p.notes, o.id AS ownerID, o.firstName, o.lastName, o.address, o.phone FROM pet p JOIN owner o ON o.id=p.ownerId WHERE p.id=\"" + petID + "\";")
    rows = cur.fetchall()
    for row in rows:
        pet = {
            'id': row[0],
            'name': row[1],
            'breed': row[2],
            'notes': row[3],
            'owner': {
                "id": row[4],
                "firstName": row[5],
                "lastName": row[6],
                "address": row[7],
                "phone": row[8]
            }
        }
    cur.close()
        return json.dumps(pet)
    return json.dumps({})

def getOwnerInfo(petID):
    ownerInfo = json.loads(getInfo(petID)).get('owner')
    result = 'Here is some information about my owner! Call them to let them know where I am!\n'
    result = result + ownerInfo.get('firstName') + ' ' + ownerInfo.get('lastName') + '\n'
    result = result + ownerInfo.get('phone')
    return result

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
        petID = request.form.get('Body')

    if petExits(petID):
        petInfo = json.loads(getInfo(petID))
        if notifyOwner(petID):
            resp.sms('The owner of ' + petInfo.get('name') + ' has been notified!')
            resp.sms(getOwnerInfo(petID))
            print str(petID)
        else:
            resp.sms('The owner of ' + petInfo.get('name') + ' could not be reached. Please try again :(')
    else:
        resp.sms('This QR code is either incorrect or this pet is not registered.')
    
    return str(resp)

@app.route("/text_in/error", methods=['GET', 'POST'])
def handle_errors():
    resp = twilio.twiml.Response()
    resp.sms("bruh")
    return str(resp)

@app.route("/getDoggoInfo", methods=['GET'])
def getDoggoInfo():
    doggoID = str(request.args.get('dogID'))
    if doggoID is None:
        return "blah"

    data = getInfo(doggoID)

    return data

@app.route("/addOwner", methods=['POST'])
def addOwner():
    #expecting an owner first name, last name, phone, address
    first = request.form.get('firstName')
    last = request.form.get('lastName')
    phone = request.form.get('phone')
    address = request.form.get('address')

    cur = db.cursor()
    try:
        cur.execute("INSERT INTO owner (firstName, lastName, address, phone) VALUES ('"+ first +"', '"+ last +"', '"+ address +"', '"+ phone +"');")
        cur.commit()
    except:
        cur.rollback()

    cur.close()


if __name__ == "__main__":
    app.run(debug=True)