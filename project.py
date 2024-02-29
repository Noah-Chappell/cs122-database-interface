import sys
from typing import Callable

#custom modules
import date_string as Date
from database_interface import DbInterface

#TODO: fill in info once db is setup
DB_CONNECTION_INFO = {
    "host":"localhost",
    "user":"",
    "passwd":"",
    "database":""
}


def getConsoleInput() -> list[str]:
    '''
    returns command line input without filename
    '''
    return sys.argv[1:]


def main():
    # input format:[function arg1 arg2 ...]
    CONSOLE_INPUT: list[str] = getConsoleInput()

    DB_INTERFACE = DbInterface(*DB_CONNECTION_INFO)
    command: Callable | None = DB_INTERFACE.getFunction(CONSOLE_INPUT[0])
    if (command == None):
        raise ValueError(f'DbInterface has no function {CONSOLE_INPUT[0]}')
    
    command(*CONSOLE_INPUT[1:])

if __name__ == '__main__':
    main()