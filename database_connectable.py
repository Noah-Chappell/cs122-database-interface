from typing import Type
import mysql.connector

SqlConnection = Type[mysql.connector.connection_cext.CMySQLConnection]

DATABASE_NOT_FOUND: int = 1049

class Connectable:
    def __init__(self, host: str, user: str, password: str, databaseName: str) -> None:
        #connects to SQL database and stores in instance variable, if database 
        #doesnt exist, it will be created
        dbConnection: SqlConnection | None = None
        try:
            dbConnection = Connectable.__connectToDatabase(host, user, password, databaseName)

        except mysql.connector.errors.ProgrammingError as err:
            if (err.errno == DATABASE_NOT_FOUND):

                dbConnection = Connectable.__connectToServer(host, user, password)
                dbConnection.execute(f'CREATE DATABASE {databaseName}')
                dbConnection.commit()

                dbConnection = Connectable.__connectToDatabase(host, user, password, databaseName)
            else:
                raise err
            
        self.dbConnection: SqlConnection = dbConnection

    def __connectToDatabase(host: str, user: str, password: str, databaseName: str) -> SqlConnection:
        '''
        returns a connection to a database on SQL server based on passed 
        parameters
        '''
        return mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=databaseName
            )
    
    def __connectToServer(host: str, user: str, password: str) -> SqlConnection:
        '''
        returns a connection to SQL server based on passed parameters
        '''
        return mysql.connector.connect(
                host=host,
                user=user,
                password=password,
            )