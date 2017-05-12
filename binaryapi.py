from base64 import b64decode, b64encode
import json
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.setLevel(logging.INFO)

log.info('Outside of handler')

# I'm gonna expect to be called with only a data payload, e.g.,
# curl -v --binary-data @CSLOGO.gif $API


def run(cmd):
    """Run a command as a subprocess, log output or errors."""
    log.info('RUN {}'.format(cmd))
    if type(cmd) is str:
        cmd = cmd.split()
    try:
        log.info('RAN {}: {}'.format(cmd, subprocess.check_output(cmd)))
    except subprocess.CalledProcessError as e:
        log.error('RAN {}: {}'.format(cmd, e))
        raise


def handler(event, context):
    log.info('API Event: {}'.format(json.dumps(event)))
    body = event['body']
    log.info('API isBase64Encoded={}'.format(event['isBase64Encoded']))
    log.info('body type={}'.format(type(body)))
    # log.info('body:\n{}'.format(body))
    log.info('body len: {}'.format(len(body)))
    log.info('content-type: {}'.format(event['headers']['Content-Type']))

    log.info('b64decoding...')
    img = b64decode(body)
    log.info('writing /tmp/img.gif...')
    with open('/tmp/img.gif', 'wb') as img_fp:
        img_fp.write(img)
    run('ls -l /tmp')
    log.info('converting...')
    run('convert /tmp/img.gif /tmp/img.jpg')
    run('ls -l /tmp')

    # Base64 encode the binary and convert those bytes to UTF string for JSON body
    # The request must set the header "Accept: image/jpeg" for the APIG to turn
    # the byte string in to binary, and the Binary 
    log.info('reading output JPG and b64 encodeing...')
    img_jpg = open('/tmp/img.jpg', 'rb').read()
    out_b64 = b64encode(img_jpg)
    out_str = out_b64.decode('utf8')
    log.info('out_str: {}'.format(out_str))

    # Lamda proxy specifies: statusCode, isBase64Encoded, body, headers
    return {
        'statusCode': 200,
        'body': out_str,
        'isBase64Encoded': True,
        'headers':  {'Content-Type': 'image/jpeg'},
    }
    # # Code for default http lambda-proxy integration
    # out = {
    #     "message": "OK",
    #     "bodyLen": len(body),
    #     "event": event
    # }
    # return {
    #     "statusCode": 200,
    #     "body": json.dumps(out)
    # }

    # Use this if you don't use the http event with LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
