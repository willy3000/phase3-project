import sqlite3
import random
from termcolor import colored


conn = sqlite3.connect('portal.db')
conn.execute('''CREATE TABLE IF NOT EXISTS STUDENTS
         (ID VARCHAR(255) PRIMARY KEY NOT NULL,
         NAME VARCHAR(255) NOT NULL, COURSE_ID VARCHAR(255) NOT NULL, MENTOR_ID VARCHAR(255) NOT NULL);''')
conn.execute('''CREATE TABLE IF NOT EXISTS MENTORS
         (ID VARCHAR(255) PRIMARY KEY NOT NULL,
         NAME VARCHAR(255) NOT NULL, COURSE_ID VARCHAR(255) NOT NULL, STUDENTS_COUNT INT NOT NULL);''')
conn.execute('''CREATE TABLE IF NOT EXISTS COURSES
         (ID VARCHAR(255) PRIMARY KEY NOT NULL,
         NAME VARCHAR(255) NOT NULL);''')
conn.execute('''CREATE TABLE IF NOT EXISTS MARKS
         (ID VARCHAR(255) PRIMARY KEY NOT NULL,
         PHASE0 INT NULL, PHASE1 INT NULL,PHASE2 INT NULL,PHASE3 INT NULL,PHASE4 INT NULL, PHASE5 INT NULL);''')


def generateId(name):
    value = ''.join(str(random.randint(0, 9)) for _ in range(4))
    id = name[:2] + "-" + value
    return id


def getAverage(marks):
    total_phases = 6
    sum = 0
    for grade in marks:
        if (grade == None):
            total_phases -= 1
        else:
            sum += int(grade)
    if (total_phases == 0):
        return "None"
    return format(sum/total_phases, '.2f')


def getMentorAverage(mentorId):
    sum = 0
    excluded_students = 0
    students = conn.execute(
        'SELECT * FROM STUDENTS WHERE MENTOR_ID=?', (mentorId,)).fetchall()
    for student in students:
        marks = conn.execute('SELECT * FROM MARKS WHERE ID=?',
                             (student[0],)).fetchall()[0]
        student_average = getAverage([marks[1], marks[2],
                                      marks[3], marks[4], marks[5], marks[6]])
        if (student_average == "None"):
            excluded_students += 1
        else:
            sum += float(student_average)

    if (excluded_students == len(students)):
        return 'None'
    return format(sum/(len(students)-excluded_students), '.2f')


def selectStudent():
    option = 0
    print("1. All Students")
    print("2. Search for Student")
    option = input('Select Option: ')
    if (option == '1'):
        students = getStudents()
        for index, student in enumerate(students):
            print(f"{index+1}. {student[0]} | {student[1]}")
        option = input('Select Student: ')
    elif (option == "2"):
        keyword = input("Search by Name or ID : ")
        students = searchMembers(keyword, getStudents())
        for index, student in enumerate(students):
            print(f"{index+1}. {student[0]} | {student[1]}")
        option = input('Select Student: ')
    return students[int(option)-1]


def selectMentor():
    option = 0
    print("1. All Mentors")
    print("2. Search for Mentor")
    option = input('Select Option: ')
    if (option == '1'):
        mentors = getMentors()
        for index, mentor in enumerate(mentors):
            print(f"{index+1}. {mentor[0]} | {mentor[1]}")
        option = input('Select Mentor: ')
    elif (option == "2"):
        keyword = input("Search by Name or ID : ")
        mentors = searchMembers(keyword, getMentors())
        for index, mentor in enumerate(mentors):
            print(f"{index+1}. {mentor[0]} | {mentor[1]}")
        option = input('Select Mentor: ')
    return mentors[int(option)-1]


def getCourses():
    data = conn.execute("SELECT * FROM COURSES")
    courses = data.fetchall()
    return courses


def getStudents():
    data = conn.execute("SELECT * FROM STUDENTS")
    students = data.fetchall()
    return students


def getMentors():
    data = conn.execute("SELECT * FROM MENTORS")
    mentors = data.fetchall()
    return mentors


def getMentor(mentorId):
    data = conn.execute("SELECT * FROM MENTORS WHERE ID=?", (mentorId,))
    mentor = data.fetchall()[0]
    return mentor


