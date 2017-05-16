# Demonstrate binary in/out for Lambda fronted by API Gateway:
# take an incoming form with GIF and filename, convert to JPEG and return it.
#
# This expects to be called with multipart/form-data payload and headers like::
#
#     curl -F filename=CSLOGO.gif -F file=@CSLOGO.gif $API

from cgi import FieldStorage, parse_header, parse_multipart
from base64 import b64decode, b64encode
from io import BytesIO
from json import dumps, loads
from subprocess import check_output
from traceback import format_exc


def handler(event, context):
    try:
        print('# event: {}'.format(event))

        content_type = event['headers']['Content-Type']
        (ctype, pdict) = parse_header(content_type)
        print('# 1. ctype={} pdict={}'.format(ctype, pdict))
        # parse_header bug? wants bytes for boundary not str
        pdict['boundary'] = bytes(pdict['boundary'], 'utf8')
        print('# 2. ctype={} pdict={}'.format(ctype, pdict))

        # parser does not get filename from content-disposition::
        #  Content-Disposition: form-data; name="file"; filename="CSLOGO.gif"
        # Live with it for now, we can ask for another field, `filename`.
        # lots of bug
        # complaints from 2009-2017 on this module not working.

        # With APIG Binary set, we get same Content Type but
        # isBase64Encoded=True and body is encoded.
        body = event['body']
        if event['isBase64Encoded'] is True:
            print('# b64 body={}'.format(body))
            body_bytes = b64decode(body)
        else:
            body_bytes = bytes(body, 'utf')
        print('# body_bytes={}'.format(body_bytes))
        body_fp = BytesIO(body_bytes)
        thing = parse_multipart(body_fp, pdict)
        print('# thing: {}'.format(thing))
        print('# dir(thing): {}'.format(dir(thing)))
        # Alt parsing, I get nothing:
        # with POST set headers for ctype to override default
        # ctype app/x-www-form-urlencoded
        # FieldStorage looks for LOWERCASE headers so misses our Content-Type
        # in the event['headers']; force ours to be LC.
        # Follow in the PDB: Completely fucking hopeless...
        ret = FieldStorage(fp=body_fp,
                           headers={'content-type': content_type},
                           environ={'REQUEST_METHOD': 'POST'})
        print('# Fieldstorage ret={} keys={}'.format(ret, ret.keys()))

        img = thing['file'][0]  # form could have multiples
        with open('/tmp/formdata.gif', 'wb') as img_fp:
            img_fp.write(img)
        check_output(['convert', '/tmp/formdata.gif', '/tmp/formdata.jpg'])

        ls = check_output('ls -al /tmp'.split())
        print('# ls: {}'.format(ls))

        return {'statusCode': 200,  'body': dumps(event)}

    except Exception as e:
        msg = '[599] {} {}'.format(e, format_exc())
        return {'statusCode': 599,
                'body': dumps({'message': msg})}

    # The data should have been sent with Content-Type that the APIG recognizes
    # as binary so it will base64-encode it to us. Decode and save image.

    # if event['headers']['Content-Type'] != 'image/gif':
    #     return {'statusCode': 400,
    #             'body': dumps({'message': 'Content-Type must be image/gif'})}
    # if event['isBase64Encoded'] is False:
    #     return {'statusCode': 400,
    #             'body': dumps({'message': 'APIG did not provide base64 data'})}

    # img_gif = b64decode(event['body'])
    # with open('/tmp/img.gif', 'wb') as img_fp:
    #     img_fp.write(img_gif)

    # # Do the conversion here (whatever your app needs, could be a thumbnailer)

    # check_output(['convert', '/tmp/img.gif', '/tmp/img.jpg'])

    # # To return binary, we must Base64 encode the output image and convert
    # # those bytes to UTF string for JSON body.  The request must set the header
    # # "Accept: image/jpeg" for the APIG to turn the encoded string in to binary
    # # for the client HTTP response.

    # if event['headers']['Accept'] != 'image/jpeg':
    #     return {'statusCode': 400,
    #             'body': dumps({'message': 'Accept must specify image/jpeg'})}

    # img_jpg = open('/tmp/img.jpg', 'rb').read()
    # out_b64 = b64encode(img_jpg)
    # out_str = out_b64.decode('utf8')

    # # Set status and return output as JSON string which APIG converts to binary
    # # APIG ignores the Content-Type here, only looking at client Accept header
    # # but we want to tell the final client the type.

    # return {
    #     'statusCode': 200,
    #     'body': out_str,
    #     'isBase64Encoded': True,
    #     'headers':  {'Content-Type': 'image/jpeg'},
    # }

if __name__ == '__main__':
    #event = loads(open('event-formdata.json', 'rb').read())
    event = loads(open('event-formdata.json', 'r').read())
    res = handler(event, None)
    print(res)
