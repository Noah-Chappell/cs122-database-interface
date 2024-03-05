class TableInitData:
    def __init__(self, tableName, initCommand) -> None:
        self.tableName = tableName
        self.initCommand = initCommand

TABLE_CREATE_ORDER = ['users', 'emails', 'students', 'admins', 'courses', 'projects', 'machines', 'use', 'manage']

ALIAS_TABLE_MAP = {
            'users' : TableInitData(
                        'Users', 
                        '''
                        CREATE TABLE Users (
                            UCINetID VARCHAR(20) PRIMARY KEY NOT NULL,
                            FirstName VARCHAR(50),
                            MiddleName VARCHAR(50),
                            LastName VARCHAR(50)
                        );
                        '''),
            'emails' : TableInitData(
                        'UserEmail',
                        '''
                        CREATE TABLE UserEmail (
                            UCINetID VARCHAR(20) NOT NULL,
                            Email    VARCHAR(320),
                            PRIMARY KEY (UCINetID, Email),
                            FOREIGN KEY (UCINetID) REFERENCES Users (UCINetID)
                                ON DELETE CASCADE
                        );
                        '''),
            'students' : TableInitData(
                        'Students',
                        '''
                        CREATE TABLE Students (
                                UCINetID VARCHAR(20) PRIMARY KEY NOT NULL,
                                FOREIGN KEY (UCINetID) REFERENCES Users(UCINetID)
                                ON DELETE CASCADE
                            );
                            '''),
            'admins' : TableInitData(
                        'Administrators',
                        '''
                        CREATE TABLE Administrators (
                            UCINetID VARCHAR(20) PRIMARY KEY NOT NULL,
                            FOREIGN KEY (UCINetID) REFERENCES Users(UCINetID)
                            ON DELETE CASCADE
                        );
                        '''),
            'courses' : TableInitData(
                        'Courses' ,
                        '''
                        CREATE TABLE Courses (
                            CourseID INT PRIMARY KEY NOT NULL,
                            Title VARCHAR(100),
                            Quarter VARCHAR(20)
                        );
                        '''),
            'projects' : TableInitData(
                        'Projects',
                        '''
                        CREATE TABLE Projects (
                                ProjectID INT PRIMARY KEY NOT NULL,
                                Name VARCHAR(100),
                                Description TEXT,
                                CourseID INT NOT NULL,
                                FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
                            );
                            '''),
            'machines' : TableInitData(
                        'Machines',
                        '''
                        CREATE TABLE Machines (
                                MachineID INT PRIMARY KEY NOT NULL,
                                Hostname VARCHAR(255),
                                IPAddress VARCHAR(15),
                                OperationalStatus VARCHAR(50),
                                Location VARCHAR(255)
                            );
                            '''),
            'use' : TableInitData(
                        'StudentUseMachinesInProject',
                        '''
                        CREATE TABLE StudentUseMachinesInProject (
                            ProjectID INT,
                            StudentUCINetID VARCHAR(20),
                            MachineID INT,
                            StartDate DATE,
                            EndDate DATE,
                            PRIMARY KEY (ProjectID, StudentUCINetID, MachineID),
                            FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
                            FOREIGN KEY (StudentUCINetID) REFERENCES Students(UCINetID),
                            FOREIGN KEY (MachineID) REFERENCES Machines(MachineID)
                        );
                        '''),
            'manage' : TableInitData(
                        'AdministratorManageMachines',
                        '''
                        CREATE TABLE AdministratorManageMachines (
                            AdministratorUCINetID VARCHAR(20),
                            MachineID INT,
                            PRIMARY KEY (AdministratorUCINetID, MachineID),
                            FOREIGN KEY (AdministratorUCINetID) REFERENCES Administrators(UCINetID),
                            FOREIGN KEY (MachineID) REFERENCES Machines(MachineID)
                        );
                        ''')
        }