def searchMembers(keyword, members):
    filteredMembers = []
    for member in members:
        if (keyword.lower() == member[0].lower()):
            filteredMembers.append(member)
        elif (keyword.lower() in member[1].lower()):
            filteredMembers.append(member)
    return filteredMembers


def getStudentDetails(student):
    studentId = student[0]
    studentName = student[1]
    courseId = student[2]

    marksData = conn.execute("SELECT * FROM MARKS WHERE ID=?", (studentId,))
    marks = marksData.fetchall()[0]

    courseData = conn.execute("SELECT * FROM COURSES WHERE ID=?", (courseId,))
    course = courseData.fetchall()[0]
    print("----------------------Details-----------------------")
    print()
    print("Student Name: "+studentName)
    print("Course: "+course[1])
    print("Technical Mentor: " + getMentor(student[3])[1])
    print("Phase 0: "+str(marks[1]))
    print("Phase 1: "+str(marks[2]))
    print("Phase 2: "+str(marks[3]))
    print("Phase 3: "+str(marks[4]))
    print("Phase 4: "+str(marks[5]))
    print("Phase 5: "+str(marks[6]))
    print("Average: " + str(getAverage([marks[1], marks[2],
          marks[3], marks[4], marks[5], marks[6]])))
    print()
    print("---------------------------------------------")


def getMentorDetails(mentor):
    mentorName = mentor[1]
    courseId = mentor[2]

    courseData = conn.execute("SELECT * FROM COURSES WHERE ID=?", (courseId,))
    course = courseData.fetchall()[0]
    print("----------------------Details-----------------------")
    print()
    print("Mentor Name: "+mentorName)
    print("Course: "+course[1])
    print("Students: " + str(mentor[3]))
    print("Average Performance: " + str(getMentorAverage(mentor[0])))
    print()
    print("---------------------------------------------")


def deregisterStudent(studentId, mentorId):
    mentor = getMentor(mentorId)
    students_count = mentor[3]
    print('student id', studentId)
    conn.execute("DELETE FROM STUDENTS WHERE ID=?", (studentId,))
    conn.execute('UPDATE MENTORS SET STUDENTS_COUNT=? WHERE  ID=?',
                 (students_count-1, mentorId))
    conn.commit()
    print(colored('Student Deregistered', 'green'))


def recordMarks(studentId, phase, marks):
    print('student id', studentId)
    phase = "PHASE"+str(phase)
    conn.execute(
        f'UPDATE MARKS set {phase} = ? WHERE  ID=?', (marks, studentId))
    conn.commit()


