from typing import Callable, Iterable
import os
import csv

#custom modules
import date_string as Date
import database_connectable as DbConnectable
import csv_dbinitialization
import safe_query as SafeQuerying



class DbInterface(DbConnectable.Connectable):
    '''
    interface to communicate with SQL database via callable functions
    if passed database given does not exist it will be created empty
    '''
    #all functions are prefixed with db to avoid naming collisions, so db_ is
    #added to function calls
    COMMAND_PREFIX = "db_"

    def __init__(self, host: str, user: str, password: str, databaseName: str) -> None:
        super().__init__(host, user, password, databaseName)
    
    def __outputBool(boolValue: bool) -> None:
        '''
        prints output of SQL command assuming the value is a bool
        '''
        print( "Success" if boolValue else "Fail" )

    def __outputTable(rawTable: Iterable) -> None:
        '''
        prints output of SQL command assuming the value is a table
        '''
        for row in rawTable:
            outputRow = str(row)[1:-1]
            outputRow.replace("'NULL'", "NULL")
            print(outputRow)


    def getFunction(self, functionName : str) -> Callable | None:
        '''
        returns DbInterface function if present, else returns None
        '''
        classFunction: callable | None = getattr(
            DbInterface, 
            DbInterface.COMMAND_PREFIX + functionName, None
            )
        if (callable(classFunction)):
            return classFunction
        return None
    


    def csvinput_normalized(rawCsvRow: str) -> csv:
        '''
        takes a SQL response row and converts it to printable output
        '''
        insertRow = '(' + str(rawCsvRow)[1:-1] + ')'
        insertRow.replace("'NULL'", "NULL")
        return(insertRow)
    


    
    def csvToTable(self, filePath: str) -> None:
        '''
        takes a filepath and converts the csv file at that path to a table
        in the instances connected database
        '''
        tableAlias: str = os.path.split(filePath)[1][:-4]

        with open(filePath, mode='r') as csvFile:
            tableData = csv.reader(csvFile)
            for row in tableData:
                self.dbCursor.execute(
                    f'INSERT INTO {csv_dbinitialization.ALIAS_TABLE_MAP[tableAlias].tableName}\
                        VALUES {DbInterface.csvinput_normalized(row)};'
                )
            self.dbConnetion.commit()

    def drop_tables(self) -> None:
        '''
        deletes all project schema's tables from the instances connected 
        database
        '''
        for alias in reversed(csv_dbinitialization.TABLE_CREATE_ORDER):
            self.dbCursor.execute(f'DROP TABLE IF EXISTS \
                        {csv_dbinitialization.ALIAS_TABLE_MAP[alias].tableName};')
        self.dbConnetion.commit()

    def initializeTables(self) -> None:
        '''
        creates all the tables in the project schema in the instances connected
        database
        '''
        for alias in csv_dbinitialization.TABLE_CREATE_ORDER:
            self.dbCursor.execute(\
                csv_dbinitialization.ALIAS_TABLE_MAP[alias].initCommand)
            self.dbConnetion.commit()
    
    def fill_tables(self, folderPath: str) -> None:
        '''
        given a path to a folder containing csv data for project schema tables,
        fills schema tables with data from corresponding files
        '''
        presentFiles = os.listdir(folderPath)
        for alias in csv_dbinitialization.TABLE_CREATE_ORDER:
            workingFile = alias + '.csv'
            if (workingFile not in presentFiles):
                raise ValueError(f"could not find {workingFile} in {folderPath}")
            self.csvToTable(os.path.join(folderPath, workingFile))
            self.dbConnetion.commit()

    def db_tableSize(self, tableName: str) -> int:
        '''
        gives a table name returns the size of that table
        '''
        self.dbCursor.execute(f'SELECT COUNT(*) AS count FROM {tableName}')
        return self.dbCursor.fetchone()[0]
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~PROJECT REQUIRED FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~

    def db_import(self, folderPath: str) -> None:
        #project required
        '''
        Delete existing tables, and create new tables. Then read the csv files 
        in the given folder and import data into database. You can assume that 
        the folder always contains all the necessary CSV files and the files are 
        correct.

        Table - Number of users,Number of machine, Number of Course
        '''
        self.drop_tables()
        self.initializeTables()
        self.fill_tables(folderPath)
                
        
        numUsers = self.db_tableSize('Users')
        numMachines = self.db_tableSize('Machines')
        numCourses = self.db_tableSize('Courses')
        
        DbInterface.__outputTable([[numUsers, numMachines, numCourses]])
    

    def executeMultipleQueryCommand(self, safeQueryList: list, commit: bool) -> bool:
        try:
            SafeQuerying.SafeQuery.executeMultiple(safeQueryList, self.dbCursor)
            if (commit):
                self.dbConnetion.commit()
        except Exception as err:
            if (err.__class__.__module__ == DbConnectable.SqlErrorModuleName):
                # print(err)
                return False
            else:
                raise err
        return True
    
    def executeSingleQueryCommand(self, query: str, commit: bool) -> bool:
        try:
            self.dbCursor.execute(query)
            if (commit):
                self.dbConnetion.commit()
        except Exception as err:
            if (err.__class__.__module__ == DbConnectable.SqlErrorModuleName):
                # print(err)
                return False
            else:
                raise err
        return True


    #TODO: finish all assignment functions and add project requirements as comments
    def db_insertStudent(self, UCINetID: str, email: str, First: str, Middle: str, Last: str, commit=True) -> None:
        '''
        Insert a new student into the related tables.

        Bool
        '''
        insertQueries = [
            SafeQuerying.SafeQuery(
                f"INSERT INTO Users\
                    VALUES ('{UCINetID}', '{First}', '{Middle}', '{Last}');", 
                f"DELETE FROM Users\
                    WHERE UCINetID = '{UCINetID}';"),
            SafeQuerying.SafeQuery(
                f"INSERT INTO UserEmail\
                    VALUES ('{UCINetID}', '{email}');", 
                f"DELETE FROM UserEmail\
                    WHERE UCINetID = '{UCINetID}';"),
            SafeQuerying.SafeQuery(
                f"INSERT INTO Students\
                    VALUES('{UCINetID}');", 
                f"DELETE FROM students\
                    WHERE UCINetID = '{UCINetID}';")
        ]
        querySuccess = self.executeMultipleQueryCommand(insertQueries, commit)
        DbInterface.__outputBool(querySuccess)
    
    def db_addEmail(self, UCINetID: str, email: str, commit=True) -> None:
        '''
        Add email to a user
        '''
        query = f"INSERT INTO UserEmail\
                    VALUES('{UCINetID}', '{email}')"
        querySuccess = self.executeSingleQueryCommand(query, commit)
        DbInterface.__outputBool(querySuccess)
        
    def db_deleteStudent(self, UCINetID: str, email: str, commit=True) -> None:
        #DBInterface.__outputBool()
        pass
    def db_insertMachine(self, UCINetID: str, email: str, commit=True) -> None:
        #DBInterface.__outputBool()
        pass
    def db_insertUse(self, UCINetID: str, email: str, commit=True) -> None:
        #DBInterface.__outputBool()
        pass
    def db_updateCourse(self, UCINetID: str, email: str, commit=True) -> None:
        #DBInterface.__outputBool()
        pass
    def db_listCourse(self, UCINetID: str, email: str) -> None:
        #DBInterface.__outputTable()
        pass
    def db_popularCourse(self, UCINetID: str, email: str) -> None:
        #DBInterface.__outputTable()
        pass
    def db_adminEmails(self, UCINetID: str, email: str) -> None:
        #DBInterface.__outputTable()
        pass
    def db_activeStudent(self, UCINetID: str, email: str) -> None:
        #DBInterface.__outputTable()
        pass
    def db_machineUsage(self, UCINetID: str, email: str) -> None:
        #DBInterface.__outputTable()
        pass
    
    