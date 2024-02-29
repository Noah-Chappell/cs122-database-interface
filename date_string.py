class Date:
    def __init__(self, year: int | str , month: int=None, day: int=None) -> None:
        '''
        takes a year, month, or day and creates a date in the SQL assignment
        format, it also can take only a dateString
        ''' 
        
        if (isinstance(year, str)):
            if (len(year) != 10):
                raise ValueError("invalid dateString input")
            self.year: str = year[:4]
            self.month: str = year[5:7]
            self.day: str = year[8:]

        elif (isinstance(year, int)):
            self.year: str = Date.formatInt(year, 4)
            self.month: str = Date.formatInt(month, 2)
            self.day: str = Date.formatInt(day, 2)
        else:
            raise ValueError(f"invalid arguments: {year}, {month}, {day}")
    
    def __str__(self) -> str:
        return f'{self.year}-{self.month}-{self.day}'
    
    def formatInt(dateInt: int, requiredLength: int) -> str:
        dateString = str(dateInt)
        leadingZeroes = '0'*(requiredLength - len(dateString))
        return leadingZeroes + dateString