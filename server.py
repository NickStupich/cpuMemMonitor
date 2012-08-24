import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cronThread
import dataService
from urlparse import parse_qs
import re
import sys
import platform

ds = dataService.DataService()

class MyHandler(BaseHTTPRequestHandler):
		
	def do_GET(self):
		queryParams = re.sub('.*\?', '', self.path)
		paramsDict = parse_qs(queryParams) if queryParams else {}
		baseUrl = re.sub('\?.*', '', self.path)
		
		pageContent = None
	
		if baseUrl.endswith('.html'):
			numLines = 5
			if paramsDict.has_key('numLines'):
				numLines = int(paramsDict['numLines'][0])
			topPage = baseUrl.strip('.html').strip('/').split('/')[0]
			if topPage == 'userBreakdown':
				content = ds.getUserBreakdownDataString()
				pageContent = content
			elif topPage == 'totalHistory':				
				hours = 1
				paramsDict = parse_qs(queryParams)
				if paramsDict.has_key('hours'):
					hours = float(paramsDict['hours'][0])
				
				content = ds.getTotalHistoryDataString(hours, numLines)
				pageContent = content
				
			elif topPage == 'userHistory':
				user = paramsDict.get('user')
				user = user[0] if user else None
				hours = 1
				if paramsDict.has_key('hours'):
					hours = float(paramsDict['hours'][0])
					
				pageContent = ds.getUserHistoryDataString(user, hours, numLines)
					
				
		if self.path.endswith('.js'):
			self.send_response(200)
			self.send_header('Content-type',	'text/javascript')
			self.end_headers()
			
			content = open('js/' + self.path).read()
			self.wfile.write(content)
			
		if self.path.endswith('.css'):
			self.send_response(200)
			self.send_header('Content-type',	'text/css')
			self.end_headers()
			
			content = open('css/' + self.path).read()
			self.wfile.write(content)
			
		if baseUrl.endswith('.html'):
			self.send_response(200)
			self.send_header('Content-type',	'text/html')
			self.end_headers()
			
			self.wfile.write(pageContent)
			
		return
     
	def redirectTo(self, url, timeout = 0):
		self.wfile.write("""<html><head>
			<meta HTTP-EQUIV="REFRESH"
			content="%i; url=%s"/></head>""" % (timeout, url))

	def do_POST(self):
		pass

def main():
	if '64' in platform.machine() and (not '64' in sys.version):
		print 'This MUST be run in 64 bit python for a 64 bit machine - otherwise applications with >2GB memory dont work properly'
		exit(1)
		
	try:
		ct = cronThread.CronThread()
		ct.start()
		server = HTTPServer(('', 80), MyHandler)
		print 'started httpserver...'
		server.serve_forever()
	except KeyboardInterrupt:
		print '^C received, shutting down server, this may take many seconds'
		server.socket.close()
		ct.stop()

if __name__ == '__main__':
    main()

