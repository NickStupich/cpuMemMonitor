import psutil
from datetime import datetime
import time

cpuScanTime = 0.1

def timestampToDatetime(timestamp):
	return datetime.fromtimestamp(timestamp)
	
def datetimetoTimestamp(dt):
	return time.mktime(dt.timetuple())

class UserBreakdownInfo():
	def __init__(self, data = None):
		self.userProcessDict = {}
		self.userMemTotal = {}
		self.userCpuTotal = {}
		
		if data is None:
			data = self.getProcessData()
		self.data, self.timestamp = data
		
		self.extractData()
		
	def getProcessData(self):	
		timestamp = datetime.now()
		processData = []
		
		for p in psutil.get_process_list():
			try:
				username = p.username
				if username.lower().__contains__("system"): username = 'SYSTEM'
			except Exception, e:
				username = 'SYSTEM'
			try:
				mem = p.get_memory_percent()
				cpu = p.get_cpu_percent(interval = cpuScanTime)
				name = p.name
				pid = p.pid
			except psutil.error.NoSuchProcess:
				#process no longer exists, just discard it
				pass
				
			processData.append((pid, name, cpu, mem, username))
			
		return processData, timestamp
		
	def extractData(self):
		self.userProcessDict = {}
		self.userMemTotal = {}
		self.userCpuTotal = {}
		
		for (pid, name, cpu, mem, username) in self.data:
			if not username in self.userProcessDict:
				self.userProcessDict[username] = []
				self.userMemTotal[username] = 0.0
				self.userCpuTotal[username] = 0.0
			
			self.userProcessDict[username].append((pid, name, mem, cpu))
			
			if name != 'System Idle Process':
				self.userMemTotal[username] += mem
				self.userCpuTotal[username] += cpu
				
		self.totalCpu = sum(self.userCpuTotal.values())
		self.totalMem = sum(self.userMemTotal.values())
			
def getNumCpus():
	return psutil.NUM_CPUS
	
def getTotalMemory():
	return psutil.virtual_memory().total
	
def getFreeMemory():
	return psutil.virtual_memory().free
			
def test():
	ubi = UserBreakdownInfo()
	
if __name__ == "__main__":
	test()
		