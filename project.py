import sys
from typing import Callable

#custom modules
import date_string as Date


class DbInterface:
    def getFunction(functionName : str) -> Callable | None:
        '''
        returns DbInterface function if present, else returns None
        '''
        classFunction: callable | None = getattr(DbInterface, functionName, None)
        if (callable(classFunction)):
            return classFunction
        return None


def getCommandLineInput() -> list[str]:
    '''
    returns command line input without filename
    '''
    return sys.argv[1:]


def main():
    # input format:[function arg1 arg2 ...]
    input: list[str] = getCommandLineInput()

    command: Callable | None = DbInterface.getFunction(input[0])
    if (command == None):
        raise ValueError(f'DbInterface has no function {input[0]}')
    
    command(*input[1:])

if __name__ == '__main__':
    main()