import breakdownInfo
import db
import time
from datetime import datetime, timedelta

class DataService():
	def __init__(self):
		self.dbm = db.dbManager()

	def getUserBreakdownDataString(self):
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
		
		return {	'dataMem' : dataMem, 
					'dataCpu' : dataCpu, 
					'time' : str(bdi.timestamp), 
					'navHeader' : open('html/navHeader.html').read(),
				}
		
	def getTotalHistoryDataString(self, minTimestamp = None, hours = 1):
		if minTimestamp is None:
			minTimestamp = time.mktime((datetime.now() - timedelta(hours=hours)).timetuple())
			
		bdis = self.dbm.getSince(minTimestamp)
		dataMem = '['
		
		uniqueUsers = []
		for bdi in bdis:
			for user in bdi.userProcessDict:
				if not user in uniqueUsers:
					uniqueUsers.append(user)
		
		for user in uniqueUsers:
			userMem = '['
			for bdi in bdis:
				userMem += '[%d, %f],' % (breakdownInfo.datetimetoTimestamp(bdi.timestamp),
											bdi.userMemTotal[user] if bdi.userMemTotal.has_key(user) else 0.0)
			userMem += ']'
			
			dataMem += userMem + ',\n'
			
		userMem = '['
		for bdi in bdis:
			userMem += '[%d, %f],' % (breakdownInfo.datetimetoTimestamp(bdi.timestamp), bdi.totalMem)
		userMem += ']'
		dataMem += userMem + ',\n'
			
		dataMem += ']'
		
		dataCpu = '['
		for user in uniqueUsers:
			userCpu = '['
			for bdi in bdis:
				userCpu += '[%d, %f],' % (breakdownInfo.datetimetoTimestamp(bdi.timestamp),
											bdi.userCpuTotal[user] if bdi.userCpuTotal.has_key(user) else 0.0)
			userCpu += ']'
			
			dataCpu += userCpu + ',\n'
			
		userCpu = '['
		for bdi in bdis:
			userCpu += '[%d, %f],' % (breakdownInfo.datetimetoTimestamp(bdi.timestamp), bdi.totalCpu)
		userCpu += ']'
		dataCpu += userCpu + ',\n'
			
		dataCpu += ']'
			
		uniqueUsers.append('Total (shadow)')
		labels = '[' + ','.join(['"' + user + '"' for user in uniqueUsers]) + ']'
		
		return {	'labels' : labels, 
					'dataMem' : dataMem, 
					'dataCpu' : dataCpu, 
					'blankDictLabelsMinusOne' : '{},' * (len(uniqueUsers)-1), 
					'navHeader' : open('html/navHeader.html').read(),
				}