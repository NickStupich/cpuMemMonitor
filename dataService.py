import breakdownInfo
import db
import time
from datetime import datetime, timedelta
import json

OTHER_KEY = "OTHER"
TOTAL_KEY = "TOTAL (Shadow)"

def datetimeToJs(dt):
	return dt.strftime('%m-%d %I:%M:%S%p')
	
class DataService():
	def __init__(self):
		self.dbm = db.dbManager()

	def getUserBreakdownDataString(self):
		content = open('html/userBreakdown.html').read()
		
		bdi = self.dbm.getLatest(n=1)[0]
		totalMem = 0.0
		dataMem = '['
		for user in bdi.userMemTotal:
			dataMem += "['%s', %f]," % (user, bdi.userMemTotal[user])
			totalMem += bdi.userMemTotal[user]
		dataMem += "['free', %f]" % (100.0 * breakdownInfo.getFreeMemory() / breakdownInfo.getTotalMemory())
		dataMem += ']'
		
		totalCpu = 0.0
		dataCpu = '['
		for user in bdi.userCpuTotal:
			dataCpu += "['%s', %f]," % (user, bdi.userCpuTotal[user])
			totalCpu += bdi.userCpuTotal[user]
		dataCpu += "['free', %f]" % (100 * breakdownInfo.getNumCpus() - totalCpu)
		dataCpu += ']'
		
		contentDict = {	'dataMem' : dataMem, 
					'dataCpu' : dataCpu, 
					'time' : str(bdi.timestamp), 
					'navHeader' : open('html/navHeader.html').read(),
				}
				
		result = content % contentDict
		return result
		
	def getUniqueKeys(self, data, numKeys = 5):
		uniqueKeys = []
		for d in data:
			for key in d:
				if not key in uniqueKeys:
					uniqueKeys.append(key)
						
		if len(uniqueKeys) > numKeys and numKeys > 0:
			keyTotals = dict([(key, 0.0) for key in uniqueKeys])
			for d in data:
				for key in d:
					keyTotals[key] += d[key]
					
			sortedKeys = sorted(keyTotals.items(), key = lambda x: x[1], reverse = True)
			uniqueKeys = map(lambda x: x[0], sortedKeys[:numKeys]) + [OTHER_KEY]
			
		return [TOTAL_KEY] + uniqueKeys
		
	def getUserLinksContent(self, bdis):
		uniqueUsers = self.getUniqueKeys(map(lambda x: x.userMemTotal, bdis))[1:]	#ignore the total key
		userLink = '<div><a href="/userHistory.html?user=%(username)s">%(username)s</a></div>'
		resultList = [userLink % {'username' : username} for username in uniqueUsers]
		header = '<div><h2>Individual users breakdown</h2></div>'
		result = '\n'.join([header] + resultList)
		return result
		
	def getDataList(self, data, timestamps, uniqueKeys):
		result = []
		for key in uniqueKeys:
			subResult = []
			for dataPt, timestamp in zip(data, timestamps):
				if key == TOTAL_KEY:
					subResult.append((datetimeToJs(timestamp), sum(dataPt.values())))
				elif key == OTHER_KEY:
					subResult.append((datetimeToJs(timestamp), sum([v for k, v in dataPt.items() if (not k in uniqueKeys)])))
				else:
					subResult.append((datetimeToJs(timestamp), dataPt.get(key, 0)))
			
			result.append(subResult)
		return result
		
	def getTotalHistoryDataString(self, hours = 1, numUsers = 5):
		minTimestamp = time.mktime((datetime.now() - timedelta(hours=hours)).timetuple())
			
		bdis = self.dbm.getSince(minTimestamp)
		
		if len(bdis) == 0:
			return """<html><body>No data to display</body></html>"""
		
		timestamps = map(lambda x: x.timestamp, bdis)
		userMemTotals = map(lambda x: x.userMemTotal, bdis)
		userCpuTotals = map(lambda x: x.userCpuTotal, bdis)
		userLinks = self.getUserLinksContent(bdis)
		return self.getTimeGraph(userMemTotals, userCpuTotals, timestamps, userLinks, numUsers)
		
	def getTimeGraph(self, memTotals, cpuTotals, timestamps, userLinks, numKeys):
		
		uniqueKeys = self.getUniqueKeys(memTotals, numKeys)	#unique keys will be sorted by memory
		
		dataMem = self.getDataList(memTotals, timestamps, uniqueKeys)
		dataCpu = self.getDataList(cpuTotals, timestamps, uniqueKeys)
		
		graphsContent = open('html/timeGraphs.html').read()
		graphsDict = {	'labels' : json.dumps(uniqueKeys, indent = 3), 
						'dataMem' : json.dumps(dataMem, indent = 3), 
						'dataCpu' : json.dumps(dataCpu, indent = 3), 
						'blankDictLabelsMinusOne' : '{},' * (len(uniqueKeys)-1), 					
						'minTime' : datetimeToJs(timestamps[-1]),
						'maxTime' : datetimeToJs(timestamps[0]),
						'maxCpu' : breakdownInfo.getNumCpus() * 100,
					}
		graphsResult = graphsContent % graphsDict
				
		contentDict = {	'navHeader' : open('html/navHeader.html').read(),
						'timeGraphs' : graphsResult,
						'usersLink' : userLinks,
					}
					
		content = open('html/totalHistory.html').read()
		result = content % contentDict
		
		return result
		
	def getUserHistoryDataString(self, user, hours = 1, processesToShow = 5):
		minTimestamp = time.mktime((datetime.now() - timedelta(hours=hours)).timetuple())
			
		bdis = self.dbm.getSince(minTimestamp)
		if user is None:
			return self.getUserLinksContent(bdis)

		userLinks = self.getUserLinksContent(bdis)
		timestamps = map(lambda x: x.timestamp, bdis)
		
		userInfo = map(lambda x: x.userProcessDict[user], bdis)
		
		userMemTotals = []
		userCpuTotals = []
		for xi in userInfo:
			dMem = {}
			dCpu = {}
			for y in xi:
				if not dMem.has_key(y[1]):
					dMem[y[1]] = 0.0
					dCpu[y[1]] = 0.0
					
				dMem[y[1]] += y[2]
				dCpu[y[1]] += y[3]
				
			userMemTotals.append(dMem)
			userCpuTotals.append(dCpu)
		
		return self.getTimeGraph(userMemTotals, userCpuTotals, timestamps, userLinks, processesToShow)
		
		