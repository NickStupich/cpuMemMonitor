import breakdownInfo
import sqlite3
import cPickle as pickle
import time
from datetime import datetime

dbName = 'serverMonitor'
tableName = 'rawData'

class dbManager():
	def __init__(self):	
		self.conn = sqlite3.connect(dbName)
		self.c = self.conn.cursor()

		createSql = 'create table if not exists %s (timestamp INTEGER, data BLOB)' % tableName
		self.c.execute(createSql)
		
	def dropTable(self):
		print 'about to drop table, are you sure (y/n)?'
		s = raw_input()
		if s == 'y':
			sql = 'drop table %s' % tableName
			self.c.execute(sql)
			self.conn.commit()
			
	def insert(self, bdi):
		timestamp = time.mktime(bdi.timestamp.timetuple())
		data = pickle.dumps(bdi.data)
		sql = 'INSERT INTO %s VALUES (?,?)' % tableName
		self.c.execute(sql, (timestamp, sqlite3.Binary(data)))
		self.conn.commit()
		
	def deleteOldRecords(self, n = 4):
		#get the old timestamp to keep
		sql = 'SELECT * from %s ORDER BY timestamp desc LIMIT 1 OFFSET %d' % (tableName, n-1)
		timestamp = None
		for row in self.c.execute(sql):
			timestamp = row[0]
		
		if timestamp is not None:
			#if it IS none, then there already <n items in the db
			sql = 'DELETE from %s WHERE timestamp < %d' % (tableName, timestamp)
			self.c.execute(sql)
			self.conn.commit()
				
	def getLatest(self, n = 10):
		sql = 'SELECT * from %s ORDER BY timestamp desc LIMIT %d' % (tableName, n)
		result = self.getBdiList(self.c.execute(sql))
		return result
		
	def getBdiList(self, iterator):
		result = []
		for row in iterator:
			timestamp = breakdownInfo.timestampToDatetime(row[0])
			data = pickle.loads(str(row[1]))
			bdi = breakdownInfo.UserBreakdownInfo((data, timestamp))
			result.append(bdi)
		return result
		
	def getSince(self, timestamp):
		sql = 'SELECT * from %s WHERE timestamp > (?) ORDER BY timestamp desc' % (tableName)
		result = self.getBdiList(self.c.execute(sql, (timestamp,)))
		return result
		
def test():
	dbm = dbManager()
	dbm.dropTable()
	"""
	#dbm = dbManager()
	
	bdi = breakdownInfo.UserBreakdownInfo()
	dbm.insert(bdi)
	
	for x in dbm.getLatest(10):
		print x.userMemTotal, x.timestamp
		
	dbm.deleteOldRecords(2)
	print '\n' *5
	for x in dbm.getLatest(10):
		print x.userMemTotal, x.timestamp
	
	
	print 'total records: %d' % len(dbm.getSince(0))
	print '0 records: %d' % len(dbm.getSince(10**10))
	"""
if __name__ == "__main__":
	test()