class Student:
    def __init__(self, name):
        self.name = name
        self.id = generateId(name)

    def enroll(self, courseId, mentor):
        mentorId = mentor[0]
        students_count = mentor[3]
        conn.execute("INSERT INTO STUDENTS (ID,NAME, COURSE_ID, MENTOR_ID) VALUES (?, ?, ?, ?)",
                     (self.id, self.name, courseId, mentorId))
        conn.execute("INSERT INTO MARKS (ID,PHASE0, PHASE1, PHASE2, PHASE3, PHASE4, PHASE5) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (self.id, None, None, None, None, None, None))
        conn.execute('UPDATE MENTORS SET STUDENTS_COUNT=? WHERE  ID=?',
                     (students_count+1, mentorId))
        conn.commit()


class Mentor:
    def __init__(self, name):
        self.name = name
        self.id = generateId(name)

    def enroll(self, courseId):
        conn.execute("INSERT INTO MENTORS (ID,NAME, COURSE_ID, STUDENTS_COUNT) VALUES (?, ?, ?, ?)",
                     (self.id, self.name, courseId, 0))
        conn.commit()


class Course:
    def __init__(self, name):
        self.name = name
        self.id = generateId(name)

    def create_course(self):
        conn.execute("INSERT INTO COURSES (ID,NAME) VALUES (?, ?)",
                     (self.id, self.name))
        conn.commit()
        getCourses()


def registerStudent():
    name = input('Enter student name: ')
    student = Student(name)
    print()
    print('Select Course')
    for index, course in enumerate(getCourses()):
        print(f"{index+1}. {course[1]}")
    option = input('Select Course : ')
    courses = getCourses()
    courseId = courses[int(option)-1][0]
    print()
    print('Assign Tecnical Mentor')
    for index, course in enumerate(getMentors()):
        print(f"{index+1}. {course[1]}")
    option = input('Select Mentor : ')
    mentors = getMentors()
    mentor = mentors[int(option)-1]
    student.enroll(courseId, mentor)
    print(colored('Student Enrolled', 'green'))


def registerTechnicalMentor():
    name = input('Enter mentor name: ')
    mentor = Mentor(name)
    print()
    print('Select Course')
    for index, course in enumerate(getCourses()):
        print(f"{index+1}. {course[1]}")
    option = input('Select Course : ')
    courses = getCourses()
    courseId = courses[int(option)-1][0]
    mentor.enroll(courseId)
    print(colored('Technical Mentor Enrolled', 'green'))


def createNewourse():
    name = input('Enter course name: ')
    course = Course(name)
    course.create_course()
    print(colored('Course Created', 'green'))


while True:
    print()
    print("----------MENU----------")
    print()
    print("1. Register Student")
    print("2. See Student's Details")
    print("3. De-register Student")
    print("4. Create New Course")
    print("5. Record Marks")
    print("6. Register Technical Mentor")
    print("7. See Technical Mentor Details")
    print()

    option = input('Select Option: ')

    courses = getCourses()
    mentors = getMentors()
    if (option == '1'):
        if (len(courses) == 0):
            print(colored(
                "No Courses available for students to enroll under, create course first.", 'red'))
        elif (len(mentors) == 0):
            print(colored(
                "No Mentors available for students to enroll under, create mentor first.", 'red'))
        else:
            registerStudent()
    elif (option == '2'):
        print("1. All Students")
        print("2. Search for Student")
        option = input('Select Option: ')
        if (option == '1'):
            students = getStudents()
            print()
            print("---------------------------Students-----------------------------")
            for index, student in enumerate(students):
                print(f"{index+1}. {student[0]} | {student[1]}")
            print("-------------------------------------------------------------")
            print()
            option = input('Select Student: ')
            getStudentDetails(students[int(option)-1])
        elif (option == "2"):
            keyword = input("Search by Name or ID : ")
            students = searchMembers(keyword, getStudents())
            for index, student in enumerate(students):
                print(f"{index+1}. {student[0]} | {student[1]}")
            option = input('Select Student: ')
            getStudentDetails(students[int(option)-1])

    elif (option == "3"):
        print("1. All Students")
        print("2. Search for Student")
        option = input('Select Option: ')
        if (option == '1'):
            students = getStudents()
            for index, student in enumerate(students):
                print(f"{index+1}. {student[0]} | {student[1]}")
            option = input('Select Student: ')
            print(
                colored('Are you sure you want to deregister this student? (y/n): ', 'yellow'))
            confirmation = input().lower()
            if (confirmation == 'y'):
                deregisterStudent(
                    students[int(option)-1][0], students[int(option)-1][3])
            else:
                print(colored('Deregistration cancelled', 'red'))
        elif (option == "2"):
            keyword = input("Search by Name or ID : ")
            students = searchMembers(keyword, getStudents())
            for index, student in enumerate(students):
                print(f"{index+1}. {student[0]} | {student[1]}")
            option = input('Select Student: ')
            print(
                colored('Are you sure you want to deregister this student? (y/n): ', 'yellow'))
            confirmation = input().lower()
            if (confirmation == 'y'):
                deregisterStudent(
                    students[int(option)-1][0], students[int(option)-1][3])
            else:
                print(colored('Deregistration cancelled', 'red'))

    elif (option == "4"):
        createNewourse()

    elif (option == "5"):
        studentId = selectStudent()[0]
        print()
        print("-------------------Select Phase-------------------")
        print('0. PHASE 0')
        print('1. PHASE 1')
        print('2. PHASE 2')
        print('3. PHASE 3')
        print('4. PHASE 4')
        print('5. PHASE 5')
        print()
        print("----------------------------------------------------")
        phase = input('Select Phase: ')
        marks = input(f'Enter Students Marks for Phase{phase}: ')
        recordMarks(studentId, phase, marks)
    elif (option == "6"):
        if (len(courses) == 0):
            print(colored(
                "No Courses available for technical mentor to enroll under, create course first.", 'red'))
        else:
            registerTechnicalMentor()
    elif (option == '7'):
        mentor = selectMentor()
        getMentorDetails(mentor)
