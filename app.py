from flask import Flask, Response
from mss import mss
from os import remove
import netifaces
from gevent import monkey, pywsgi

app = Flask(__name__)

def generate():
    while True:
        with mss() as getImg:
            imgName = getImg.shot()
            with open(imgName, 'rb') as img:
                toYield = img.read()
            remove(imgName)
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + toYield + b'\r\n')

@app.route('/')
def root():
    return """
    <html>
        <body>
            <img src='/feed' style='height: 100%;width: 100%;'>
        </body>
    </html>
    """

@app.route('/feed')
def feed():
    return Response(generate(),
    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    monkey.patch_all()
    ip = (netifaces.ifaddresses(
        'wlp8s0' if 'wlp8s0' in netifaces.interfaces() else 'enp0s20u2')[
            netifaces.AF_INET
        ][0]['addr'], 8000)
    print(ip)
    pywsgi.WSGIServer(ip, app).serve_forever()