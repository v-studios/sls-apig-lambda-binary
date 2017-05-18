=================
 XFORMURLENCODED
=================

Deploy the first time::

  export AWS_PROFILE=vstudios-chris-serverless
  time sls deploy -v

Throw an image at it and capture the event::

  curl -v -H "Accept: image/jpeg" --data-urlencode FILENAME=CSLOGO --data-urlencode FILE@../CSLOGO.gif $XFORM|python -mjson.tool

  "body": "FILENAME=CSLOGO&FILE=GIF87a%1A%00%1A%00%F0%00%00%00%00%00%FF%FF%FF%2C%00%00%00%00%1A%00%1A%00%00%02U%0C%8E%A9%8B%06%01%A3%9C%D4%3D%CB%F2%81%5B%FB%D6m%D5%E7%94%15%A7%95%E2%C7%A8%17%BB%B8%E8%89%81%CFz%9Dq8%D7%29o%82%DD%86%3D%1A%8A%883Jx8%D6%0C%28%7C%12%95%3D%A6H%99%0C%09%B3%C3%ED%0B%A9%A0J%7D9%9A%8D%BC%0Dz%1B%16%B1%B9%BBN%04%0A%00%3B",
  "isBase64Encoded": false,

Note that we get a URL-encoded version of the binary file, and `isBase64Encoded` is False.

Don't do this: without the URLencode we get truncated data; note the
name of the field is not present with this curl variation::

  curl -v -H "Accept: image/jpeg" --data FILENAME=CSLOGO --data @../CSLOGO.gif $XFORM

  "body": "FILENAME=CSLOGO&GIF87a\u001a",

