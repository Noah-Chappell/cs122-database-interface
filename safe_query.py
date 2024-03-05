from database_connectable import SqlCursor

class SafeQuery:
    '''
    query which requires an undo method to be instantiated
    '''
    def __init__(self, query: str, reverseQuery: str) -> None:
        self.doQuery = query
        self.undoQuery = reverseQuery
    def executeMultiple(queryList: list, cursor: SqlCursor) -> bool:
        complete = 0
        try:
            for safeQuery in queryList:
                cursor.execute(safeQuery.doQuery)
                complete += 1
        except Exception as err:
            try:
                for i in range(complete):
                    cursor.execute(queryList[i].undoQuery)
            except Exception as cleanupErr:
                print(f"there was an issue with cleanup: ")
                print(cleanupErr)
            raise err

