from flask import Flask, render_template, request, redirect, json
import twilio.twiml
from twilio.rest import TwilioRestClient
from PIL import Image
import urllib2
import cookielib
import io
import zbarlight
<<<<<<< HEAD
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection
=======
import MySQLdb
>>>>>>> 7fae3ac2735da7518b08cf40d63a5d0cb71b0f6a

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
        sql = "INSERT INTO owner (firstName, lastName, address, phone) VALUES (%s, %s, %s, %s);"
        cur.execute(sql, (first, last, phone, address))
        db.commit()
    except:
        db.rollback()
        print("addOwner: rollback")

    #TODO: Get the id of the new owner and return it in a json obj
    cur.execute('SELECT LAST_INSERT_ID()')
    lastID = cur.fetchone()

    cur.close()

    return str(lastID[0])

@app.route("/addPet", methods=['POST'])
def addPet():
    name = request.form.get('name')
    breed = request.form.get('breed')
    notes = request.form.get('notes')
    ownerID = request.form.get('ownerID')

    cur = db.cursor()
    try:
        sql = "INSERT INTO pet (name, ownerId, breed, notes) VALUES (%s, %s, %s, %s);"
        cur.execute(sql, (name, ownerID, breed, notes))
        db.commit()
    except:
        db.rollback()
        print("addPet: rollback")

    #TODO: Get the id of the new owner and return it in a json obj
    cur.execute('SELECT LAST_INSERT_ID()')
    lastID = cur.fetchone()

    return str(lastID[0])

if __name__ == "__main__":
    app.run(debug=True)