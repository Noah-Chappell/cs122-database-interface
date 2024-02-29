from typing import Callable
#TODO: import mysql.connector

class DbInterface:
    '''
    interface to communicate with SQL database via callable functions
    '''
    def __init__(self, **kwargs) -> None:
        #TODO: initialize database connection and store it in this.DB
        #TODO: store cursor int this.dbCursor
        pass

    def getFunction(functionName : str) -> Callable | None:
        '''
        returns DbInterface function if present, else returns None
        '''
        classFunction: callable | None = getattr(DbInterface, functionName, None)
        if (callable(classFunction)):
            return classFunction
        return None
    
    #TODO: add assignment required methods