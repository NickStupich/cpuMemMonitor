import breakdownInfo
import db
import time
from datetime import datetime, timedelta

def datetimeToJs(dt):
	return dt.strftime('%m-%d %I:%M%p')
	
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
		
	def dictListToString(self, dataList, timestamps, uniqueKeys = None, doTotal = True):
		if uniqueKeys is None:
			uniqueKeys = []
			for d in dataList:
				for key in d:
					if not key in uniqueKeys:
						uniqueKeys.append(key)
						
		result = '['
		
		if doTotal:
			subResult = '['
			for dataPt, timestamp in zip(dataList, timestamps):
				subResult += "['%s', %f]," % (datetimeToJs(timestamp), sum(dataPt.values()))
			subResult += ']'
			result += subResult + ',\n'
			
		for key in uniqueKeys:
			
			subResult = '['
			for dataPt, timestamp in zip(dataList, timestamps):		
				subResult += "['%s', %f]," % (datetimeToJs(timestamp), dataPt[key] if dataPt.has_key(key) else 0.0)
			subResult += ']'
			
			result += subResult + ',\n'
		result += ']'
		
		if doTotal:
			uniqueKeys.insert(0, 'Total (Shadow)')
		
		return result, uniqueKeys
		
	def getTotalHistoryDataString(self, minTimestamp = None, hours = 1):
		if minTimestamp is None:
			minTimestamp = time.mktime((datetime.now() - timedelta(hours=hours)).timetuple())
			
		bdis = self.dbm.getSince(minTimestamp)
		
		timestamps = map(lambda x: x.timestamp, bdis)
		userMemTotals = map(lambda x: x.userMemTotal, bdis)
		userCpuTotals = map(lambda x: x.userCpuTotal, bdis)
		dataMem, uniqueUsers = self.dictListToString(userMemTotals, timestamps)
		dataCpu, uniqueUsers = self.dictListToString(userCpuTotals, timestamps)
		
		labels = '[' + ','.join(['"' + user + '"' for user in uniqueUsers]) + ']'
		
		graphsContent = open('html/timeGraphs.html').read()
		graphsDict = {	'labels' : labels, 
						'dataMem' : dataMem, 
						'dataCpu' : dataCpu, 
						'blankDictLabelsMinusOne' : '{},' * (len(uniqueUsers)-1), 					
						'minTime' : datetimeToJs(bdis[-1].timestamp),
						'maxTime' : datetimeToJs(bdis[0].timestamp)
					}
		graphsResult = graphsContent % graphsDict
				
		contentDict = {	'navHeader' : open('html/navHeader.html').read(),
						'timeGraphs' : graphsResult
					}
					
		content = open('html/totalHistory.html').read()
		print content
		result = content % contentDict
		
		return result
		
	def getUserHistoryDataString(user):
		return None