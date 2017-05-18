#!/usr/bin/env python3
# Demonstrate binary in/out for Lambda fronted by API Gateway:
# take an incoming form with GIF and filename, convert to JPEG and return it.
#
# This expects to be called with multipart/form-data payload and headers like::
#
#   curl -H "Accept: image/jpeg" -F file=@../CSLOGO.gif $API

from cgi import parse_header, parse_multipart, FieldStorage, MiniFieldStorage
from base64 import b64decode, b64encode
from io import BytesIO
from json import dumps, loads
from subprocess import check_output
import urllib

def handler(event, context):
    print('# body: {}'.format(dumps({'event': event})))
    print('# isBase64Encoded={}'.format(event['isBase64Encoded']))

    # The data should have been sent with Content-Type that the APIG recognizes
    # as binary so it will base64-encode it to us. Decode and save image.

    # TODO: OMFG content-type header from HTML form (or via APIG?) are lowercase!!!
    # Also, the Accept header may not be matched by APIG Binary?
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

    content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
    if content_type != 'application/x-www-form-urlencoded':
        return {
            'statusCode': 400,
            'body': dumps(
                {'message':
                 'Content-Type "{}" must be application/x-www-form-urlencoded'.format(content_type)})}
    # if event['isBase64Encoded'] is not False:
    #     return {'statusCode': 400,
    #             'body': dumps({'message': 'APIG did not provide base64 data'})}

    # Parse the multipart form, we require at least 'file'

    # no boundary in xwfu
    body = event['body']
    if event['isBase64Encoded']:
        body = b64decode(body)
        print('# b64decoded body={}'.format(body))

    # body_bytes = bytes(body, 'utf8')
    # #body_bytes = b64decode(event['body'])
    # body_fp = BytesIO(body_bytes)
    # # fp=None, headers=None, outerboundary=b'', method=GET, keep_blank_values, strict_parsing; encoding?
    # # environ REQUEST_METHOD
    # form = FieldStorage(fp=body_fp,
    #                     headers={'content-type': content_type},
    #                     environ={'REQUEST_METHOD': 'POST'})
    # form: FieldStorage(None, None,
    #                    [MiniFieldStorage('FILENAME', 'CSLOGO'),
    #                     MiniFieldStorage('FILE', 'GIF87a\x1a\x...N\x04\n\x00;')])
    # Then form['FILE'].value, form['FILENAME'].value
    # This is same as gif above so no pointgoing through this work with FieldStorage.

    # This seems easy but the GIF I get is broken.
    body_str = body.decode('utf8')
    form = urllib.parse.parse_qs(body_str)  # wants str, not bytes
    print('# form: {}'.format(form))
    print('# form.keys(): {}'.format(form.keys()))
    if 'file' not in form:
        return {'statusCode': 400,
                'body': dumps({'message': 'Form must have "file"'})}

    # Save the file contents and convert
    img_gif = form['file'][0]  # form could have multiples
    print('# img_gif type={}'.format(type(img_gif)))
    if type(img_gif) != bytes:
        img_gif = bytes(img_gif, 'utf8')
        print('# img_gif type={}'.format(type(img_gif)))
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


if __name__ == '__main__':
    event = loads(open('event-xformurlencoded.json', 'r').read())  # NOT binary
    ret = handler(event, None)
    print(ret)
