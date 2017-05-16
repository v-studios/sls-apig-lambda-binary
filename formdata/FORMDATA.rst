==========
 FORMDATA
==========


Per W3:

  https://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.1

  The content type "application/x-www-form-urlencoded" is inefficient
  for sending large quantities of binary data or text containing
  non-ASCII characters.

  The content type "multipart/form-data" should be used for submitting
  forms that contain files, non-ASCII data, and binary data.

Curl's -F is said to do multipart/form-data so lets start there::

  curl -v -F file=@../CSLOGO.gif $FORMDATA | python -mjson.tool

I have to set APIG Binary Support for `multipart/form-data` to get the
binary safely.

Then I can parse the form with Python-3's `CGI` libraray (which seems
buggy), and grab the file as a base64-encoded object. After decoding I
can save to disk and convert to JPG.

Then I can return read the JPG, base64-encode, and return this from
Lambda to APIG. I have to set APIG Binary for `image/jpeg`, and set
the header `Accept` to `image/jpeg` to get APIG to convert the b64 to
binary for the client.

  curl -v -H "Accept: image/jpeg" -F FILENAME=TESTME.gif -F file=@../CSLOGO.gif $API > out.jpg

I have found adding the Binary Support to be unreliable: sometimes the
changes "stick", other ties it acts like nothing happened. I believe
simply adding the media types doesn't affect the deployed APIG
themselves, so you need to redeploy them. You can either do it with
the CLI::

  sls deploy

Or on the AWS console, APIGI, chose your gateway, then Resources,
Actions -> Deploy API.

Note that you CAN set wildcards on the APIG Binary Support, just
remember to redeploy. For this app, I've replaced my image/jpeg with
`image/*` and verified output works as expected.

One day maybe AWS CloudFormation will learn about Binary Support so
that the Serverless Framework team can add this to the serverless.yml
file.
