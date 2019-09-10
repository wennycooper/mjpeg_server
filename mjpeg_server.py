# -*- coding: utf-8 -*-

#MJPEG Server for the video file

import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import cv2
import re
import sys
# import imutils
import numpy as np
import socket


if len(sys.argv) < 2 :
    print "Usage : webcamserver <quality> <port>"
    cameraQuality = 100
    port = 8080
else:
    cameraQuality = sys.argv[1]
    port = int(sys.argv[2])

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global cameraQuality
        try:
            self.path=re.sub('[^.a-zA-Z0-9]', "",str(self.path))
            if self.path=="" or self.path==None or self.path[:1]==".":
                self.send_response(200)
                self.end_headers()
                message =  threading.currentThread().getName()
                self.wfile.write(message)
                self.wfile.write('\n')
                return
            if self.path.endswith(".html"):
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            if self.path.endswith(".mjpeg"):
                capture = cv2.VideoCapture('sample_video.mp4')
                self.send_response(200)
                self.wfile.write("Content-Type: multipart/x-mixed-replace; boundary=--aaboundary")
                self.wfile.write("\r\n\r\n")
                while 1:
                    ret, img1 = capture.read()

                    cv2mat1 = cv2.imencode(".jpeg", img1, (cv2.IMWRITE_JPEG_QUALITY, cameraQuality))[1]
                    data_encode = np.array(cv2mat1)
                    JpegData1 = data_encode.tostring()

                    self.wfile.write("--aaboundary\r\n")
                    self.wfile.write("Content-Type: image/jpeg\r\n")
                    self.wfile.write("Content-length: "+str(len(JpegData1))+"\r\n\r\n" )
                    self.wfile.write(JpegData1)
                    self.wfile.write("\r\n\r\n\r\n")
                    time.sleep(0.02)
                return
            if self.path.endswith(".jpeg"):
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type','image/jpeg')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            return
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
    def do_POST(self):
        global rootnode, cameraQuality
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            self.send_response(301)

            self.end_headers()
            upfilecontent = query.get('upfile')
            print "filecontent", upfilecontent[0]
            value=int(upfilecontent[0])
            cameraQuality=max(2, min(99, value))
            self.wfile.write("<HTML>POST OK. Camera Set to<BR><BR>");
            self.wfile.write(str(cameraQuality));

        except :
            pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#class ThreadedHTTPServer(HTTPServer):
    """Handle requests in a separate thread."""


def main():
    while 1:
        try:
            server = ThreadedHTTPServer(('0.0.0.0', port), MyHandler)
            print 'Starting httpServer...'
            print 'See <Local IP>:'+ str(port) + '/1.mjpeg'
            server.serve_forever()
        except KeyboardInterrupt:
            print '^C received, shutting down server'
            server.socket.close()
            return

if __name__ == '__main__':
    main()
