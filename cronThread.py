import db
import breakdownInfo
from threading import Thread
from datetime import datetime
import time

delay = 10 #seconds

class CronThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		
	def run(self):
		self.isRunning = True
		start = datetime.now()
		dbm = db.dbManager()
		
		while self.isRunning:
			bdi = breakdownInfo.UserBreakdownInfo()
			dbm.insert(bdi)
			#print 'inserted'
			elapsedSeconds = (datetime.now() - start).total_seconds()
			if delay > elapsedSeconds:
				time.sleep(delay - elapsedSeconds)
			
	def stop(self):
		self.isRunning = False
			
		
def main():
	ct = CronThread()
	ct.start()
	print 'started , type "stop" to stop'
	while 1:
		s = raw_input()
		if s.__contains__('stop'):
			print 'stopping...'
			ct.stop()
			ct.join()
			break
			
	
if __name__ == "__main__":
	main()