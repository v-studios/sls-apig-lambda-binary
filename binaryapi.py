# Demonstrate binary in/out for Lambda fronted by API Gateway:
# take an incoming GIF, convert to JPEG and return it.
#
# This expects to be called with a binary payload and headers to cause APIG to
# do binary/string conversion to/from Lambda.::
#
#     curl -H "Content-Type: image/gif" -H "Accept: image/jpeg" \
#          --data-binary @CSLOGO.gif $API
#
# You must set APIG Binary Support for the content types in AWS Console.

from base64 import b64decode, b64encode
from json import dumps
from subprocess import check_output


def handler(event, context):
    # The data should have been sent with Content-Type that the APIG recognizes
    # as binary so it will base64-encode it to us. Decode and save image.

    if event['headers']['Content-Type'] != 'image/gif':
        return {'statusCode': 400,
                'body': dumps({'message': 'Content-Type must be image/gif'})}
    if event['isBase64Encoded'] is False:
        return {'statusCode': 400,
                'body': dumps({'message': 'APIG did not provide base64 data'})}

    img_gif = b64decode(event['body'])
    with open('/tmp/img.gif', 'wb') as img_fp:
        img_fp.write(img_gif)

    # Do the conversion here (whatever your app needs, could be a thumbnailer)

    check_output(['convert', '/tmp/img.gif', '/tmp/img.jpg'])

    # To return binary, we must Base64 encode the output image and convert
    # those bytes to UTF string for JSON body.  The request must set the header
    # "Accept: image/jpeg" for the APIG to turn the encoded string in to binary
    # for the client HTTP response.

    if event['headers']['Accept'] != 'image/jpeg':
        return {'statusCode': 400,
                'body': dumps({'message': 'Accept must specify image/jpeg'})}

    img_jpg = open('/tmp/img.jpg', 'rb').read()
    out_b64 = b64encode(img_jpg)
    out_str = out_b64.decode('utf8')

    # Set status and return output as JSON string which APIG converts to binary
    # APIG ignores the Content-Type here, only looking at client Accept header
    # but we want to tell the final client the type.

    return {
        'statusCode': 200,
        'body': out_str,
        'isBase64Encoded': True,
        'headers':  {'Content-Type': 'image/jpeg'},
    }
