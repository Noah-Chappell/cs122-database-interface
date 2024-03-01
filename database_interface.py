from typing import Callable

#custom modules
import date_string as Date
import database_connectable as DbConnectable


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

    def __outputTable(dbConnection: DbConnectable.SqlConnection) -> None:
        '''
        prints output of SQL command assuming the value is a table
        '''
        for row in dbConnection:
            printRow: str = ""
            for item in row:
                printRow += item + ','
            print(printRow[:-1])


    def getFunction(functionName : str) -> Callable | None:
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
    


    #TODO: finish all assignment functions
    def db_import(folderName: str) -> None:
        #__outputTable()
        pass
    def db_addEmail(UCINetID: str, email: str) -> None:
        #__outputBool()
        pass
    def db_deleteStudent(UCINetID: str, email: str) -> None:
        #__outputBool()
        pass
    def db_insertMachine(UCINetID: str, email: str) -> None:
        #__outputBool()
        pass
    def db_insertUse(UCINetID: str, email: str) -> None:
        #__outputBool()
        pass
    def db_updateCourse(UCINetID: str, email: str) -> None:
        #__outputBool()
        pass
    def db_listCourse(UCINetID: str, email: str) -> None:
        #__outputTable()
        pass
    def db_popularCourse(UCINetID: str, email: str) -> None:
        #__outputTable()
        pass
    def db_adminEmails(UCINetID: str, email: str) -> None:
        #__outputTable()
        pass
    def db_activeStudent(UCINetID: str, email: str) -> None:
        #__outputTable()
        pass
    def db_machineUsage(UCINetID: str, email: str) -> None:
        #__outputTable()
        pass
    
    