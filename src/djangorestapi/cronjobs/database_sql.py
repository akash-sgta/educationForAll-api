import mysql.connector as msql
import sqlite3

import os
from pathlib import Path

# ---------------------------------------------------

class Database(object):

    def __init__(self, type=None):
        super().__init__()
        
        self.conn = None

        self.database = None
        self.user = None
        self.password = None
        self.host = None
        self.port = None

        if(type == None):
            self.__type = None
        else:
            if(type.lower() == 'sqlite'):
                self.__type = 'SQLITE'
            elif(type.lower() == 'mysql'):
                self.__type = 'MYSQL'
            else:
                self.__type = None
    
    @property
    def type(self):
        return self.__type
    @type.setter
    def type(self, type):
        if(type == None):
            self.__type = None
        else:
            if(type.lower() == 'sqlite'):
                self.__type = 'SQLITE'
            elif(type.lower() == 'mysql'):
                self.__type = 'MYSQL'
            else:
                self.__type = None
    
    @property
    def data(self):
        dataDict = dict()
        if(self.database != None):
            dataDict['database'] = self.database
        if(self.user != None):
            dataDict['user'] = self.user
        if(self.password != None):
            dataDict['password'] = self.password
        if(self.host != None):
            dataDict['host'] = self.host
        if(self.port != None):
            dataDict['port'] = self.port
        
        if(len(dataDict.keys()) == 0):
            return None
        else:
            return dataDict

    @data.setter
    def data(self, dataDict):
        if(type(dataDict) != type(dict())):
            return None
        else:
            if('database' in dataDict.keys()):
                self.database = dataDict['database']
            if('user' in dataDict.keys()):
                self.user = dataDict['user']
            if('password' in dataDict.keys()):
                self.password = dataDict['password']
            if('host' in dataDict.keys()):
                self.host = dataDict['host']
            if('port' in dataDict.keys()):
                self.port = dataDict['port']
            return True
    
    def connect_sqlite(self):
        try:
            self.conn = sqlite3.connect(self.database)
        except Exception as ex:
            print(f"[x] {ex}")
            return None
        else:
            return self.conn
    
    def connect_mysql(self):
        try:
            self.conn = msql.connect(
                            host = self.host,
                            user = self.user,
                            password = self.password,
                            database = self.database,
                            port = self.port
                        )
        except Exception as ex:
            print(f"[x] {ex}")
            return None
        else:
            return self.conn
    
    def connect(self):
        if(self.type == 'MYSQL'):
            return self.connect_mysql()
        elif(self.type == 'SQLITE'):
            return self.connect_sqlite()
        else:
            return None

    def commit(self):
        if(self.conn != None):
            self.conn.commit()
            return True
        else:
            return None

    def disconnect(self):
        if(self.conn != None):
            self.conn.close()
        self.conn = None
        return True

    def generate_cursor(self):
        if(self.conn != None):
            self.cursor = self.conn.cursor()
            return self.cursor
        else:
            return None
    
    def select_sql(self, appName=None, tableName=None, columnName=None, condition=None):
        if(tableName != None and columnName != None):
            query = f'''SELECT {",".join(columnName)} FROM {appName.lower()}_{tableName.lower()} '''
            if(condition != None):
                query += f'''WHERE {condition} '''
            query += f'''ORDER BY {",".join(columnName)};'''
            query = query.strip()
            cursor = None
            try:
                cursor = self.conn.cursor()
                cursor.execute(query)
            except Exception as ex:
                print(f"[x] {ex}")
                data = None
            else:
                data = cursor.fetchall()
        else:
            data = None

        return data

    def update_sql(self, appName=None, tableName=None, columnChanges=None, condition=None):
        if(tableName != None and columnChanges != None):
            query = f'''UPDATE {appName}_{tableName} SET {columnChanges} '''
            if(condition != None):
                query += f'''WHERE {condition}'''
            query += ';'
            query = query.strip()
            cursor = None
            try:
                cursor = self.conn.cursor()
                cursor.execute(query)
            except Exception as ex:
                print(f"[x] {ex}")
                data = None
            else:
                data = cursor.fetchall()
        else:
            data = None

        return data
    
    def delete_sql(self, appName=None, tableName=None, condition=None):
        if(tableName != None and condition != None):
            query = f'''DELETE FROM {appName}_{tableName} '''
            if(condition != None):
                query += f'''WHERE {condition}'''
            query += ';'
            query = query.strip()
            cursor = None
            try:
                cursor = self.conn.cursor()
                cursor.execute(query)
            except Exception as ex:
                print(f"[x] {ex}")
                data = None
            else:
                data = cursor.fetchall()
        else:
            data = None

        return data

def main():
    BASE = Path(__file__).resolve().parent.parent
    
    with open(os.path.join(BASE, 'config', 'debug.txt'), 'r') as debug_status:
        DEBUG = debug_status.read()[1:-1]
        if(DEBUG == 'True'):
            DEBUG = True
        else:
            DEBUG = False

    if(DEBUG):
        db = Database('sqlite')
        db.data = {
            "database" : os.path.join(BASE, 'test_databases', 'app.db.sqlite3')
        }
    else:
        db = Database('mysql')
        db.data = {
            'database':  "appDB",
            'user': "admin",
            'password': "GANDUgandu",
            'host': "projectdatabase1.czbsimzcrcxe.ap-south-1.rds.amazonaws.com",
            'port' : "6969"
        }
    
    db.connect()
    db.generate_cursor()
    
    data = db.select_sql(
        appName = 'auth_prime',
        tableName = 'user_token_table',
        columnName = ['token_hash', 'token_start', 'user_credential_id_id'])
    print(data)


# main()