# Demonstrate binary in/out for Lambda fronted by API Gateway:
# take an incoming form with GIF and filename, convert to JPEG and return it.
#
# This expects to be called with multipart/form-data payload and headers like::
#
#   curl -H "Accept: image/jpeg" -F file=@../CSLOGO.gif $API

from cgi import parse_header, parse_multipart
from base64 import b64decode, b64encode
from io import BytesIO
from json import dumps
from subprocess import check_output


def handler(event, context):
    # The data should have been sent with Content-Type that the APIG recognizes
    # as binary so it will base64-encode it to us. Decode and save image.

    content_type = event['headers']['Content-Type']
    if not content_type.startswith('multipart/form-data; boundary='):
        return {'statusCode': 400,
                'body': dumps(
                    {'message': 'Content-Type must be multipart/form-data'})}
    if event['isBase64Encoded'] is False:
        return {'statusCode': 400,
                'body': dumps({'message': 'APIG did not provide base64 data'})}

    # Parse the multipart form, we require at least 'file'

    (ctype, pdict) = parse_header(content_type)
    if type(pdict['boundary']) is not bytes:
        # fix parse_header bug: wants bytes for boundary, not str
        pdict['boundary'] = bytes(pdict['boundary'], 'utf8')

    body_bytes = b64decode(event['body'])
    body_fp = BytesIO(body_bytes)

    # parser does not get filename from content-disposition::
    #  Content-Disposition: form-data; name="file"; filename="CSLOGO.gif"
    # Live with it for now, we can ask for another field, `filename`.
    # lots of bug
    # complaints from 2009-2017 on this module not working.

    form = parse_multipart(body_fp, pdict)
    print('# form: {}'.format(form))
    print('# form.keys(): {}'.format(form.keys()))
    if 'file' not in form:
        return {'statusCode': 400,
                'body': dumps({'message': 'Form must have "file"'})}

    # Save the file contents and convert

    img_gif = form['file'][0]  # form could have multiples
    with open('/tmp/img.gif', 'wb') as img_fp:
        img_fp.write(img_gif)

    # Do the conversion here (whatever your app needs, could be a thumbnailer)

    check_output(['convert', '/tmp/img.gif', '/tmp/img.jpg'])

    ls = check_output('ls -al /tmp'.split())
    print('# ls: {}'.format(ls))

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
