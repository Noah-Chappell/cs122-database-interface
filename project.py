import sys
from typing import Callable

#custom modules
from database_interface import DbInterface

#TODO: fill in info once db is setup
DB_CONNECTION_INFO = {
    'host':'localhost',
    'user':'root',
    'password':'root',
    'databaseName':'ics-server-database'
}


def getConsoleInput() -> list[str]:
    '''
    returns command line input without filename
    '''
    return sys.argv[1:]


def main():
    # input format:[function arg1 arg2 ...]
    CONSOLE_INPUT: list[str] = getConsoleInput()

    DB_INTERFACE = DbInterface(**DB_CONNECTION_INFO)
    print("---connection established---")
    command: Callable | None = DB_INTERFACE.getFunction(CONSOLE_INPUT[0])
    if (command == None):
        raise ValueError(f'DbInterface has no function {CONSOLE_INPUT[0]}')
    print("---calling---")
    command(DB_INTERFACE, *CONSOLE_INPUT[1:])
    print("---finished---")

if __name__ == '__main__':
    main()