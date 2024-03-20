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
    if passed database does not exist, an empty database of that name
    will be created
    '''
    #all functions are prefixed with db to avoid naming collisions, so db_ is
    #added to function calls
    COMMAND_PREFIX = "db_"

    def __init__(self, host: str, user: str, password: str, databaseName: str) -> None:
        super().__init__(host, user, password, databaseName)
    
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
            outputRow = str(row).strip("[](),")
            outputRow.replace("'NULL'", "NULL")
            print(outputRow)



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
    

    def executeMultipleQueryCommand(self, safeQueryList: list, commit: bool, debug=False) -> bool:
        '''
        facilitates the execution of multiple safeQuerys and returns whether
        that query succeded or failed, passed queries must
        be of SageQuerying.SafeQuery
        '''
        try:
            SafeQuerying.SafeQuery.executeMultiple(safeQueryList, self.dbCursor)
            if (commit):
                self.dbConnetion.commit()
        except Exception as err:
            if (err.__class__.__module__ == DbConnectable.SqlErrorModuleName):
                if (debug):
                    print(err)
                return False
            else:
                raise err
        return True
    
    def executeSingleQueryCommand(self, query: str, commit: bool, debug=False) -> bool:
        '''
        facilitates the execution of a single passed query and returns whether
        that query succeded or failed
        '''
        try:
            self.dbCursor.execute(query)
            if (commit):
                self.dbConnetion.commit()
        except Exception as err:
            if (err.__class__.__module__ == DbConnectable.SqlErrorModuleName):
                if (debug):
                    print(err)
                return False
            else:
                raise err
        return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~PROJECT REQUIRED FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~

    def db_import(self, folderPath: str) -> None:
        '''
        Delete existing tables, and create new tables. Then read the csv files 
        in the given folder and import data into database. You can assume that 
        the folder always contains all the necessary CSV files and the files are 
        correct.

        in -> python3 project.py import [folderName:str]

        out -> Table - Number of users,Number of machine, Number of Course
        '''
        self.drop_tables()
        self.initializeTables()
        self.fill_tables(folderPath)
                
        
        numUsers = self.db_tableSize('Users')
        numMachines = self.db_tableSize('Machines')
        numCourses = self.db_tableSize('Courses')
        
        DbInterface.__outputTable([[numUsers, numMachines, numCourses]])

    def db_insertStudent(self, UCINetID: str, email: str, First: str, Middle: str, Last: str, commit=True) -> None:
        '''
        Insert a new student into the related tables.

        in -> python3 project.py insertStudent [UCINetID:str] [email:str] [First:str] [Middle:str] [Last:str]
        out -> Bool
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

        in -> python3 project.py addEmail[UCINetID:str] [email:str]
        out -> Bool
        '''
        query = f"INSERT INTO UserEmail\
                    VALUES('{UCINetID}', '{email}')"
        querySuccess = self.executeSingleQueryCommand(query, commit)
        DbInterface.__outputBool(querySuccess)
    
    def db_deleteStudent(self, UCINetID: str, commit=True) -> None:
        '''
        Delete the student in both the User and Student table.

        in -> python3 project.py deleteStudent [UCINetID:str]
        out -> Bool
        '''
        query = f"DELETE FROM Users\
                    WHERE UCINetID = '{UCINetID}'"
        querySuccess = self.executeSingleQueryCommand(query, commit)
        DbInterface.__outputBool(querySuccess)

    def db_insertMachine(self, MachineID: str, hostname: str, IPAddr:str, status: str, location: str, commit=True) -> None:
        '''
        Insert a new machine.

        in -> python3 project.py insertMachine [MachineID:int] [hostname:str] [IPAddr:str] [status:str] [location:str]
        out -> Bool
        '''
        query = f"INSERT INTO Machines\
                    VALUES ({MachineID}, '{hostname}', '{IPAddr}', '{status}', '{location}')"
        querySuccess = self.executeSingleQueryCommand(query, commit)
        DbInterface.__outputBool(querySuccess)

    def db_insertUse(self, ProjId: str, UCINetID: str, MachineID: str, start: str, end: str, commit=True) -> None:
        '''
        Insert a new use record.

        in -> python3 project.py insertUse [ProjId:int] [UCINetID:str] [MachineID:int] [start:date] [end:date]
        out -> Bool
        '''
        query = f"INSERT INTO StudentUseMachinesInProject\
                    VALUES ({ProjId}, '{UCINetID}', {MachineID}, '{start}', '{end}')"
        querySuccess = self.executeSingleQueryCommand(query, commit)
        DbInterface.__outputBool(querySuccess)
    
    def db_updateCourse(self, CourseId: str, title: str, commit=True) -> None:
        '''
        Update the title of a course

        in -> python3 project.py updateCourse [CourseId:int] [title:str]
        out -> Bool
        '''
        query = f"UPDATE Courses\
                    SET Title = '{title}'\
                    WHERE CourseID = {CourseId}"
        querySuccess = self.executeSingleQueryCommand(query, commit)
        DbInterface.__outputBool(querySuccess)

    def db_listCourse(self, UCINetID: str) -> None:
        '''
        Given a student ID, list all unique courses the student attended. Ordered by courseId ascending.

        in -> python3 project.py listCourse [UCINetID:str]
        out -> Table - CourseId,title,quarter
        '''
        query = f"SELECT DISTINCT C.CourseID, Title, Quarter FROM Courses C\
                    JOIN Projects P ON C.CourseID = P.CourseID\
                    JOIN StudentUseMachinesInProject SU ON P.ProjectID = SU.ProjectID\
                    WHERE StudentUCINetID = '{UCINetID}'\
                    ORDER BY C.CourseID ASC"
        querySuccess = self.executeSingleQueryCommand(query, commit=False)
        if querySuccess:
            rows = self.dbCursor.fetchall()
            DbInterface.__outputTable(rows)

    def db_popularCourse(self, N: int) -> None:
        '''
        List the top N course that has the most students attended. Ordered by studentCount, courseID descending.

        in -> python3 project.py popularCourse [N: int]
        out -> Table - CourseId,title,studentCount
        '''
        query = f"SELECT C.CourseID, Title, COUNT(StudentUCINetID) AS NumStudents FROM Courses C\
                    JOIN Projects P ON C.CourseID = P.CourseID\
                    JOIN StudentUseMachinesInProject SU ON P.ProjectID = SU.ProjectID\
                    GROUP BY C.CourseID\
                    ORDER BY NumStudents DESC, C.CourseID DESC\
                    LIMIT {N}"
        querySuccess = self.executeSingleQueryCommand(query, commit=False)
        if querySuccess:
            rows = self.dbCursor.fetchall()
            DbInterface.__outputTable(rows)

    def db_adminEmails(self, machineId: int) -> None:
        '''
        Given a machine ID, find all administrators of that machine. 
        List the emails of those administrators. Ordered by netid ascending.

        in -> python3 project.py adminEmails [machineId: int]
        out -> Table - UCINETId,first name,middle name,last name,list of email
        '''
        query = f"SELECT AdministratorUCINetID, FirstName, MiddleName, LastName, GROUP_CONCAT(Email SEPARATOR ';') FROM AdministratorManageMachines AM\
                    JOIN Users U ON AM.AdministratorUCINetID = U.UCINetID\
                    JOIN UserEmail UE ON U.UCINetID = UE.UCINetID\
                    WHERE MachineID = {machineId}\
                    GROUP BY AdministratorUCINetID\
                    ORDER BY AdministratorUCINetID ASC"
        querySuccess = self.executeSingleQueryCommand(query, commit=False)
        if querySuccess:
            rows = self.dbCursor.fetchall()
            DbInterface.__outputTable(rows)

    def db_activeStudent(self, machineId: int, N: int, start: Date, end: Date) -> None:
        '''
        Given a machine Id, find all active students that used it more than N 
        times (including N) in a specific time range (including start and end date). 
        Ordered by netid ascending. N will be at least 1.
        
        in -> python3 project.py activeStudent [machineId: int] [N:int] [start:date] [end:date]
        out -> Table - UCINETId,first name,middle name,last name
        '''
        
        query = f"SELECT StudentUCINetID, FirstName, MiddleName, LastName\
                    FROM StudentUseMachinesInProject SU\
                    JOIN Users U\
                        ON SU.StudentUCINetID = U.UCINetID\
                    WHERE MachineID = {machineId} AND StartDate >= '{start}' AND EndDate <= '{end}'\
                    GROUP BY MachineID, StudentUCINetID, SU.StudentUCINetID, FirstName, MiddleName, LastName\
                        Having COUNT(*) >= {N}\
                    ORDER BY StudentUCINetID ASC"
        querySuccess = self.executeSingleQueryCommand(query, commit=False)
        if querySuccess:
            rows = self.dbCursor.fetchall()
            DbInterface.__outputTable(rows)


    def db_machineUsage(self, courseId: int) -> None:
        '''
        Given a course id, count the number of usage of each machine in that course.
        Each unique record in the MachineUse table counts as one usage. Machines that
        are not used in the course should have a count of 0 instead of NULL. 
        Ordered by machineId descending.

        in -> python3 project.py machineUsage [courseId: int]
        out -> Table - machineID,hostname,ipAddr,count
        '''

        query = f"SELECT MachineID, Hostname, IPAddress, COUNT(ProjectID)\
                    FROM Courses\
                    JOIN Projects\
                        USING (CourseID)\
                    JOIN StudentUseMachinesInProject\
                        USING (ProjectID)\
                    RIGHT JOIN Machines\
                        USING (MachineID)\
                    WHERE CourseID = {courseId}\
                    GROUP BY MachineID, Hostname, IPAddress\
                    ORDER BY MachineID DESC"
        querySuccess = self.executeSingleQueryCommand(query, commit=False, debug=True)
        if querySuccess:
            rows = self.dbCursor.fetchall()
            DbInterface.__outputTable(rows)
    





# /\___/\
#(  _ _  )
#  = Y =
#_.__..._/..___