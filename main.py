import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

conn = sqlite3.connect("House points")
cursor = conn.cursor()

window = ctk.CTk()
window.title('House Points System')
window.geometry('1000x600')
window.resizable(False, False)
ctk.set_appearance_mode("light")

default_color = '#262832'

class User:
    def __init__(self, password, first_name, last_name):
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def login(selected_role, Id_entry, password_entry):
            if selected_role.get() == 'Student':
                Id = Id_entry.get()
                password = password_entry.get()
                user = cursor.execute("SELECT * FROM Student WHERE student_id = ?", (Id,)).fetchall()
                if user:
                    if user[0][1] == password:
                        first_name = user[0][2]
                        last_name = user[0][3]
                        grade = user[0][4]
                        StudentHouse = user[0][5]
                        StudentPoints = user[0][6]
                        student = Student(Id, password, first_name, last_name, grade, StudentHouse, StudentPoints)
                        StudentHomePage(student)
                    else:
                        messagebox.showerror("Login Failed", "Invalid Password")
                else:
                    messagebox.showerror("Login Failed", "User does not exist")
            elif selected_role.get() == 'Teacher':
                Id = Id_entry.get()
                password = password_entry.get()
                user = cursor.execute("SELECT * FROM Teacher WHERE teacher_id = ?", (Id,)).fetchall()
                if user:
                    if user[0][1] == password:
                        first_name = user[0][2]
                        last_name = user[0][3]
                        subject = user[0][4]
                        teacher = Teacher(Id, password, first_name, last_name, subject)
                        TeacherHomePage(teacher)
                    else:
                        messagebox.showerror("Login Failed", "Invalid Id or password")
                else:
                    messagebox.showerror("Login Failed", "User does not exist")
            else:
                messagebox.showerror("Login Failed", "Select Student or Teacher")

class Student(User):
        def __init__(self, Id, password, first_name, last_name, grade, StudentHouse, StudentPoints):
            super().__init__(password, first_name, last_name)
            self.student_id = Id
            self.student_first_name = first_name
            self.student_last_name = last_name
            self.student_grade = grade
            self.student_houseId = StudentHouse
            self.student_points = StudentPoints

        def CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_class, selected_house, year_groups):
                first_name = EnterFirstName.get()
                last_name = EnterLastName.get()
                password = EnterPassword.get()
                Id = EnterId.get()
                grade = selected_class.get()
                if first_name == '' or last_name == '' or password == '' or Id == '' or grade not in year_groups:
                    messagebox.showerror('',"Account not created, please properly fill all fields to create an account")
                else:
                    if selected_house == '':
                        messagebox.showerror('',"Account not created, please select a house")
                    else:
                        houseId = GetHouseID(selected_house)
                        cursor.execute("INSERT INTO Student (student_ID, password, first_name, last_name, grade, house_id, total_points, leaderboard_position) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (Id, password, first_name, last_name, grade, houseId, 0, 0))
                        conn.commit()
                        for i in range(1,4):
                            cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (?, ?, ?)", (Id, i, 0))
                            conn.commit()
                        messagebox.showinfo('',"Account created!")
                        RemoveWidgets()
                        Loginpage()

        def UpdateStudentFields(self, FirstName_entry, LastName_entry, student):
            NewFirstName = FirstName_entry.get()
            NewLastName = LastName_entry.get()
            cursor.execute("UPDATE Student SET first_name = ? WHERE student_id = ?", (NewFirstName, self.student_id,))
            cursor.execute("UPDATE Student SET last_name = ? WHERE student_id = ?", (NewLastName, self.student_id,))
            conn.commit()
            self.student_first_name = NewFirstName
            self.student_last_name = NewLastName
            messagebox.showinfo('',"Successfully updated account details")
            RemoveWidgets()
            StudentHomePage(student)

        def PurchaseToken(self, token_id):
            purchase_date =  datetime.now().strftime('%Y-%m-%d')
            point_cost = cursor.execute("SELECT point_cost FROM Token WHERE token_id = ?", (token_id,)).fetchone()
            new_sum = self.student_points - point_cost[0]
            if new_sum < 0:
                messagebox.showerror('',"Insufficient number of points, no points deducted")
                new_sum = 0
                cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_sum, self.student_id,))
                conn.commit()
            else:
                cursor.execute("INSERT INTO Purchase_token (student_id, token_id, purchase_date) VALUES (?, ?, ?);", (self.student_id, token_id, purchase_date))
                intial_quantity = cursor.execute("SELECT quantity FROM Student_token_ownership WHERE student_id = ? AND token_id = ?", (self.student_id, token_id,)).fetchone()
                new_quantity = intial_quantity[0] + 1
                cursor.execute("UPDATE Student_token_ownership SET quantity = ? WHERE student_id = ? AND token_id = ?", (new_quantity, self.student_id, token_id,))
                cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_sum, self.student_id))
                conn.commit()
                messagebox.showinfo('',"Token purchased!")
            self.student_points = new_sum

