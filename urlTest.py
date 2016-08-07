import zbarlight
import io
from PIL import Image
import urllib2

url='http://media.twiliocdn.com.s3-external-1.amazonaws.com/ACa52bfd8d5b49c0c3fa25cc747a8767b6/934939f4b7ecb2e8d839d4e443333cba'

fd = urllib2.urlopen(url)
image_file = io.BytesIO(fd.read())
image = Image.open(image_file)

print(image)

codes = zbarlight.scan_codes('qrcode', image)

print(codes)