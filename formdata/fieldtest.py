#!/usr/bin/env python3
# Test cgi.FieldStorage against multipart/form-data form with b64 body

from cgi import FieldStorage, parse_header, parse_multipart
from base64 import b64decode, b64encode
from io import BytesIO
from json import dumps, loads

EVENT_FILE = 'event-formdata-apigbinary-on.json'

event_bytes = open(EVENT_FILE, 'r').read()  # NOT bytes, str for json
event = loads(event_bytes)
assert event['isBase64Encoded'] is True

body_bytes = b64decode(event['body'])
# b'--------------------------ac23260d12225f00\r\nContent-Disposition: form-data; name="file"; filename="CSLOGO.gif"\r\nContent-Type: image/gif\r\n\r\nGIF87a\x1a\x00\x1a\x00\xf0\x00\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x1a\x00\x1a\x00\x00\x02U\x0c\x8e\xa9\x8b\x06\x01\xa3\x9c\xd4=\xcb\xf2\x81[\xfb\xd6m\xd5\xe7\x94\x15\xa7\x95\xe2\xc7\xa8\x17\xbb\xb8\xe8\x89\x81\xcfz\x9dq8\xd7)o\x82\xdd\x86=\x1a\x8a\x883Jx8\xd6\x0c(|\x12\x95=\xa6H\x99\x0c\t\xb3\xc3\xed\x0b\xa9\xa0J}9\x9a\x8d\xbc\rz\x1b\x16\xb1\xb9\xbbN\x04\n\x00;\r\n--------------------------ac23260d12225f00--\r\n'
body_fp = BytesIO(body_bytes)

# content_type = event['headers']['Content-Type']  # could be lowercase
# (ctype, pdict) = parse_header(content_type)
# if type(pdict['boundary']) is not bytes:
#     # fix parse_header bug: wants bytes for boundary, not str
#     pdict['boundary'] = bytes(pdict['boundary'], 'utf8')

#    form = parse_multipart(body_fp, pdict)



# No docs on call params for FieldStorage!! see:
# http://epydoc.sourceforge.net/stdlib/cgi.FieldStorage-class.html


# __init__(self, fp=None, headers=None, outerboundary=b'',
#          environ=os.environ, keep_blank_values=0, strict_parsing=0,
#          limit=None, encoding='utf-8', errors='replace'):
# fp wants TextIOWrapper, or that has read/readlines returning bytes
# headers:
# * some set from environ like CONTENT_TYPE
# * content-disposition causes it to cdisp,pdict = parse_header(...)
# * if empty, sets content-type: x-www-form-urlencoded so need to override

# outerboundary: ?from pdict?
# environ: default os.environ -- REQUEST_METHOD set POST;
#          if no headers, CONTENT_TYPE sets headers[]
# keep_blank_values: default false
# strict_parsing: false doesn't report errors
# limit: ...
# encoding, errors: handlers

# The file upload draft standard entertains the possibility of uploading
# multiple files from one field (using a recursive multipart/* encoding). When
# this occurs, the item will be a dictionary-like FieldStorage item. This can
# be determined by testing its type attribute, which should be
# multipart/form-data (or perhaps another MIME type matching multipart/*). In
# this case, it can be iterated over recursively just like the top-level form
# object.

# Downcase APIG headers so FieldStorage can find 'content-type'
# instead of defauling to x-www-form-urlencoded
headers = {k.lower(): v for k, v in event['headers'].items()}
import pdb; pdb.set_trace();
form = FieldStorage(fp=body_fp,
                    environ={'REQUEST_METHOD': event['httpMethod']},
                    headers=headers,
                    keep_blank_values=True,
                    strict_parsing=True)
assert 'file' in form  # that's what we insist it's called for now
filefield = form['file']
if not filefield.file:
    print('Does not have a "file" part, not an upload')
    exit

fn = filefield.filename
ft = filefield.type  # image/gif
ff = filefield.file  # has read() but returns b''  WTF?
fp = filefield.fp    # different addrss, read() returns b'', WTF?
#fv = filefield.value  # as string, uploads transperanetly reads file every time you request

print(fn, ft, ff, fp)
print(ff.read())
print(fp.read())
import pdb; pdb.set_trace();
