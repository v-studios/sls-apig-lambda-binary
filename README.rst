===========================================================
 Serverless API Gateway and Lamba with Binary Input/Output
===========================================================

It's not obvious from the AWS docs how to get binary data (like
images) into or out of a Lambda_ function via the `API Gateway`_. Adding
the Serverless_ framework makes this even more opaque.

After a bunch of reading, trial and error, the code and serverless
config here are a minimal example of how to do just that, using Python
for the Lambda function.

Below, we talk first about how to accept binary data, then how to
return it.

TL;DR:

* Manually set APIG Binary Support through the console for your
  content types
* Specify `Content-Type` and `Accept` headers to make APIG convert
  binary and base64 strings
* In Lambda, Decode from base64 on input, encode to base64 on output


Create and Deploy Lambda, APIG
==============================

Set your AWS_PROFILE so an AIM with plenty of privs like::

  export AWS_PROFILE=vstudios-chris-serverless

The `serverless.yml` defines the Lambda and the API Gateway, create
them::

  sls create --template aws-python3 --path binaryapi
  sls deploy -v

After function and APIG are created you can just upload the function::

  sls deploy -v function --function binaryapi

After you've invoked it once, you can tail the logs in your terminal, rather than reloading the CloudWatch logs::

  sls logs --tail --function binaryapi &

Upload Binary Payload
=====================

Send single binary payload
--------------------------

Send a binary payload (no filename=, no file=, etc)::

  curl -v --data @CSLOGO.gif $API | python -mjson.tool

The event output shows we get a truncated body, and strangely a form-encoded::

    "event": {
        "body": "GIF87a\u001a",    # <-- TRUNCATED FILE
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",

Set the data to be binary::

 curl -v --data-binary @CSLOGO.gif $API | python -mjson.tool

Our event log seems to show we get the full body but content-type is
still form-encoded. It errors out trying to log the body.

Set content type::

  curl -v -H "Content-Type: image/gif" --data-binary @CSLOGO.gif $API

Function now gets correct content type, still errors on log; comment
it. Now we get output but it shows the length of the body is wrong,
112 instead of 118.

Enable image/gif in AWS Console > APIs > my API > Binary Support.

What's it do without content-type?

  curl -v --data-binary @CSLOGO.gif $API

BodyLen is 112 so we're not getting all of it.

With binary set for `image/gif` on the API, it looks like we get
encoded binary as the body, and a larger size::

  "bodyLen": 160,
  "event": {
    "body": "R0lGODdhGgAaAPAAAAAAAP///ywAAAAAGgAaAAACVQyOqYsGAaOc1D3L8oFb+9Zt1eeUFaeV4seoF7u46ImBz3qdcTjXKW+C3YY9GoqIM0p4ONYMKHwSlT2mSJkMCbPD7QupoEp9OZqNvA16GxaxubtOBAoAOw==",
  "httpMethod": "POST",
  "isBase64Encoded": true,

Note that isBase64Encoded is True; if we decode, we get 118
chars. Looks promising.

TL;DR:

* after creating APIG, set binary for your content type
* set Content-Type on the curl request
* base64decode the body (the isBase64Encoded should be true)

TODO: Setting Filename
----------------------

Easiest way is with a form, but we seem to be having problems with
form-encoded data. Need to try some more.

We could post to a URL with like:

  /convert/{filename}

and use the filename as a clue how to process the file. Have to figure
how to spec the input mapping in serverless.yml.

Maybe easier would be to set them in a query string which we'd get
with `event['queryStringParameters']`.

Form Encoded with Filename and File Body
----------------------------------------

TBD.

I had problems parsing the form-encoded body relating to bytes vs strings.

http://forum.serverless.com/t/endpoint-for-file-upload-api-gateway-lambda-python/908/2:

  Firstly, you need to (via console only currently) in "Binary Support" add "multipart/form-data".
  This is the Content-Type used by POSTs that include files.

Returning Binary Payload
========================

Base64-encode the output body and convert those bytes to a UTF str in
the json body, and add `isBase64Encoded=true`; set the `Content-Type`
or APIG will return `application/json`::

    img_jpg = open('/tmp/img.jpg', 'rb').read()
    out_b64 = b64encode(img_jpg)
    out_str = out_b64.decode('utf8')
    return {
        'statusCode': 200,
        'body': out_str,
        'isBase64Encoded': True,
        'headers':  {'Content-Type': 'image/jpeg'},
    }

We must set the `Accept` header to get APIG to return us binary
instead of the base64 encoded data, but now we get our image::

  curl -v \
       -H "Content-Type: image/gif" \
       -H "Accept: image/jpeg" \
       --data-binary @CSLOGO.gif \
       $API2 \
       > cslogo.jpg

If we omit the `Accept`, or ask for `image/\*` or `\*/\*', we get the
base64 of the JPG, not the binary. This is not helped by adding
`image/\*` to the APIG Binary media types.

[THIS MAY NOT BE TRUE, ITS NOW FAILING AND I'VE PUT IT BACK BUT STILL
NOT GETTING CONVERSION, WAITING FOR SETTING]
For output, we don't need to set `image/jpeg`
APIG Binary media type. This seems odd given the docs on the page --
it implies it's needed to properly handle `Accept`:

  API Gateway will look at the Content-Type and Accept HTTP headers to
  decide how to handle the body.

But since we want to handle input binary for images (and PDF) we
should add it anyway (along with image/tiff, image/png, etc).




TODO
====

Add binary for image/jpeg, image/png, image/tiff, application/pdf,
application/octet-stream, multipart/form-data. Try image/\*, application/\*

What's {proxy+} do in serverless.yml?::

    events:
      - http:
          path: api/{proxy+}
          method: any

allows handler to get requests for any request below api/, the + makes
it greedy, and `proxy` is the variable assigned when it hits the
handler. Method `any` (docs say `ANY`) matches any GET, POST, etc.

What about the resource type which was either IIRC json or form-encoded? how to specify, use?

Add header processing, see d below; how do we do that in serverless.yml?

http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-payload-encodings-configure-with-console.html

This doc explains content type conversions but I don't know how to apply it to serverless.yml.
http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-payload-encodings-workflow.html



.. _`API Gateway`: https://aws.amazon.com/api-gateway/
.. _Lambda: https://aws.amazon.com/lambda/
.. _Serverless: https://serverless.com/
