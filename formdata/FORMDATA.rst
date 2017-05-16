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

The event body is a form with embedded binary, base64Encoded=False,
and form proper content-type::

  {
      "body": "--------------------------dc53a7a19017bf09\r\nContent-Disposition: form-data; name=\"file\"; filename=\"CSLOGO.gif\"\r\nContent-Type: image/gif\r\n\r\nGIF87a\u001a\u0000\u001a\u0000\ufffd\u0000\u0000\u0000\u0000\u0000\ufffd\ufffd\ufffd,\u0000\u0000\u0000\u0000\u001a\u0000\u001a\u0000\u0000\u0002U\f\ufffd\ufffd\ufffd\u0006\u0001\ufffd\ufffd\ufffd=\ufffd\ufffd[\ufffd\ufffdm\ufffd\ufffd\u0015\ufffd\ufffd\ufffd\u01e8\u0017\ufffd\ufffd\u8241\ufffdz\ufffdq8\ufffd)o\ufffd\u0746=\u001a\ufffd\ufffd3Jx8\ufffd\f(|\u0012\ufffd=\ufffdH\ufffd\f\t\ufffd\ufffd\ufffd\u000b\ufffd\ufffdJ}9\ufffd\ufffd\ufffd\rz\u001b\u0016\ufffd\ufffd\ufffdN\u0004\n\u0000;\r\n--------------------------dc53a7a19017bf09--\r\n",
      "headers": {
          "Content-Type": "multipart/form-data; boundary=------------------------dc53a7a19017bf09",
      },
      "isBase64Encoded": false,

The body, after newline expansion, is::

  "--------------------------dc53a7a19017bf09
  Content-Disposition: form-data; name=\"file\"; filename=\"CSLOGO.gif\"
  Content-Type: image/gif

  GIF87a\u001a...\n\u0000;
  --------------------------dc53a7a19017bf09--

I'm struggling with what appears to be a very buggy CGI module parsing
the form.  After hacking it to extract the incoming image and saving
it to disk, we see it's mangled; is it CGI or is it lack of binary in APIG?