class Teacher(User):
    def __init__(self, Id, password, first_name, last_name, subject):
        super().__init__(password, first_name, last_name)
        self.teacher_id = Id
        self.teacher_first_name = first_name
        self.teacher_last_name = last_name
        self.teacher_subject = subject

    def CreateNewTeacher(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_subject, subjects):
        id = EnterId.get()
        password = EnterPassword.get()
        first_name = EnterFirstName.get()
        last_name = EnterLastName.get()
        subject = selected_subject
        if first_name == '' or last_name== '' or id == '':
            messagebox.showerror('',"Account not created, please properly fill all fields to create an account")
        else:
            if subject not in subjects:
                messagebox.showerror('',"Account not created, please select the subject you teach")
            else:
                cursor.execute("INSERT INTO Teacher (teacher_id, password, first_name, last_name, subject) VALUES (?, ?, ?, ?, ?)", (id, password, first_name, last_name, subject,))
                conn.commit()
                messagebox.showinfo('',"Account created!")
                RemoveWidgets()
                Loginpage()

    def ChangeStudentPoints(teacher, search, change, amount, reason):
        studentid = search.get()
        change = change.get()
        amount = amount.get()
        reason = reason.get()
        student = cursor.execute("SELECT * FROM Student WHERE student_id = ?", (studentid,)).fetchone()
        if studentid == '' or change == '' or amount == '' or reason == '':
            messagebox.showerror("","Please ensure all fields are filled.")
        else:
            student = cursor.execute("SELECT * FROM Student WHERE student_id = ?", (studentid,)).fetchone()
            if student:
                current_points = cursor.execute("SELECT total_points FROM Student WHERE student_id = ?", (studentid,)).fetchone()
                if change == "Adding":
                    if amount.isdigit():
                        new_points = int(current_points[0]) + int(amount)
                        date_created =  datetime.now().strftime('%Y-%m-%d')
                        cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_points, studentid))
                        cursor.execute("INSERT INTO House_points_record (student_id, teacher_id, points, date_created, reason) VALUES (?, ?, ?, ?, ?)", (studentid, teacher.teacher_id, new_points, date_created, reason,))
                        conn.commit()
                        messagebox.showinfo('Points Awarded',"Points successfully given to Student {}".format(studentid))
                    else:
                        messagebox.showerror('Invalid Input',"Amount must be a number")
                elif change == "Deducting":
                    if amount.isdigit():
                        new_points = int(current_points[0]) - int(amount)
                        if new_points < 0:
                            messagebox.showerror('',"Amount to be deducted is greater than what the student owns!")
                        else:
                            date_created =  datetime.now().strftime('%Y-%m-%d')
                            cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_points, studentid))
                            cursor.execute("INSERT INTO House_points_record (student_id, teacher_id, points, date_created, reason) VALUES (?, ?, ?, ?, ?)", (studentid, teacher.teacher_id, new_points, date_created, reason,))
                            conn.commit()
                            messagebox.showinfo('Points Deducted',"Points deducted from Student {}".format(studentid))
                    else:
                        messagebox.showerror('Invalid Input',"Amount must be a number")
            else:
                messagebox.showerror("", 'Student does not exist!')

def GetHouseID(selected_house):
    Houses = {"Gazelles": 1, "Oryxes": 2, "Foxes": 3, "Falcons": 4}
    houseId = Houses[selected_house]
    return houseId

def GetHouseColor(user):
    colors = {1: '#077A00', 2: '#C1A848', 3: '#000000', 4:  '#000B52'}
    color = colors[user.student_houseId]
    return color

def GetTokenId(token_name):
    tokens = {"Dress code exemption":1, "Cafeteria coupon":2, "One day off":3, "null":4}
    token_id = tokens[token_name]
    return  token_id

def GetTokenDesc(token_id):
    desc = cursor.execute("SELECT description FROM Token where token_id = ?",(token_id,)).fetchone()
    return desc[0]

