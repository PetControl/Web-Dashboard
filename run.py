from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

def notifyOwner(petID):
    number = getInfo(petID, "ownerNumber")
    #Figure out how to send a text to a number here
    #Text owner whatever is in the "text" variable

def petExits(petID):
    #TODO: Have this communicate to the DB and get a real answer
    return True

def parseQRCode(imageURI):
    fd = urllib.urlopen(imageURI)
    image_file = io.BytesIO(fd.read())
    image = Image.open(image_file)
    image.load()

    codes = zbarlight.scan_codes('qrcode', image)
    print('QR codes: %s' % codes)
    return codes[0]

def getInfo(petID, key):
    #TODO: Have this connect to the DB lmao
    return ""

@app.route("/text_in", methods=['GET', 'POST'])
def direct_request():

    resp = twilio.twiml.Response()

    # Get the pet id
    petID = None
    if request.form.get('NumMedia') == 1:
        #need to parse the qr code to get the dog id
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
def handle_errors:
    resp = twilio.twiml.Response()
    resp.sms("bruh")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)