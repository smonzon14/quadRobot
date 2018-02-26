from socketserver import ThreadingMixIn
from threading import Thread
from io import BytesIO
from PIL import Image
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from stream import WebcamVideoStream

vs = WebcamVideoStream().start()
img = vs.read()
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    global img, port

                    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = BytesIO()
                    jpg.save(tmpFile, 'JPEG')
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(tmpFile.getbuffer().nbytes))
                    self.end_headers()
                    # print(jpg)
                    self.wfile.write(tmpFile.getvalue())

                    # jpg.save(self.wfile, 'JPEG')
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode())
            self.wfile.write(
                ('<img src="http:// ' + self.client_address[0] + ':' + str(port) + '/cam.mjpg"/>').encode())
            self.wfile.write('</body></html>'.encode())
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def serve():
    server = ThreadedHTTPServer(("", port), CamHandler)
    server.serve_forever()


server_thread = Thread(target=serve, args=())
server_thread.start()

print("mjpeg server started on port " + str(port))
while(1):
    img = vs.read()