def ApplyFilters(frame, class_filter, points_filter, house_filter):
    for widget in frame.winfo_children():
        widget.destroy()
    if house_filter.get() == "All":
        if class_filter.get() == "All":
            if points_filter.get() == "Highest - Lowest":
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id ORDER BY total_points DESC").fetchall()
            else:
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id ORDER BY total_points ASC").fetchall()
        else:
            if points_filter.get() == "Highest - Lowest":
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id AND Student.grade = ? ORDER BY total_points DESC", (class_filter.get(),)).fetchall()
            else:
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id AND Student.grade = ? ORDER BY total_points ASC", (class_filter.get(),)).fetchall()
    else:
        if class_filter.get() == "All":
            if points_filter.get() == "Highest - Lowest":
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id AND House.house_name = ? ORDER BY total_points DESC", (house_filter.get(),)).fetchall()
            else:
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id AND House.house_name = ? ORDER BY total_points ASC", (house_filter.get(),)).fetchall()
        else:
            if points_filter.get() == "Highest - Lowest":
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id AND Student.grade = ? AND House.house_name = ? ORDER BY total_points DESC", (class_filter.get(), house_filter.get(),)).fetchall()
            else:
                Records = cursor.execute("SELECT student_id, first_name, last_name, grade, total_points, house_name FROM Student, House WHERE Student.house_id = House.house_id AND Student.grade = ? AND House.house_name = ? ORDER BY total_points ASC", (class_filter.get(), house_filter.get(),)).fetchall()

    column1 = ctk.CTkButton(frame, text='Student ID', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
    column1.grid(row=0, column=0)

    column2 = ctk.CTkButton(frame, text='First Name', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
    column2.grid(row=0, column=1)
    
    column3 = ctk.CTkButton(frame, text='Last Name', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
    column3.grid(row=0, column=2)

    column4 = ctk.CTkButton(frame, text='Year Group', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
    column4.grid(row=0, column=3)

    column5 = ctk.CTkButton(frame, text='Total Points', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
    column5.grid(row=0, column=4)
    
    column6 = ctk.CTkButton(frame, text='House', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
    column6.grid(row=0, column=5)
    if Records != []:
        for i, record in enumerate(Records):
            for j, value in enumerate(record):
                button = ctk.CTkButton(frame, text=f'{value}', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=116, height=20, hover='disabled')
                button.grid(row=i+1, column=j)
    else:
        message = ctk.CTkButton(frame, text="No data", text_color='black',  font=('Franklin Gothic Condensed', 20), fg_color='light grey', border_width=2, width=500, height=100, hover='disabled')
        message.grid(row=5, column=0, columnspan=6)  

def ValidatePointAmount(text):
    max_chars = 4
    if len(text) > max_chars:
        return False
    if not text.isdigit() and text != "":
        return False
    return True

def RemoveWidgets():
    for widget in window.winfo_children():
        widget.destroy()

def Loginpage():
    RemoveWidgets()
    login_frame = ctk.CTkFrame(window, fg_color=default_color, border_width=50, border_color='grey')
    login_frame.pack(fill='both', expand=True)

    titleLabel = ctk.CTkLabel(login_frame, text='ASCS House Points', text_color='white', font=('Franklin Gothic Condensed', 60), fg_color=default_color)
    titleLabel.pack(pady=(75, 60))

    input_frame = ctk.CTkFrame(login_frame, fg_color=default_color)
    input_frame.pack()

    id_label = ctk.CTkLabel(input_frame, text='ID number', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color)
    id_label.grid(row=0, column=0)
    
    password_label = ctk.CTkLabel(input_frame, text='Password', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color)
    password_label.grid(row=1, column=0)

    Id_entry = ctk.CTkEntry(input_frame)
    Id_entry.grid(row=0, column=1, padx=5, pady=10)

    password_entry = ctk.CTkEntry(input_frame, show='*')
    password_entry.grid(row=1, column=1, padx=5, pady=10)

    selected_role = ctk.StringVar()
    options = ["Teacher", "Student"]
    rolecombobox = ctk.CTkComboBox(input_frame, values=options, state='readonly', variable=selected_role, font=('franklin gothic condensed', 20))
    rolecombobox.grid(row=2, column=0, columnspan=2, padx=10, pady=20)
    rolecombobox.set("Select a role")

    submit_btn = ctk.CTkButton(input_frame, text='Submit', command=lambda:User.login(selected_role, Id_entry, password_entry), font=('Franklin gothic condensed', 20), text_color='black',fg_color='white', border_width=3, border_color='dark grey')
    submit_btn.grid(row=3, columnspan=2, pady=10)
    
    createstudentacc_btn = ctk.CTkButton(input_frame, text='Create a student account', command=lambda:CreateStudentPage(), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    createstudentacc_btn.grid(row=4, column=1, padx=10, pady=15)
    
    createteacheracc_btn = ctk.CTkButton(input_frame, text='Create a teacher account', command=lambda:CreateTeacherPage(), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    createteacheracc_btn.grid(row=4, column=0, padx=10,pady=15)

def CreateStudentPage():
    RemoveWidgets()
    CreateAcc_frame = ctk.CTkFrame(window, fg_color=default_color, border_width=50, border_color='grey')
    CreateAcc_frame.pack(fill='both', expand=True)

    ctk.CTkLabel(CreateAcc_frame, text='Enter your details', text_color='white', font=('Franklin Gothic Condensed', 40), fg_color=default_color).pack(pady=(85, 25))

    entryframe = ctk.CTkFrame(CreateAcc_frame, fg_color=default_color)
    entryframe.pack()

    ctk.CTkLabel(entryframe, text='Enter your first name', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=0, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter your last name', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=0, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter an ID number', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Select your class', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter a password', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Select your House', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=2, padx=15, pady=20)

    EnterFirstName = ctk.CTkEntry(entryframe)
    EnterFirstName.grid(row=0, column=1)

    EnterLastName = ctk.CTkEntry(entryframe)
    EnterLastName.grid(row=0, column=3)

    EnterId = ctk.CTkEntry(entryframe)
    EnterId.grid(row=1, column=1)

    EnterPassword = ctk.CTkEntry(entryframe)
    EnterPassword.grid(row=2, column=1)

    selected_class = ctk.StringVar()
    year_groups = ["9A", "9B", "9C", "9D", "10A", "10B", "10C", "10D", "11A", "11B", "11C", "11D", "12A", "12B", "12C", "12D", "13A", "13B", "13C", "13D"]
    classcombobox = ctk.CTkComboBox(entryframe, values=year_groups,state='readonly', variable=selected_class)
    classcombobox.grid(row=1, column=3)
    classcombobox.set("Classes (9-13)")
    classcombobox.configure(font=('franklin gothic condensed', 15))

    selected_house = ctk.StringVar()
    houses = ["Gazelles", "Oryxes","Foxes","Falcons"]
    housecombobox = ctk.CTkComboBox(entryframe, values=houses, state='readonly', variable=selected_house)
    housecombobox.grid(row=2, column=3)
    housecombobox.configure(font=('franklin gothic condensed', 15))

    create_btn = ctk.CTkButton(entryframe, text='Create account', bg_color='black', command=lambda:Student.CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_class, selected_house.get(), year_groups), 
    font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    create_btn.grid(row=4, columnspan=4, pady=20)

    back_btn = ctk.CTkButton(entryframe, command=lambda:Loginpage(), text='Back', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    back_btn.grid(row=5, columnspan=4)

def CreateTeacherPage():
    RemoveWidgets()
    CreateAcc_frame = ctk.CTkFrame(window, fg_color=default_color, border_width=50, border_color='grey')
    CreateAcc_frame.pack(fill='both', expand=True)

    ctk.CTkLabel(CreateAcc_frame, text='Enter your details', text_color='white', font=('Franklin Gothic Condensed', 40), fg_color=default_color).pack(pady=(85, 25))

    entryframe = ctk.CTkFrame(CreateAcc_frame, fg_color=default_color)
    entryframe.pack()

    ctk.CTkLabel(entryframe, text='Enter your first name', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=0, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter your last name', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=0, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter an ID number', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Select your subject', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter a password', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=0, padx=15, pady=20)

    EnterFirstName = ctk.CTkEntry(entryframe)
    EnterFirstName.grid(row=0, column=1)

    EnterLastName = ctk.CTkEntry(entryframe)
    EnterLastName.grid(row=0, column=3)

    EnterId = ctk.CTkEntry(entryframe)
    EnterId.grid(row=1, column=1)

    EnterPassword = ctk.CTkEntry(entryframe)
    EnterPassword.grid(row=2, column=1)

    selected_subject = ctk.StringVar()
    subjects = ["Mathematics", "Physics", "Biology", "Chemistry", "Geography", "Psychology", "History", "Business", "Computer Science", "English"]
    subjectcombobox = ctk.CTkComboBox(entryframe, values=subjects,state='readonly', variable=selected_subject)
    subjectcombobox.grid(row=1, column=3)
    subjectcombobox.set("Subjects")
    subjectcombobox.configure(font=('franklin gothic condensed', 20))

    create_btn = ctk.CTkButton(entryframe, text='Create account', bg_color='black', command=lambda:Teacher.CreateNewTeacher(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_subject.get(), subjects), 
    font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    create_btn.grid(row=4, columnspan=4, pady=20)

    back_btn = ctk.CTkButton(entryframe, command=lambda:Loginpage(), text='Back', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    back_btn.grid(row=5, columnspan=4)

def TeacherHomePage(teacher):
    RemoveWidgets()
    TeacherName = str(teacher.teacher_first_name + ' ' + teacher.teacher_last_name)
    TeacherSubject = str(teacher.teacher_subject)

    TeacherHome_frame = ctk.CTkFrame(window, fg_color=default_color)
    TeacherHome_frame.pack(fill='both', expand=True)

    topbar_frame = ctk.CTkFrame(TeacherHome_frame, fg_color='light grey', border_width=2, border_color='black', width=800, height=60)
    topbar_frame.place(x=198, y=0)
        
    TeacherName_label = ctk.CTkButton(topbar_frame, text=TeacherName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    TeacherName_label.place(x=0, y=0)

    TeacherSubject_label = ctk.CTkButton(topbar_frame, text=TeacherSubject, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=150, height=60, hover='disabled')
    TeacherSubject_label.place(x=174)

    options_frame = ctk.CTkFrame(TeacherHome_frame, fg_color='#5F6262', border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    #manage_acc_btn = ctk.CTkButton(options_frame, command=lambda:TeacherAccManagementPage(), text='Account\nManagement', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    #manage_acc_btn.place(x=3, y=275)

    empty_btn = ctk.CTkButton(options_frame, text='', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    empty_btn.place(x=3, y=340)

    logout_btn = ctk.CTkButton(options_frame, command=lambda:logout(teacher), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    logout_btn.place(x=3, y=400)

    managestudents_btn = ctk.CTkButton(TeacherHome_frame, command=lambda:ManageStudentsPage(teacher, TeacherName, TeacherSubject), text='Add or Deduct\nhouse points', font=('Franklin Gothic Condensed', 22), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    managestudents_btn.place(x=675, y=125)

    viewstudents_btn = ctk.CTkButton(TeacherHome_frame, command=lambda:ViewStudentListPage(teacher, TeacherName, TeacherSubject), text='Student\nList', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    viewstudents_btn.place(x=375, y=375)

def Teacher_CommonWidgets(Mainframe, teacher, TeacherName, TeacherSubject):
    topbar_frame = ctk.CTkFrame(Mainframe, fg_color='light grey', border_width=2, border_color='black', width=800, height=60)
    topbar_frame.place(x=198, y=0)
        
    TeacherName_label = ctk.CTkButton(topbar_frame, text=TeacherName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    TeacherName_label.place(x=0, y=0)

    TeacherSubject_label = ctk.CTkButton(topbar_frame, text=TeacherSubject, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=150, height=60, hover='disabled')
    TeacherSubject_label.place(x=174)

    options_frame = ctk.CTkFrame(Mainframe, fg_color='#5F6262', border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    back_btn = ctk.CTkButton(options_frame, command=lambda:TeacherHomePage(teacher), text='Back', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', width=190, height=50, border_width=1)
    back_btn.place(x=3, y=500)

def ManageStudentsPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    ManageStudents_frame = ctk.CTkFrame(window, fg_color=default_color)
    ManageStudents_frame.pack(fill='both', expand=True)

    Teacher_CommonWidgets(ManageStudents_frame, teacher, TeacherName, TeacherSubject)

    Search_label = ctk.CTkLabel(ManageStudents_frame, text="Enter Student ID:", text_color='white', fg_color=default_color, font=('Franklin gothic condensed', 25))
    Search_label.place(x=385, y=135)

    search = ctk.CTkEntry(ManageStudents_frame, width=175, height=35, font=('franklin gothic condensed', 15))
    search.place(x=625, y=135)

    changepoints_label = ctk.CTkLabel(ManageStudents_frame, text="Adding or Deducting\nPoints? ", text_color='white', fg_color=default_color, font=('Franklin gothic condensed', 25))
    changepoints_label.place(x=385, y=195)

    change = ctk.StringVar()
    changes = ["","Adding","Deducting"]
    changecombobox = ctk.CTkComboBox(ManageStudents_frame, values=changes, state='readonly', variable=change, width=175, height=35, font=('franklin gothic condensed', 15))
    changecombobox.place(x=625, y=205)

    amount_label = ctk.CTkLabel(ManageStudents_frame, text='Amount', text_color='white', fg_color=default_color, font=('Franklin gothic condensed', 30))
    amount_label.place(x=435, y=275)

    validation_cmd = window.register(ValidatePointAmount)
    amount = ctk.CTkEntry(ManageStudents_frame, width=175, height=35, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd, "%P"))
    amount.place(x=625, y=275)

    reason_label = ctk.CTkLabel(ManageStudents_frame, text="Reason", text_color='white', fg_color=default_color, font=('Franklin gothic condensed', 20))
    reason_label.place(x=530, y=350)

    reason = ctk.CTkEntry(ManageStudents_frame, width=350, height=150)
    reason.place(x=400, y=385)

    submit_btn = ctk.CTkButton(ManageStudents_frame, text='Submit', command=lambda:Teacher.ChangeStudentPoints(teacher, search, change, amount, reason), font=('Franklin gothic condensed', 15), text_color='black', fg_color='white', border_width=3,border_color='dark grey')
    submit_btn.place(x=850, y=385)
    
def ViewStudentListPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    ViewStudentList_frame = ctk.CTkFrame(window, fg_color=default_color)
    ViewStudentList_frame.pack(fill='both', expand=True)
    
    Teacher_CommonWidgets(ViewStudentList_frame, teacher, TeacherName, TeacherSubject)

    class_filter = ctk.StringVar()
    year_groups = ["All", "9A", "9B", "9C", "9D", "10A", "10B", "10C", "10D", "11A", "11B", "11C", "11D", "12A", "12B", "12C", "12D", "13A", "13B", "13C", "13D"]
    class_filter_combobox = ctk.CTkComboBox(ViewStudentList_frame, values=year_groups,state='readonly', variable=class_filter, font=('franklin gothic condensed', 15))
    class_filter_combobox.place(x=645, y=150)
    class_filter_combobox.set("All")
    
    points_filter = ctk.StringVar()
    points_range = ["Highest - Lowest", "Lowest - Highest"]
    points_filter_combobox = ctk.CTkComboBox(ViewStudentList_frame, values=points_range, state='readonly', variable=points_filter, font=('franklin gothic condensed', 15))
    points_filter_combobox.place(x=445, y=150)
    points_filter_combobox.set("Highest - Lowest")

    house_filter = ctk.StringVar()
    houses = ["All", "Gazelles", "Oryxes", "Foxes", "Falcons"]
    house_filter_combobox = ctk.CTkComboBox(ViewStudentList_frame, values=houses, state='readonly', variable=house_filter, font=('franklin gothic condensed', 15))
    house_filter_combobox.place(x=245, y=150)
    house_filter_combobox.set("All")

    StudentList_frame = ctk.CTkScrollableFrame(ViewStudentList_frame, fg_color=default_color, bg_color=default_color, border_width=2, border_color='black', width=700, height=550)
    StudentList_frame.place(x=245, y=190)

    ApplyFilters(StudentList_frame, class_filter, points_filter, house_filter)

    apply_filters_btn = ctk.CTkButton(ViewStudentList_frame, text="Apply filters", command=lambda:ApplyFilters(StudentList_frame, class_filter, points_filter, house_filter), font=('Franklin gothic condensed', 15), text_color='black',fg_color='white', border_width=3, border_color='dark grey')
    apply_filters_btn.place(x=825, y=150)

def StudentHomePage(student):
    RemoveWidgets()
    StudentName = str(student.student_first_name + '  ' + student.student_last_name)
    StudentClass = str(student.student_grade)
    color = GetHouseColor(student)

    StudentHome_frame = ctk.CTkFrame(window, fg_color=default_color)
    StudentHome_frame.pack(fill='both', expand=True)

    topbar_frame = ctk.CTkFrame(StudentHome_frame, fg_color='light grey', border_width=2, border_color='black', width=800, height=60)
    topbar_frame.place(x=198, y=0)
    
    StudentName_label = ctk.CTkButton(topbar_frame, text=StudentName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    StudentName_label.place(x=0, y=0)

    StudentClass_label = ctk.CTkButton(topbar_frame, text=StudentClass, font=('Franklin Gothic Condensed', 21), text_color='black', fg_color='light grey', border_width=2, width=75, height=60, hover='disabled')
    StudentClass_label.place(x=174)

    StudentPoints_label = ctk.CTkButton(topbar_frame, text=("My total Points:  {}".format(student.student_points)), font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='light grey', border_width=2, width=300, height=60, hover='disabled')
    StudentPoints_label.place(x=500)

    options_frame = ctk.CTkFrame(StudentHome_frame, fg_color=color, border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    houseimage_btn = ctk.CTkButton(options_frame, text="(House image goes here)", text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    houseimage_btn.grid(row=0, pady=(50, 85))

    manage_acc_btn = ctk.CTkButton(options_frame, command=lambda:StudentAccManagementPage(student, StudentName, StudentClass, color), text='Account\nManagement', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    manage_acc_btn.grid(row=1, pady=(0, 20))

    check_notifs_btn = ctk.CTkButton(options_frame, text='Notifications', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    check_notifs_btn.grid(row=2, pady=(0, 20))

    logout_btn = ctk.CTkButton(options_frame, command=lambda:logout(student), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    logout_btn.grid(row=3, pady=(0, 20))

    sizer = ctk.CTkButton(options_frame, text='', fg_color=color, width=200, height=0, hover='disabled')
    sizer.grid(row=4, pady=(700, 0))

    Shop_btn = ctk.CTkButton(StudentHome_frame, command=lambda:TokenShopPage(student, StudentName, StudentClass, color), text='Token\nShop', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    Shop_btn.place(x=675, y=375)

    viewhistory_btn = ctk.CTkButton(StudentHome_frame, command=lambda:ViewPurchaseHistoryPage(student, StudentName, StudentClass, color), text='View\nPurchase\nHistory', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    viewhistory_btn.place(x=375, y=375)

def Student_CommonWidgets(Frame, student, StudentName, StudentClass, color):
    topbar_frame = ctk.CTkFrame(Frame, fg_color='light grey', border_width=2, border_color='black', width=800, height=60)
    topbar_frame.place(x=198, y=0)
    
    StudentName_label = ctk.CTkButton(topbar_frame, text=StudentName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    StudentName_label.place(x=0, y=0)

    StudentClass_label = ctk.CTkButton(topbar_frame, text=StudentClass, font=('Franklin Gothic Condensed', 21), text_color='black', fg_color='light grey', border_width=2, width=75, height=60, hover='disabled')
    StudentClass_label.place(x=174)

    StudentPoints_label = ctk.CTkButton(topbar_frame, text=("My total Points:  {}".format(student.student_points)), font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='light grey', border_width=2, width=300, height=60, hover='disabled')
    StudentPoints_label.place(x=500)

    options_frame = ctk.CTkFrame(Frame, fg_color=color, border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    houseimage_btn = ctk.CTkButton(options_frame, text="(House image goes here)", text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    houseimage_btn.grid(row=0, pady=(50, 85))

    manage_acc_btn = ctk.CTkButton(options_frame, command=lambda:StudentAccManagementPage(student, StudentName, StudentClass, color), text='Account\nManagement', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    manage_acc_btn.grid(row=1, pady=(0, 20))

    check_notifs_btn = ctk.CTkButton(options_frame, text='Notifications', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    check_notifs_btn.grid(row=2, pady=(0, 20))

    logout_btn = ctk.CTkButton(options_frame, command=lambda:logout(student), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    logout_btn.grid(row=3, pady=(0, 20))

    back_btn = ctk.CTkButton(options_frame, command=lambda:StudentHomePage(student), text='Back', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', width=180, height=50, border_width=1)
    back_btn.grid(row=4, pady=(0, 20))

    sizer = ctk.CTkButton(options_frame, text='', fg_color=color, width=200, height=0, hover='disabled')
    sizer.grid(row=5, pady=(700, 0))

def StudentAccManagementPage(student, StudentName, StudentClass,  color):
    RemoveWidgets()
    StudentAccManagement_frame = ctk.CTkFrame(window, fg_color=default_color)
    StudentAccManagement_frame.pack(fill='both', expand=True)

    Student_CommonWidgets(StudentAccManagement_frame, student, StudentName, StudentClass, color)

    ctk.CTkLabel(StudentAccManagement_frame, text ='First name', text_color='white', font=('Franklin Gothic Condensed', 20), fg_color=default_color).place(x=340, y=200)
    FirstName_entry =  ctk.CTkEntry(StudentAccManagement_frame)
    FirstName_entry.insert(0,student.student_first_name)
    FirstName_entry.place(x=440, y=200)

    ctk.CTkLabel(StudentAccManagement_frame, text ='Last name', text_color='white',font=('Franklin Gothic Condensed', 20), fg_color=default_color).place(x=340, y=225)
    LastName_entry = ctk.CTkEntry(StudentAccManagement_frame)
    LastName_entry.insert(0,student.student_last_name)
    LastName_entry.place(x=440, y=225)

    #!!Add more fields!! 

    ctk.CTkButton(StudentAccManagement_frame, text='Submit', command=lambda:student.UpdateStudentFields(FirstName_entry, LastName_entry, student)).place(x=500, y=300)

def ViewPurchaseHistoryPage(student, StudentName, StudentClass, color):
    RemoveWidgets()
    Records = cursor.execute("SELECT purchase_id, token_name, purchase_date FROM Purchase_token JOIN Token ON Token.token_id = Purchase_token.token_id").fetchall()
    PurchaseHistory_frame = ctk.CTkFrame(window, fg_color=default_color)
    PurchaseHistory_frame.pack(fill='both', expand=True)

    Student_CommonWidgets(PurchaseHistory_frame, student, StudentName, StudentClass, color)

    PageTitle_label = ctk.CTkButton(PurchaseHistory_frame, text='My Purchases', font=('Franklin Gothic Condensed', 50), text_color='black', fg_color='white', border_width=2, width=400, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=100)

    Records_frame = ctk.CTkScrollableFrame(window, fg_color=default_color, bg_color=default_color, border_width=2, border_color='black', width=700, height=450)
    Records_frame.place(x=245, y=190)

    column1 = ctk.CTkButton(Records_frame, text='Purchase ID', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='grey', border_width=2, width=233, height=20, hover='disabled')
    column1.grid(row=0, column=0)

    column2 = ctk.CTkButton(Records_frame, text='Token', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='grey', border_width=2, width=233, height=20, hover='disabled')
    column2.grid(row=0, column=1)
    
    column3 = ctk.CTkButton(Records_frame, text='Date Purchased', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='grey', border_width=2, width=233, height=20, hover='disabled')
    column3.grid(row=0, column=2)

    for i, record in enumerate(Records):
        for j, value in enumerate(record):
            button = ctk.CTkButton(Records_frame, text=f'{value}', text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=233, height=20, hover='disabled')
            button.grid(row=i+1, column=j)

def TokenShopPage(student, StudentName, StudentClass, color):
    RemoveWidgets()
    token_name = {1:"Dress code exemption", 2:"Cafeteria coupon", 3:"One day off", 4:"null"}
    Shop_frame = ctk.CTkFrame(window, fg_color=default_color)
    Shop_frame.pack(fill='both', expand=True)

    Student_CommonWidgets(Shop_frame, student, StudentName, StudentClass, color)

    PageTitle_label = ctk.CTkButton(Shop_frame, text='Token Shop', font=('Franklin Gothic Condensed', 45), text_color='black', fg_color='white', border_width=2, width=250, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=90)

    Token1_btn = ctk.CTkButton(Shop_frame, text='Dress Code\nExemption', command=lambda:ConfirmPurchaseWindow(student, token_name[1]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='white',height= 120, width=120, border_width=1)
    Token1_btn.place(x=400, y=190)

    Token1_desc = ctk.CTkLabel(Shop_frame, text=('{}'.format(GetTokenDesc(GetTokenId(token_name[1])))), text_color='white', font=('Franklin Gothic Condensed', 17), width=100, height=2)
    Token1_desc.place(x=335, y=315)

    Token2_btn = ctk.CTkButton(Shop_frame, text='Cafeteria\nCoupon', command=lambda:ConfirmPurchaseWindow(student, token_name[2]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='white',height= 120, width=120, border_width=1)
    Token2_btn.place(x=650, y=190)

    Token2_desc = ctk.CTkLabel(Shop_frame, text=('{}'.format(GetTokenDesc(GetTokenId(token_name[2])))), text_color='white', font=('Franklin Gothic Condensed', 17), width=100, height=2)
    Token2_desc.place(x=615, y=315)

    Token3_btn = ctk.CTkButton(Shop_frame, text='1 day\noff', command=lambda:ConfirmPurchaseWindow(student, token_name[3]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='white',height= 120, width=120, border_width=1)
    Token3_btn.place(x=400, y=390)

    Token3_desc = ctk.CTkLabel(Shop_frame, text=('{}'.format(GetTokenDesc(GetTokenId(token_name[3])))), text_color='white', font=('Franklin Gothic Condensed', 17), width=100, height=2)
    Token3_desc.place(x=365, y=515)

def ConfirmPurchaseWindow(student, token_name):
    token_id = GetTokenId(token_name)
    confirmPurchase_window = ctk.CTkToplevel(window, fg_color='light grey')
    confirmPurchase_window.geometry('750x150')
    confirmPurchase_window.title('Confirm purchase')
    confirmPurchase_window.resizable(False, False)

    ctk.CTkLabel(confirmPurchase_window, text=('Are you sure you want to purchase this "{}" token?').format(token_name), font=('Franklin Gothic Condensed', 17)).place(x=125, y=35)

    confirm_btn = ctk.CTkButton(confirmPurchase_window, text='Yes', command=lambda: PurchaseAndClose(confirmPurchase_window, student, token_id))
    confirm_btn.place(x=175, y=85)

    cancel_btn = ctk.CTkButton(confirmPurchase_window, text='No', command=confirmPurchase_window.destroy)
    cancel_btn.place(x=425, y=85)

def PurchaseAndClose(window, student, token_id):
    student.PurchaseToken(token_id)
    StudentHomePage(student)
    window.destroy()

def logout(user):
    del user
    RemoveWidgets()
    Loginpage()

if __name__ == "__main__":
    # from House_points_database import database
    # database()
    Loginpage()
    window.mainloop()
