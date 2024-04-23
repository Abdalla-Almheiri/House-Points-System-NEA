#Importing modules to be used in the program
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import sqlite3
import hashlib
from datetime import datetime, timedelta

#Connecting to the database and creating a cursor
conn = sqlite3.connect("House points")
cursor = conn.cursor()

#Creating a window using custom tkinter's CTk class 
window = ctk.CTk()
window.title('House Points System')
window.geometry('1100x650')
window.resizable(False, False)
ctk.set_appearance_mode("light")

default_color = '#262832'

class User:
    #Initializing a user object with password, first name, and last name
    def __init__(self, password, first_name, last_name):
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        
    def CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_class, selected_house, year_groups):
        #Retrieving values from entry widgets
        Id = EnterId.get()
        password = EnterPassword.get()
        first_name = EnterFirstName.get()
        last_name = EnterLastName.get()
        grade = selected_class.get()
        #Hashing the password entered by the user
        hashed = EncryptPassword(password)
        #Getting the house id from the name of the selected house
        houseId = GetHouseID(selected_house)
        #Checking if all fields were filled and all combobox options were selected
        if first_name == '' or last_name == '' or password == '' or Id == '' or grade not in year_groups:
            messagebox.showerror('',"Account not created, please properly fill in all your information to create an account.")
        else:
            if selected_house == '':
                messagebox.showerror('',"Account not created, please select a house.")
            else:
                if CheckID(Id) == True:
                    #Data inserted into the Student table
                    cursor.execute("INSERT INTO Student (student_ID, password_hash, first_name, last_name, grade, house_id, total_points, leaderboard_position, position_in_house) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)", (Id, hashed, first_name, last_name, grade, houseId, 0))
                    conn.commit()
                    #Inserting records into Owned_tokens table
                    for i in range(1,4):
                        cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, next_purchase_date) VALUES (?, ?, ?, NULL, NULL)", (Id, i, 0))
                        conn.commit()
                    messagebox.showinfo('',"Account created!")
                    #Clearing create account page and displaying login page
                    RemoveWidgets()
                    Loginpage()

    def CreateNewTeacher(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_subject, selected_title, subjects, titles):
        #Retrieving values from entry widgets and performing error checks
        id = EnterId.get()
        password = EnterPassword.get()
        first_name = EnterFirstName.get()
        last_name = EnterLastName.get()
        subject = selected_subject
        title = selected_title
        #Hashing the password entered by the user
        hashed = EncryptPassword(password)
        #Checking if all fields were filled and all combobox options were selected
        if first_name == '' or last_name== '' or id == '':
            messagebox.showerror('',"Account not created, please properly fill all fields to create an account")
        else:
            if subject not in subjects:
                messagebox.showerror('',"Account not created, please select the subject you teach")
            else:
                if title not in titles:
                    messagebox.showerror('',"Account not created, please select a title")
                else:
                    #Checking that the user entered a unique ID number
                    if CheckID(id) == True:
                        #Data inserted into the Teacher table
                        cursor.execute("INSERT INTO Teacher (teacher_id, password_hash, title, first_name, last_name, subject) VALUES (?, ?, ?, ?, ?, ?)", (id, hashed, title, first_name, last_name, subject,))
                        conn.commit()
                        messagebox.showinfo('',"Account created!")
                        #Clearing create account page and displaying login page
                        RemoveWidgets()
                        Loginpage() 


    def login(selected_role, Id_entry, password_entry):
            if selected_role.get() == 'Student':
                #Retrieving values entered by the student during login
                Id = Id_entry.get()
                password = password_entry.get()
                #Hashing password 
                hashed = EncryptPassword(password)
                #Retrieving the user's record from the database using the ID number
                user = cursor.execute("SELECT * FROM Student WHERE student_id = ?", (Id,)).fetchall()
                #Checking if the user exists
                if user:
                    #Checking if the hashed password entered by the user is the same hashed password as in the database record
                    if user[0][1] == hashed:
                        #Assigning retrieved data to variables
                        first_name = user[0][2]
                        last_name = user[0][3]
                        grade = user[0][4]
                        StudentHouse = user[0][5]
                        StudentPoints = user[0][6]
                        #Creating a student object and loading the student home page
                        student = Student(Id, password, first_name, last_name, grade, StudentHouse, StudentPoints)
                        S_HomePage(student)
                    else:
                        #Message for if the user types an incorrect password
                        messagebox.showerror("Login Failed", "Invalid Password.")
                else:
                    #Message for if the user tries to sign in to an account that doesn't exist
                    messagebox.showerror("Login Failed", "User does not exist! Would you like to sign up?")
                    
            #Code that is executed in case of the user selecting the student role during login
            elif selected_role.get() == 'Teacher':
                Id = Id_entry.get()
                password = password_entry.get()
                #Hashing password
                hashed = EncryptPassword(password)
                #Retrieving the user's record from the database using the ID number
                user = cursor.execute("SELECT * FROM Teacher WHERE teacher_id = ?", (Id,)).fetchall()
                #Checking if the user exists
                if user:
                    #Checking if the hashed password entered by the user is the same hashed password as the database record
                    if user[0][1] == hashed:
                        #Assigning retrieved data to variables
                        title = user[0][2]
                        first_name = user[0][3]
                        last_name = user[0][4]
                        subject = user[0][5]
                        #Creating a student object and loading the student home page
                        teacher = Teacher(Id, password, title, first_name, last_name, subject)
                        T_HomePage(teacher)
                    else:
                        #Message for if the user types an incorrect password
                        messagebox.showerror("Login Failed", "Invalid Password.")
                else:
                    #Message for if the user tries to sign in to an account that doesn't exist
                    messagebox.showerror("Login Failed", "User does not exist! Would you like to sign up?")
            else:
                #Message for if user doesn't select a role
                messagebox.showerror("Login Failed", "Select Student or Teacher")

class Student(User):
    #Initializing subclass and using constructor method to inherit values from User Class
    def __init__(self, Id, password, first_name, last_name, grade, StudentHouse, StudentPoints):
        super().__init__(password, first_name, last_name)
        self.student_id = Id
        self.student_password = password
        self.student_first_name = first_name
        self.student_last_name = last_name
        self.student_grade = grade
        self.student_houseId = StudentHouse
        self.student_points = StudentPoints

    def CheckNotifs(self):
        #Checking if student has any unseen notifications
        notifs = cursor.execute("SELECT * FROM Notifs WHERE student_id = ? AND not_seen = 1", (self.student_id,)).fetchall()
        if notifs != []:
            #In cases where student has only one notification
            if len(notifs) < 2:
                    #Setting variables
                    record_id = notifs[0][0]
                    change = notifs[0][2]
                    #Getting number of points and identifying the change in points to display in the notification
                    points = cursor.execute("SELECT points FROM House_points_record WHERE record_id = ?", (record_id,)).fetchone()
                    if change == 'added':
                        messagebox.showinfo('Notification',"{} points where {} to your account!".format(points[0], change))
                    elif change == 'deducted':
                        messagebox.showinfo('Notification',"{} points where {} from your account!".format(points[0], change))
                    #Updating table to show that student has seen the notification
                    cursor.execute("UPDATE Notifs SET not_seen = 0 WHERE record_id = ?", (record_id,))
                    conn.commit()
            #In cases where student has two or more notifications
            elif len(notifs) >= 2:            
                messagebox.showinfo('Notification', "You have {} unchecked notifications".format(len(notifs)))
            else:
                pass
        else:
            pass

    def ShowNotifs(self):
        #Selecting unseen notifications
        notifs = cursor.execute("SELECT * FROM Notifs WHERE student_id = ? AND not_seen = 1", (self.student_id,)).fetchall()
        #Cases where Student has unseen notifs
        if notifs != []:
            for i, record in enumerate(notifs):
                    #Code executed for every unseen notification record
                    record_id = record[0]
                    change = record[2]
                    points = cursor.execute("SELECT points FROM House_points_record WHERE record_id = ?", (record_id,)).fetchone()
                    if change == 'added':
                        messagebox.showinfo('Notification',"{} points where {} to your account!".format(points[0], change))
                    elif change == 'deducted':
                        messagebox.showinfo('Notification',"{} points where {} from your account!".format(points[0], change))
                    #Updating table to show that student has seen the notification
                    cursor.execute("UPDATE Notifs SET not_seen = 0 WHERE record_id = ?", (record_id,))
                    conn.commit()
        else:
            messagebox.showinfo('Notification',"You have no new notifications.")


    def UpdateFields(self, Id_entry, FirstName_entry, LastName_entry, selected_class, selected_house, student):
        #Function that updates values in a student's account
        NewId = Id_entry.get()
        NewFirstName = FirstName_entry.get()
        NewLastName = LastName_entry.get()
        NewClass = selected_class
        NewHouse = GetHouseID(selected_house)
        if NewId == student.student_id and NewFirstName == student.student_first_name and NewLastName == student.student_last_name and NewClass == student.student_grade and NewHouse == student.student_houseId:
            messagebox.showinfo('', "No fields changed")
        else:
            try:
                cursor.execute("UPDATE Student SET student_id = ?, first_name = ?, last_name = ?, grade = ?, house_id = ? WHERE student_id = ?", (NewId, NewFirstName, NewLastName, NewClass, NewHouse, self.student_id))
                conn.commit()
                self.student_id = NewId
                self.student_first_name = NewFirstName
                self.student_last_name = NewLastName
                self.student_grade = NewClass
                self.student_houseId = NewHouse
                messagebox.showinfo('',"Your account details have been updated successfully!")
                RemoveWidgets()
                S_HomePage(student)
            except:
                messagebox.showerror('Invalid input', "ID number already in use")

    def UpdatePassword(self, Entry1, Entry2, window):
        #Seperate function for updating a student's password for the sake of security
        if Entry1 == Entry2:
            if Entry1 == self.student_password:
                messagebox.showinfo('', "Password not updated, your new password cannot be the same as your current password.")
                window.destroy()
                S_HomePage(self)
            else:
                hashed = EncryptPassword(Entry1)
                cursor.execute("UPDATE Student SET password_hash = ? WHERE student_id = ?", (hashed, self.student_id,))
                conn.commit()
                messagebox.showinfo('', "Password successfully updated!")
                window.destroy()
                S_HomePage(self)
        else:
            messagebox.showerror('', "Passwords entered in fields do not match, password not updated.")

    def PurchaseToken(self, token_id):
            #Function that allows a student to purchase a token provided certain criteria are met 
            purchase_date =  datetime.now().strftime('%Y-%m-%d')
            point_cost = cursor.execute("SELECT point_cost FROM Token WHERE token_id = ?", (token_id,)).fetchone()
            new_sum = self.student_points - point_cost[0]
            allowed_purchase_date = cursor.execute("SELECT next_purchase_date FROM Owned_tokens WHERE student_id = ? AND token_id = ?", (self.student_id, token_id,)).fetchone()
            #
            if allowed_purchase_date[0] is None:
                allowed_purchase_date = purchase_date
            else:
                allowed_purchase_date = allowed_purchase_date[0]
            if new_sum < 0 or self.student_points < point_cost[0]:
                messagebox.showerror('Cannot Buy Token',"Insufficient amount of points, no points deducted")
            else:
                if purchase_date >= str(allowed_purchase_date):
                    if token_id == 1:
                        next_purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d") + timedelta(days=60)
                    elif token_id == 2:
                        next_purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d") + timedelta(days=30)
                    elif token_id == 3:
                        next_purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d") + timedelta(days=90)
                    cursor.execute("INSERT INTO Purchase_token (student_id, token_id, purchase_date) VALUES (?, ?, ?);", (self.student_id, token_id, purchase_date))
                    intial_quantity = cursor.execute("SELECT quantity FROM Owned_tokens WHERE student_id = ? AND token_id = ?", (self.student_id, token_id,)).fetchone()
                    new_quantity = intial_quantity[0] + 1
                    cursor.execute("UPDATE Owned_tokens SET quantity = ?, last_purchase_date = ?, next_purchase_date = ? WHERE student_id = ? AND token_id = ?", (new_quantity, purchase_date, datetime.strftime(next_purchase_date, "%Y-%m-%d"), self.student_id, token_id,))
                    cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_sum, self.student_id,))
                    conn.commit()
                    messagebox.showinfo('',"Token purchased!")
                    self.student_points = new_sum
                else:
                    messagebox.showerror('Cannot Buy Token',f'You cannot purchase this token until {allowed_purchase_date}')

class Teacher(User):
    #Initializing subclass and using constructor method to inherit values from User Class
    def __init__(self, Id, password, title, first_name, last_name, subject):
        super().__init__(password, first_name, last_name)
        self.teacher_id = Id
        self.teacher_password = password
        self.teacher_title = title
        self.teacher_first_name = first_name
        self.teacher_last_name = last_name
        self.teacher_subject = subject

    def UpdateFields(self, Id_entry, selected_title, FirstName_entry, LastName_entry, selected_subject, teacher):
        NewId = Id_entry.get()
        NewTitle = selected_title
        NewFirstName = FirstName_entry.get()
        NewLastName = LastName_entry.get()
        NewSubject = selected_subject
        if NewId == teacher.teacher_id and NewTitle == teacher.teacher_title and NewFirstName == teacher.teacher_first_name and NewLastName == teacher.teacher_last_name and NewSubject == teacher.teacher_subject:
            messagebox.showinfo('', "No fields changed")
        else:
            cursor.execute("UPDATE Teacher SET teacher_id = ?, title = ?, first_name = ?, last_name = ?, subject = ? WHERE teacher_id = ?", (NewId, NewTitle, NewFirstName, NewLastName, NewSubject, self.teacher_id))
            conn.commit()
            self.teacher_id = NewId
            self.teacher_title = NewTitle
            self.teacher_first_name = NewFirstName
            self.teacher_last_name = NewLastName
            self.teacher_subject = NewSubject
            messagebox.showinfo('',"Successfully updated account details")
            RemoveWidgets()
            T_HomePage(teacher)

    def UpdatePassword(self, Entry1, Entry2, window):
        if Entry1 == Entry2:
            if Entry1 == self.teacher_password:
                messagebox.showinfo('', "Password not updated, your new password cannot be the same as your current password")
                window.destroy()
                T_HomePage(self)
            else:
                hashed = EncryptPassword(Entry1)
                cursor.execute("UPDATE Teacher SET password_hash = ? WHERE teacher_id = ?", (hashed, self.teacher_id,))
                conn.commit()
                messagebox.showinfo('', "Password successfully updated!")
                window.destroy()
                T_HomePage(self)
        else:
            messagebox.showerror('', "Passwords entered in fields do not match, password not updated")
            
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
                        student_houseid = cursor.execute("SELECT house_id FROM student WHERE student_id = ?", (studentid,)).fetchone()
                        current_house_totalpoints = cursor.execute("SELECT house_totalpoints FROM House WHERE house_id = ?", (student_houseid[0],)).fetchone()
                        new_housetotal = int(current_house_totalpoints[0] + int(amount))
                        new_points = int(current_points[0]) + int(amount)
                        positive = str('+'+amount)
                        date_created =  datetime.now().strftime('%Y-%m-%d')
                        cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_points, studentid,))
                        cursor.execute("INSERT INTO House_points_record (student_id, teacher_id, points, date_created, reason) VALUES (?, ?, ?, ?, ?)", (studentid, teacher.teacher_id, positive, date_created, reason,))
                        cursor.execute("INSERT INTO Notifs (student_id, change, not_seen) VALUES (?, ?, ?)", (studentid, 'added', 1))
                        cursor.execute("UPDATE House SET house_totalpoints = ? WHERE house_id = ?", (new_housetotal, student_houseid[0],))
                        conn.commit()
                        messagebox.showinfo('Points Awarded',"{} points successfully given to student {}".format(amount, studentid))
                        T_HomePage(teacher)
                    else:
                        messagebox.showerror('Invalid Input',"Amount must be a number")
                elif change == "Deducting":
                    if amount.isdigit():
                        new_points = int(current_points[0]) - int(amount)
                        if new_points < 0:
                            messagebox.showerror('',"Amount to be deducted is greater than what the student owns!")
                        else:
                            negative = str('-'+amount)
                            date_created =  datetime.now().strftime('%Y-%m-%d')
                            cursor.execute("UPDATE Student SET total_points = ? WHERE student_id = ?", (new_points, studentid))
                            cursor.execute("INSERT INTO House_points_record (student_id, teacher_id, points, date_created, reason) VALUES (?, ?, ?, ?, ?)", (studentid, teacher.teacher_id, negative, date_created, reason,))
                            cursor.execute("INSERT INTO Notifs (student_id, change, not_seen) VALUES (?, ?, ?)", (studentid, 'deducted', 1))
                            conn.commit()
                            messagebox.showinfo('Points Deducted',"{} points deducted from student {}".format(amount, studentid))
                            T_HomePage(teacher)
                    else:
                        messagebox.showerror('Invalid Input',"Amount must be a number")
            else:
                messagebox.showerror("", 'Student does not exist!')

#Functions that serve repeated purposes throughout the system
def EncryptPassword(password):    
    #Password encryption algorithm that hashes character strings
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    encrypted_password = sha256_hash.hexdigest()
    return encrypted_password

def GetHouseID(selected_house):
    #Retrieves the house_id
    houseId = cursor.execute("SELECT house_id FROM House WHERE house_name = ?", (selected_house,)).fetchone()
    return houseId[0]

def GetHouseName(house_id):
    #Retrieves a the name of a student's house from the House table in the database
    house_name = cursor.execute("SELECT house_name FROM House WHERE house_id = ?", (house_id,)).fetchone()
    return house_name[0]

def GetHouseColor(student):
    #Retrieves a student's house color using the student's house_id 
    colors = {1: '#077A00', 2: '#C1A848', 3: '#000000', 4:  '#000B52'}
    color = colors[student.student_houseId]
    return color

def GetHouseLogo(student):
    #Retrieves the logo of a student's house depending on the student's house_id
    if student.student_houseId == 1:
        img = ctk.CTkImage(light_image=Image.open("ASCS_Gazelle_Logo.jpg"), size=(150, 150))
    elif student.student_houseId == 2:
        img = ctk.CTkImage(light_image=Image.open("ASCS_Oryx_Logo.jpg"), size=(125, 125))
    elif student.student_houseId == 3:
        img = ctk.CTkImage(light_image=Image.open("ASCS_Foxes_Logo.jpg"), size=(150, 150))
    elif student.student_houseId == 4:
        img = ctk.CTkImage(light_image=Image.open("ASCS_Falcons_Logo.jpg"), size=(150, 150))
    return img

def GetTokenId(token_name):
    #Retrieves the token ID of a token using its corresponding token name
    tokens = {"Dress code exemption":1, "Cafeteria coupon":2, "One day off":3, "null":4}
    token_id = tokens[token_name]
    return  token_id

def GetTokenDesc(token_id):
    #Retrieves the descriptions of each token using their token_ids
    desc = cursor.execute("SELECT description FROM Token where token_id = ?",(token_id,)).fetchone()
    return desc[0]

def CheckID(Id):
    #Checks the uniqueness of an ID entered by the user during account creation
    student_id = cursor.execute("SELECT student_id FROM Student WHERE student_id = ?", (Id,)).fetchone()
    teacher_id = cursor.execute("SELECT teacher_id FROM Teacher WHERE teacher_id = ?", (Id,)).fetchone()
    if student_id or teacher_id:
        messagebox.showerror('Invalid ID', 'This ID is already being used by another user.')
        return False
    else:
        return True
    
def RemoveWidgets():
    #Function that is used to clear widgets from the screen by cycling through and destroying all the widgets in the window 
    for widget in window.winfo_children():
        widget.destroy()

#Validation for some of the entry widgets
def ValidatePointAmount(text):
    #Sets a limit for the number of characters allowed in the entry widget and allows only numbers to be typed into the entry
    max_chars = 4
    if len(text) > max_chars:
        return False
    if not text.isdigit() and text != "":
        return False
    return True

def IdEntryValidation(text):
    #Same as ValidatePointAmount however this function is used as validation for the ID number
    max_chars = 10
    if len(text) > max_chars:
        return False
    if not text.isdigit() and text != "":
        return False
    return True

def LetterValidation(text):
    #Validation for entry widgets for first name and last name
    max_chars = 15
    if len(text) > max_chars:
        return False
    if not text.isalpha() and text != "":
        return False
    return True

#Login     
def Loginpage():
    #Calling the RemoveWidgets function to remove any widgets that may be on the window for the contents of the next page to be displayed
    RemoveWidgets()
    #Creating a frame to place the login page widgets  
    login_frame = ctk.CTkFrame(window, fg_color=default_color, border_width=50, border_color='grey')
    login_frame.pack(fill='both', expand=True)
    #Title widget 
    titleLabel = ctk.CTkLabel(login_frame, text='ASCS House Points', text_color='white', font=('Franklin Gothic Condensed', 80), fg_color=default_color)
    titleLabel.pack(pady=(100, 60))
    #Subframe within main frame
    input_frame = ctk.CTkFrame(login_frame, fg_color=default_color)
    input_frame.pack()
    #Widgets
    ctk.CTkLabel(input_frame, text='ID number', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=0, column=0)
    ctk.CTkLabel(input_frame, text='Password', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=1, column=0)
    #Entry widgets that take values for login functions
    validation_cmd = window.register(IdEntryValidation)
    Id_entry = ctk.CTkEntry(input_frame, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd, "%P"))
    Id_entry.grid(row=0, column=1, pady=10)

    password_entry = ctk.CTkEntry(input_frame, font=('franklin gothic condensed', 15), show='*')
    password_entry.grid(row=1, column=1, pady=10)

    selected_role = ctk.StringVar()
    options = ["Teacher", "Student"]
    rolecombobox = ctk.CTkComboBox(input_frame, values=options, state='readonly', variable=selected_role, font=('franklin gothic condensed', 20))
    rolecombobox.grid(row=2, column=0, columnspan=2, padx=10, pady=20)
    rolecombobox.set("Select a role")

    submit_btn = ctk.CTkButton(input_frame, text='Submit', command=lambda: User.login(selected_role, Id_entry, password_entry), font=('Franklin gothic condensed', 20), text_color='black',fg_color='white', border_width=3, border_color='dark grey')
    submit_btn.grid(row=3, columnspan=2, pady=10)
    #Options for creating either a student or teacher account
    createstudentacc_btn = ctk.CTkButton(input_frame, text='Create a student account', command=lambda: CreateStudentPage(), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    createstudentacc_btn.grid(row=4, column=1, padx=15, pady=15)

    createteacheracc_btn = ctk.CTkButton(input_frame, text='Create a teacher account', command=lambda: CreateTeacherPage(), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    createteacheracc_btn.grid(row=4, column=0, padx=15,pady=15)

def CreateStudentPage():
    #Clearing widgets from previous page
    RemoveWidgets()
    #Creating the page frame
    CreateAcc_frame = ctk.CTkFrame(window, fg_color=default_color, border_width=50, border_color='grey')
    CreateAcc_frame.pack(fill='both', expand=True)
    #Label widgets
    ctk.CTkLabel(CreateAcc_frame, text='Create a Student account', text_color='white', font=('Franklin Gothic Condensed', 60), fg_color=default_color).pack(pady=(85, 0))
    ctk.CTkLabel(CreateAcc_frame, text='Enter your details', text_color='white', font=('Franklin Gothic Condensed', 40), fg_color=default_color).pack(pady=25)
    #Creating a subframe for the entry widgets 
    entryframe = ctk.CTkFrame(CreateAcc_frame, fg_color=default_color)
    entryframe.pack()

    ctk.CTkLabel(entryframe, text='Enter your first name', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=0, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter your last name', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=0, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter an ID number', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Select your class', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter a password', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Select your House', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=2, padx=15, pady=20)
    #Widgets for entering details
    validation_cmd1 = window.register(LetterValidation)
    EnterFirstName = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd1, "%P"))
    EnterFirstName.grid(row=0, column=1)

    EnterLastName = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd1, "%P"))
    EnterLastName.grid(row=0, column=3)

    validation_cmd2 = window.register(IdEntryValidation)
    EnterId = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd2, "%P"))
    EnterId.grid(row=1, column=1)

    EnterPassword = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15))
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
    housecombobox.set("House")
    housecombobox.configure(font=('franklin gothic condensed', 15))
    #Create button that executes the CreateNewStudent function in the User class 
    create_btn = ctk.CTkButton(entryframe, text='Create account', bg_color='black', command=lambda:User.CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_class, selected_house.get(), year_groups), 
    font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    create_btn.grid(row=4, columnspan=4, pady=20)
    #Back button that returns the user to the login page
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
    ctk.CTkLabel(entryframe, text='Select your subject', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=2, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Enter a password', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=2, column=0, padx=15, pady=20)
    ctk.CTkLabel(entryframe, text='Select your title', text_color='white', font=('Franklin Gothic Condensed', 25), fg_color=default_color).grid(row=1, column=2, padx=15, pady=20)

    validation_cmd1 = window.register(LetterValidation)
    EnterFirstName = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd1, "%P"))
    EnterFirstName.grid(row=0, column=1)

    EnterLastName = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd1, "%P"))
    EnterLastName.grid(row=0, column=3)

    validation_cmd2 = window.register(IdEntryValidation)
    EnterId = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15), validate="key", validatecommand=(validation_cmd2, "%P"))
    EnterId.grid(row=1, column=1)

    EnterPassword = ctk.CTkEntry(entryframe, font=('franklin gothic condensed', 15))
    EnterPassword.grid(row=2, column=1)

    selected_subject = ctk.StringVar()
    subjects = ["Mathematics", "Physics", "Biology", "Chemistry", "Geography", "Psychology", "History", "Business", "Computer Science", "English"]
    subjectcombobox = ctk.CTkComboBox(entryframe, values=subjects,state='readonly', variable=selected_subject)
    subjectcombobox.grid(row=2, column=3)
    subjectcombobox.set("Subject")
    subjectcombobox.configure(font=('franklin gothic condensed', 20))

    selected_title = ctk.StringVar()
    titles = ["Mr.", "Ms.", "Mrs."]
    titlecombobox = ctk.CTkComboBox(entryframe, values=titles,state='readonly', variable=selected_title)
    titlecombobox.grid(row=1, column=3)
    titlecombobox.set("Mr/Ms/Mrs")
    titlecombobox.configure(font=('franklin gothic condensed', 20))

    create_btn = ctk.CTkButton(entryframe, text='Create account', bg_color='black', command=lambda:User.CreateNewTeacher(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_subject.get(), selected_title.get(), subjects, titles), 
    font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    create_btn.grid(row=4, columnspan=4, pady=20)

    back_btn = ctk.CTkButton(entryframe, command=lambda:Loginpage(), text='Back', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    back_btn.grid(row=5, columnspan=4)

def T_HomePage(teacher):
    RemoveWidgets()
    TeacherName = str(teacher.teacher_title + ' ' + teacher.teacher_first_name + ' ' + teacher.teacher_last_name)
    TeacherSubject = str(teacher.teacher_subject)

    TeacherHome_frame = ctk.CTkFrame(window, fg_color=default_color)
    TeacherHome_frame.pack(fill='both', expand=True)

    PageTitle = ctk.CTkButton(TeacherHome_frame, text='Home', font=('Franklin Gothic Condensed', 45), text_color='black', fg_color='white', border_width=2, width=250, height=50, hover='disabled')
    PageTitle.place(x=250, y=75)

    buttons_frame = ctk.CTkFrame(TeacherHome_frame, fg_color=default_color)
    buttons_frame.place(x=300, y=150)

    topbar_frame = ctk.CTkFrame(TeacherHome_frame, fg_color='light grey', border_width=2, border_color='black', width=900, height=60)
    topbar_frame.place(x=198, y=0)
        
    TeacherName_label = ctk.CTkButton(topbar_frame, text=TeacherName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=60, hover='disabled')
    TeacherName_label.place(x=0, y=0)

    TeacherSubject_label = ctk.CTkButton(topbar_frame, text=TeacherSubject, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=150, height=60, hover='disabled')
    TeacherSubject_label.place(x=199)

    options_frame = ctk.CTkFrame(TeacherHome_frame, fg_color='#5F6262', border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    logo_img = ctk.CTkImage(light_image=Image.open("ASCS_LOGO.png"), size=(150, 150))
    logo_btn  = ctk.CTkButton(options_frame, image=logo_img, text='', fg_color='white', width=160, height=150, border_width=1, hover='disabled')
    logo_btn.grid(row=0, pady=(50, 85))
    
    acc_details_btn = ctk.CTkButton(options_frame, text='Account Details', command=lambda:T_AccountDetailsPage(teacher, TeacherName, TeacherSubject), font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    acc_details_btn.grid(row=1, pady=(0, 20))

    empty_btn = ctk.CTkButton(options_frame, text='', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    empty_btn.grid(row=2, pady=(0, 20))

    logout_btn = ctk.CTkButton(options_frame, command=lambda:ConfirmLogout(teacher), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    logout_btn.grid(row=3, pady=(0, 20))

    sizer = ctk.CTkButton(options_frame, text='', fg_color='#5F6262', width=200, height=0, hover='disabled')
    sizer.grid(row=4, pady=(700, 0))

    Leaderboard_btn = ctk.CTkButton(buttons_frame, command=lambda:T_LeaderboardsPage(teacher, TeacherName, TeacherSubject), text='Leaderboard', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    Leaderboard_btn.grid(row=0, column=0, padx=25, pady=25)

    addOrdeductpoints_btn = ctk.CTkButton(buttons_frame, command=lambda:T_AddOrDeductPointsPage(teacher, TeacherName, TeacherSubject), text='Add or Deduct\nhouse points', font=('Franklin Gothic Condensed', 22), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    addOrdeductpoints_btn.grid(row=0, column=1, padx=100, pady=50)

    studentlist_btn = ctk.CTkButton(buttons_frame, command=lambda:T_StudentListPage(teacher, TeacherName, TeacherSubject), text='Student\nList', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    studentlist_btn.grid(row=1, column=0, padx=100, pady=50)

    pointrecord_btn = ctk.CTkButton(buttons_frame, command=lambda:T_StudentRecordsPage(teacher, TeacherName, TeacherSubject), text='Student\nHouse Point\nRecords', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    pointrecord_btn.grid(row=1, column=1, padx=100, pady=50)

def T_CommonWidgets(Frame, teacher, TeacherName, TeacherSubject):
    topbar_frame = ctk.CTkFrame(Frame, fg_color='light grey', border_width=2, border_color='black', width=900, height=60)
    topbar_frame.place(x=198, y=0)
        
    TeacherName_label = ctk.CTkButton(topbar_frame, text=TeacherName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    TeacherName_label.place(x=0, y=0)

    TeacherSubject_label = ctk.CTkButton(topbar_frame, text=TeacherSubject, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=150, height=60, hover='disabled')
    TeacherSubject_label.place(x=174)

    options_frame = ctk.CTkFrame(Frame, fg_color='#5F6262', border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    logo_img = ctk.CTkImage(light_image=Image.open("ASCS_LOGO.png"), size=(150, 150))
    logo_btn  = ctk.CTkButton(options_frame, image=logo_img, text='', fg_color='white', width=160, height=150, border_width=1, hover='disabled')
    logo_btn.grid(row=0, pady=(50, 85))
    
    acc_details_btn = ctk.CTkButton(options_frame, text='Account Details', command=lambda:T_AccountDetailsPage(teacher, TeacherName, TeacherSubject), font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    acc_details_btn.grid(row=1, pady=(0, 20))

    empty_btn = ctk.CTkButton(options_frame, text='', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    empty_btn.grid(row=2, pady=(0, 20))

    logout_btn = ctk.CTkButton(options_frame, command=lambda:ConfirmLogout(teacher), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    logout_btn.grid(row=3, pady=(0, 20))

    sizer = ctk.CTkButton(options_frame, text='', fg_color='#5F6262', width=200, height=0, hover='disabled')
    sizer.grid(row=4, pady=(700, 0))

    home_btn = ctk.CTkButton(options_frame, command=lambda:T_HomePage(teacher), text='Home', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', width=190, height=50, border_width=1)
    home_btn.place(x=3, y=500)

def T_AccountDetailsPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    T_AccountDetailsPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    T_AccountDetailsPage_frame.pack(fill='both', expand=True)
    
    T_CommonWidgets(T_AccountDetailsPage_frame, teacher, TeacherName, TeacherSubject)

    PageTitle = ctk.CTkButton(T_AccountDetailsPage_frame, text='Account Details', font=('Franklin Gothic Condensed', 45), text_color='black', fg_color='white', border_width=2, width=250, height=50, hover='disabled')
    PageTitle.place(x=250, y=125)

    details_frame = ctk.CTkFrame(T_AccountDetailsPage_frame, fg_color=default_color)
    details_frame.place(x=250, y=250)

    ctk.CTkLabel(details_frame, text ='First name', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=0, column=0, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Last name', text_color='white',font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=0, column=2, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='ID number', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=1, column=0, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Password', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=2, column=0, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Title', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=1, column=2, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Subject', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=2, column=2, padx=30, pady=20)

    FirstName_entry =  ctk.CTkEntry(details_frame, font=('franklin gothic condensed', 20))
    FirstName_entry.insert(0, teacher.teacher_first_name)
    FirstName_entry.grid(row=0, column=1, padx=30, pady=20)

    LastName_entry = ctk.CTkEntry(details_frame, font=('franklin gothic condensed', 20))
    LastName_entry.insert(0, teacher.teacher_last_name)
    LastName_entry.grid(row=0, column=3, padx=30, pady=20) 

    Id_entry = ctk.CTkEntry(details_frame, font=('franklin gothic condensed', 20))
    Id_entry.insert(0, teacher.teacher_id)
    Id_entry.grid(row=1, column=1, padx=30, pady=20)

    password_box = ctk.CTkButton(details_frame, text="********", text_color='black', font=('franklin gothic condensed', 17), fg_color='white', border_width=3, border_color='dark grey', width=150, height=17, hover='disabled')
    password_box.grid(row=2, column=1, padx=30, pady=20)

    selected_title = ctk.StringVar()
    titles = ["Mr.", "Ms.", "Mrs."]
    titlecombobox = ctk.CTkComboBox(details_frame, values=titles,state='readonly', variable=selected_title)
    titlecombobox.grid(row=1, column=3, padx=30, pady=20)
    titlecombobox.set(teacher.teacher_title)
    titlecombobox.configure(font=('franklin gothic condensed', 20))

    selected_subject = ctk.StringVar()
    subjects = ["Mathematics", "Physics", "Biology", "Chemistry", "Geography", "Psychology", "History", "Business", "Computer Science", "English"]
    subjectscombobox = ctk.CTkComboBox(details_frame, values=subjects, state='readonly', variable=selected_subject)
    subjectscombobox.grid(row=2, column=3, padx=30, pady=20)
    subjectscombobox.set(teacher.teacher_subject)
    subjectscombobox.configure(font=('franklin gothic condensed', 20))    

    update_password_btn = ctk.CTkButton(details_frame, text='Update Password', command=lambda:T_UpdatePasswordPage(teacher), text_color='black', font=('franklin gothic condensed', 20), fg_color='white', border_width=3, border_color='dark grey')
    update_password_btn.grid(row=3, column=1, padx=30, pady=20)

    update_details_btn = ctk.CTkButton(details_frame, text='Update Details', command=lambda:teacher.UpdateFields(Id_entry, selected_title.get(), FirstName_entry, LastName_entry, selected_subject.get(), teacher), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    update_details_btn.grid(row=3, column=2, padx=30, pady=20)

def T_UpdatePasswordPage(teacher):
    password_window = ctk.CTkToplevel(window, fg_color=default_color)
    password_window.geometry('400x350')
    password_window.title('Update Password')
    password_window.attributes('-topmost', True)
    password_window.resizable(False, False)

    ctk.CTkLabel(password_window, text='Enter your new password', font=('Franklin Gothic Condensed', 35), text_color='white', fg_color=default_color).pack(pady=30)

    frame = ctk.CTkFrame(password_window, fg_color=default_color)
    frame.pack()

    ctk.CTkLabel(frame, text='New password', font=('Franklin Gothic Condensed', 25), text_color='white', fg_color=default_color).grid(row=1, column=0, padx=20, pady=15)
    ctk.CTkLabel(frame, text='Confirm password', font=('Franklin Gothic Condensed', 25), text_color='white', fg_color=default_color).grid(row=2, column=0, padx=20, pady=15)

    entry1 = ctk.CTkEntry(frame, font=('Franklin Gothic Condensed', 17))
    entry1.grid(row=1, column=1, padx=20, pady=15)

    entry2 = ctk.CTkEntry(frame, font=('Franklin Gothic Condensed', 17))
    entry2.grid(row=2, column=1, padx=20, pady=15)

    submit_btn = ctk.CTkButton(frame, text='Submit', command=lambda:Teacher.UpdatePassword(teacher, entry1.get(), entry2.get(), password_window), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    submit_btn.grid(row=3, column=1, pady=20)

    cancel_btn = ctk.CTkButton(frame, text='Cancel', command=password_window.destroy, font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    cancel_btn.grid(row=3, column=0, pady=20)

def T_LeaderboardsPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    LeaderboardsPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    LeaderboardsPage_frame.pack(fill='both', expand=True)

    T_CommonWidgets(LeaderboardsPage_frame, teacher, TeacherName, TeacherSubject)

    page_frame = ctk.CTkFrame(LeaderboardsPage_frame, fg_color=default_color, width=1000, height=600)
    page_frame.place(x=200, y=75)

    Pagetitle = ctk.CTkButton(page_frame, text='Student Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    Pagetitle.place(x=50, y=20)

    StudentsLeaderboard(page_frame)
    
    gazelles_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Gazelles', command=lambda:SelectedHouseLeadeboard(page_frame, 1), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    gazelles_leaderboard.place(x=275, y=200)

    oryxes_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Oryxes', command=lambda:SelectedHouseLeadeboard(page_frame, 2), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    oryxes_leaderboard.place(x=475, y=200)

    foxes_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Foxes', command=lambda:SelectedHouseLeadeboard(page_frame, 3), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    foxes_leaderboard.place(x=675, y=200)

    falcons_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Falcons', command=lambda:SelectedHouseLeadeboard(page_frame, 4), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    falcons_leaderboard.place(x=875, y=200)

    def SelectedRanking(event):
        if event == "House Rankings":
            HousesLeaderboard(page_frame)
        else:
            StudentsLeaderboard(page_frame)

    options = ["House Rankings", "Student Rankings"]
    rankingscombobox = ctk.CTkComboBox(LeaderboardsPage_frame, values=options,state='readonly', command=SelectedRanking, width=200)
    rankingscombobox.place(x=600, y=125)
    rankingscombobox.set("Student Rankings")
    rankingscombobox.configure(font=('franklin gothic condensed', 20))

def T_AddOrDeductPointsPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    ManageStudents_frame = ctk.CTkFrame(window, fg_color=default_color)
    ManageStudents_frame.pack(fill='both', expand=True)

    T_CommonWidgets(ManageStudents_frame, teacher, TeacherName, TeacherSubject)

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
    
def T_StudentListPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    T_StudentListPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    T_StudentListPage_frame.pack(fill='both', expand=True)
    
    T_CommonWidgets(T_StudentListPage_frame, teacher, TeacherName, TeacherSubject)

    pagetitle = ctk.CTkButton(T_StudentListPage_frame, text='Student list', font=('Franklin Gothic Condensed', 60), text_color='black', fg_color='white', border_width=2, width=250, height=50, hover='disabled')
    pagetitle.place(x=250, y=100)

    ctk.CTkLabel(T_StudentListPage_frame, text='Sort by Class', text_color='white', font=('franklin gothic condensed', 20)).place(x=645, y=220)
    class_filter = ctk.StringVar()
    year_groups = ["All", "9A", "9B", "9C", "9D", "10A", "10B", "10C", "10D", "11A", "11B", "11C", "11D", "12A", "12B", "12C", "12D", "13A", "13B", "13C", "13D"]
    class_filter_combobox = ctk.CTkComboBox(T_StudentListPage_frame, values=year_groups,state='readonly', variable=class_filter, font=('franklin gothic condensed', 15))
    class_filter_combobox.place(x=645, y=250)
    class_filter_combobox.set("All")
    
    ctk.CTkLabel(T_StudentListPage_frame, text='Sort by no. of points', text_color='white', font=('franklin gothic condensed', 20)).place(x=445, y=220)
    points_filter = ctk.StringVar()
    points_range = ["Highest - Lowest", "Lowest - Highest"]
    points_filter_combobox = ctk.CTkComboBox(T_StudentListPage_frame, values=points_range, state='readonly', variable=points_filter, font=('franklin gothic condensed', 15))
    points_filter_combobox.place(x=445, y=250)
    points_filter_combobox.set("Highest - Lowest")

    ctk.CTkLabel(T_StudentListPage_frame, text='Sort by House', text_color='white', font=('franklin gothic condensed', 20)).place(x=245, y=220)
    house_filter = ctk.StringVar()
    houses = ["All", "Gazelles", "Oryxes", "Foxes", "Falcons"]
    house_filter_combobox = ctk.CTkComboBox(T_StudentListPage_frame, values=houses, state='readonly', variable=house_filter, font=('franklin gothic condensed', 15))
    house_filter_combobox.place(x=245, y=250)
    house_filter_combobox.set("All")

    StudentList_frame = ctk.CTkScrollableFrame(T_StudentListPage_frame, fg_color=default_color, bg_color=default_color, border_width=2, border_color='black', width=700, height=550)
    StudentList_frame.place(x=245, y=290)

    T_ApplyStudentListFilters(StudentList_frame, class_filter, points_filter, house_filter)

    apply_filters_btn = ctk.CTkButton(T_StudentListPage_frame, text="Apply filters", command=lambda:T_ApplyStudentListFilters(StudentList_frame, class_filter, points_filter, house_filter), font=('Franklin gothic condensed', 15), text_color='black',fg_color='white', border_width=3, border_color='dark grey')
    apply_filters_btn.place(x=825, y=250)

def T_ApplyStudentListFilters(frame, class_filter, points_filter, house_filter):
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

    columns = ['Student ID', 'First Name', 'Last Name', 'Year Group', 'Total Points', 'House']
    for i in range(6):
        column = ctk.CTkButton(frame, text=columns[i], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=116, height=20, hover='disabled')
        column.grid(row=0, column=i)

    if Records != []:
        for i, record in enumerate(Records):
            for j, value in enumerate(record):
                button = ctk.CTkButton(frame, text=f'{value}', font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=116, height=20, hover='disabled')
                button.grid(row=i+1, column=j)
    else:
        message = ctk.CTkButton(frame, text="No data", text_color='black',  font=('Franklin Gothic Condensed', 45), fg_color='light grey', border_width=2, width=700, height=100, hover='disabled')
        message.grid(row=5, column=0, columnspan=6)  

def T_StudentRecordsPage(teacher, TeacherName, TeacherSubject):
    RemoveWidgets()
    StudentRecordsPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    StudentRecordsPage_frame.pack(fill='both', expand=True)

    pagetitle = ctk.CTkButton(StudentRecordsPage_frame, text='Student House Point records', font=('Franklin Gothic Condensed', 45), text_color='black', fg_color='white', border_width=2, width=250, height=50, hover='disabled')
    pagetitle.place(x=250, y=75)

    T_CommonWidgets(StudentRecordsPage_frame, teacher, TeacherName, TeacherSubject)
    
    Records_frame = ctk.CTkScrollableFrame(StudentRecordsPage_frame, fg_color=default_color, border_width=2, border_color='black', width=900, height=550)    
    Records_frame.place(x=199, y=200)

    column = ['Teacher ID', 'Teacher Name', 'Student ID', 'Student Name', 'Points\nAdded/Deducted', 'Date']
    for i in range(6):
        label = ctk.CTkButton(Records_frame, text=column[i], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=150, height=50, hover='disabled')
        label.grid(row=0, column=i)

    Records = cursor.execute("SELECT student_id, teacher_id, points, date_created FROM House_points_record").fetchall()
    for i in range(len(Records)):
        label = ctk.CTkButton(Records_frame, text=Records[i][1], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=150, height=20, hover='disabled')
        label.grid(row=i+1, column=0)

        name = cursor.execute("SELECT title, first_name, last_name FROM Teacher WHERE teacher_id = ?", (Records[i][1],)).fetchone()
        fullname = (name[0] + ' ' + name[1] + name[2])
        label = ctk.CTkButton(Records_frame, text=fullname, font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=150, height=20, hover='disabled')
        label.grid(row=i+1, column=1)

        label = ctk.CTkButton(Records_frame, text=Records[i][0], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=150, height=20, hover='disabled')
        label.grid(row=i+1, column=2)

        name = cursor.execute("SELECT first_name, last_name FROM Student WHERE student_id = ?", (Records[i][0],)).fetchone()
        fullname = (name[0] + ' ' + name[1])
        label = ctk.CTkButton(Records_frame, text=fullname, font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=150, height=20, hover='disabled')
        label.grid(row=i+1, column=3)        

    for i in range(len(Records)):
        for j in range(1,3):
            label = ctk.CTkButton(Records_frame, text=Records[i][j+1], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=150, height=20, hover='disabled')
            label.grid(row=i+1, column=j+3)

###Students' Side    
def S_HomePage(student):
    RemoveWidgets()
    StudentName = str(student.student_first_name + '  ' + student.student_last_name)
    StudentClass = str(student.student_grade)
    color = GetHouseColor(student)
    house_name = GetHouseName(student.student_houseId)

    StudentHome_frame = ctk.CTkFrame(window, fg_color=default_color)
    StudentHome_frame.pack(fill='both', expand=True)

    PageTitle = ctk.CTkButton(StudentHome_frame, text='Home', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    PageTitle.place(x=250, y=100)

    buttons_frame = ctk.CTkFrame(StudentHome_frame, fg_color=default_color)
    buttons_frame.place(x=300, y=200)

    topbar_frame = ctk.CTkFrame(StudentHome_frame, fg_color='light grey', border_width=2, border_color='black', width=900, height=60)
    topbar_frame.place(x=198, y=0)
    
    StudentName_label = ctk.CTkButton(topbar_frame, text=StudentName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    StudentName_label.place(x=0, y=0)

    StudentClass_label = ctk.CTkButton(topbar_frame, text=StudentClass, font=('Franklin Gothic Condensed', 21), text_color='black', fg_color='light grey', border_width=2, width=75, height=60, hover='disabled')
    StudentClass_label.place(x=174)

    StudentPoints_label = ctk.CTkButton(topbar_frame, text=("My total Points:  {}".format(student.student_points)), font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='light grey', border_width=2, width=300, height=60, hover='disabled')
    StudentPoints_label.place(x=600)

    options_frame = ctk.CTkFrame(StudentHome_frame, fg_color=color, border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    img = GetHouseLogo(student)
    houseimage_btn = ctk.CTkButton(options_frame, text='', image=img, text_color='black', fg_color='white', height= 150, width=150, border_width=1, hover='disabled')
    houseimage_btn.grid(row=0, pady=(50, 0))
    ctk.CTkLabel(options_frame, text=house_name, font=('Franklin Gothic Condensed', 20), text_color='white').grid(row=1, pady=(20, 65))

    acc_details_btn = ctk.CTkButton(options_frame, command=lambda:S_AccountDetailsPage(student, StudentName, StudentClass, color), text='Account Details', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    acc_details_btn.grid(row=2, pady=(0, 20))

    check_notifs_btn = ctk.CTkButton(options_frame, text='Show Notifications', command=lambda:Student.ShowNotifs(student), font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    check_notifs_btn.grid(row=3, pady=(0, 20))

    logout_btn = ctk.CTkButton(options_frame, command=lambda:ConfirmLogout(student), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    logout_btn.grid(row=4, pady=(0, 20))

    sizer = ctk.CTkButton(options_frame, text='', fg_color=color, width=200, height=0, hover='disabled')
    sizer.grid(row=5, pady=(700, 0))

    Leaderboard_btn = ctk.CTkButton(buttons_frame, command=lambda:S_LeaderboardsPage(student, StudentName, StudentClass, color), text='Leaderboard', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    Leaderboard_btn.grid(row=0, column=0, padx=25, pady=25)

    OwnedTokens_btn = ctk.CTkButton(buttons_frame, command=lambda:S_OwnedTokensPage(student, StudentName, StudentClass, color), text='Owned\nTokens', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    OwnedTokens_btn.grid(row=0, column=1, padx=25, pady=25)

    Shop_btn = ctk.CTkButton(buttons_frame, command=lambda:S_TokenShopPage(student, StudentName, StudentClass, color), text='Token\nShop', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    Shop_btn.grid(row=0, column=2, padx=25, pady=25)

    purchasehistory_btn = ctk.CTkButton(buttons_frame, command=lambda:S_PurchaseHistoryPage(student, StudentName, StudentClass, color), text='Purchase\nHistory', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    purchasehistory_btn.grid(row=1, column=0, columnspan=2, padx=100, pady=25)

    pointrecord_btn = ctk.CTkButton(buttons_frame, command=lambda:S_PointRecordsPage(student, StudentName, StudentClass, color), text='House Point\nRecords', font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='white', height=150, width=150, border_width=1)
    pointrecord_btn.grid(row=1, column=1, columnspan=2, padx=100, pady=25)

    Student.CheckNotifs(student)

def S_CommonWidgets(Frame, student, StudentName, StudentClass, color):
    topbar_frame = ctk.CTkFrame(Frame, fg_color='light grey', border_width=2, border_color='black', width=900, height=60)
    topbar_frame.place(x=198, y=0)
    
    StudentName_label = ctk.CTkButton(topbar_frame, text=StudentName, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=175, height=60, hover='disabled')
    StudentName_label.place(x=0, y=0)

    StudentClass_label = ctk.CTkButton(topbar_frame, text=StudentClass, font=('Franklin Gothic Condensed', 21), text_color='black', fg_color='light grey', border_width=2, width=75, height=60, hover='disabled')
    StudentClass_label.place(x=174)

    StudentPoints_label = ctk.CTkButton(topbar_frame, text=("My total Points:  {}".format(student.student_points)), font=('Franklin Gothic Condensed', 25), text_color='black', fg_color='light grey', border_width=2, width=300, height=60, hover='disabled')
    StudentPoints_label.place(x=600)

    options_frame = ctk.CTkFrame(Frame, fg_color=color, border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    img = GetHouseLogo(student)
    houseimage_btn = ctk.CTkButton(options_frame, text='', image=img, text_color='black', fg_color='white', height= 150, width=150, border_width=1, hover='disabled')
    houseimage_btn.grid(row=0, pady=(50, 85))

    manage_acc_btn = ctk.CTkButton(options_frame, command=lambda:S_AccountDetailsPage(student, StudentName, StudentClass, color), text='Account Details', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    manage_acc_btn.grid(row=1, pady=(0, 20))

    check_notifs_btn = ctk.CTkButton(options_frame, text='Notifications', command=lambda:Student.ShowNotifs(student), font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    check_notifs_btn.grid(row=2, pady=(0, 20))

    logout_btn = ctk.CTkButton(options_frame, command=lambda:ConfirmLogout(student), text='Log out', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=1, width=180, height=50)
    logout_btn.grid(row=3, pady=(0, 20))

    home_btn = ctk.CTkButton(options_frame, command=lambda:S_HomePage(student), text='Home', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', width=180, height=50, border_width=1)
    home_btn.grid(row=4, pady=(0, 20))

    sizer = ctk.CTkButton(options_frame, text='', fg_color=color, width=200, height=0, hover='disabled')
    sizer.grid(row=5, pady=(700, 0))

def S_AccountDetailsPage(student, StudentName, StudentClass,  color):
    RemoveWidgets()
    StudentAccManagement_frame = ctk.CTkFrame(window, fg_color=default_color)
    StudentAccManagement_frame.pack(fill='both', expand=True)

    S_CommonWidgets(StudentAccManagement_frame, student, StudentName, StudentClass, color)

    PageTitle = ctk.CTkButton(StudentAccManagement_frame, text='Account Details', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', hover='disabled')
    PageTitle.place(x=250, y=100)

    details_frame = ctk.CTkFrame(StudentAccManagement_frame, fg_color=default_color)
    details_frame.place(x=250, y=250)

    ctk.CTkLabel(details_frame, text ='First name', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=0, column=0, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Last name', text_color='white',font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=0, column=2, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='ID number', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=1, column=0, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Password', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=2, column=0, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='Class', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=1, column=2, padx=30, pady=20)
    ctk.CTkLabel(details_frame, text ='House', text_color='white', font=('Franklin Gothic Condensed', 30), fg_color=default_color).grid(row=2, column=2, padx=30, pady=20)

    FirstName_entry =  ctk.CTkEntry(details_frame, font=('franklin gothic condensed', 20))
    FirstName_entry.insert(0, student.student_first_name)
    FirstName_entry.grid(row=0, column=1, padx=30, pady=20)

    LastName_entry = ctk.CTkEntry(details_frame, font=('franklin gothic condensed', 20))
    LastName_entry.insert(0, student.student_last_name)
    LastName_entry.grid(row=0, column=3, padx=30, pady=20) 

    Id_entry = ctk.CTkEntry(details_frame, font=('franklin gothic condensed', 20))
    Id_entry.insert(0, student.student_id)
    Id_entry.grid(row=1, column=1, padx=30, pady=20)

    password_box = ctk.CTkButton(details_frame, text="********", text_color='black', font=('franklin gothic condensed', 17), fg_color='white', border_width=3, border_color='dark grey', width=150, height=17, hover='disabled')
    password_box.grid(row=2, column=1, padx=30, pady=20)

    selected_class = ctk.StringVar()
    year_groups = ["9A", "9B", "9C", "9D", "10A", "10B", "10C", "10D", "11A", "11B", "11C", "11D", "12A", "12B", "12C", "12D", "13A", "13B", "13C", "13D"]
    classcombobox = ctk.CTkComboBox(details_frame, values=year_groups,state='readonly', variable=selected_class)
    classcombobox.grid(row=1, column=3, padx=30, pady=20)
    classcombobox.set(student.student_grade)
    classcombobox.configure(font=('franklin gothic condensed', 20))

    selected_house = ctk.StringVar()
    houses = ["Gazelles", "Oryxes","Foxes","Falcons"]
    housecombobox = ctk.CTkComboBox(details_frame, values=houses, state='readonly', variable=selected_house)
    housecombobox.grid(row=2, column=3, padx=30, pady=20)
    housecombobox.set(GetHouseName(student.student_houseId))
    housecombobox.configure(font=('franklin gothic condensed', 20))    

    update_password_btn = ctk.CTkButton(details_frame, text='Update Password', command=lambda:S_UpdatePasswordPage(student), text_color='black', font=('franklin gothic condensed', 20), fg_color='white', border_width=3, border_color='dark grey')
    update_password_btn.grid(row=3, column=1, padx=30, pady=20)

    update_details_btn = ctk.CTkButton(details_frame, text='Update Details', command=lambda:student.UpdateFields(Id_entry, FirstName_entry, LastName_entry, selected_class.get(), selected_house.get(), student), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='dark grey')
    update_details_btn.grid(row=3, column=2, padx=30, pady=20)

def S_UpdatePasswordPage(student):
    password_window = ctk.CTkToplevel(window, fg_color=default_color)
    password_window.geometry('400x350')
    password_window.title('Update Password')
    password_window.attributes('-topmost', True)
    password_window.resizable(False, False)

    ctk.CTkLabel(password_window, text='Enter your new password', font=('Franklin Gothic Condensed', 35), text_color='white', fg_color=default_color).pack(pady=30)

    frame = ctk.CTkFrame(password_window, fg_color=default_color)
    frame.pack()

    ctk.CTkLabel(frame, text='New password', font=('Franklin Gothic Condensed', 25), text_color='white', fg_color=default_color).grid(row=1, column=0, padx=20, pady=15)
    ctk.CTkLabel(frame, text='Confirm password', font=('Franklin Gothic Condensed', 25), text_color='white', fg_color=default_color).grid(row=2, column=0, padx=20, pady=15)

    entry1 = ctk.CTkEntry(frame, font=('Franklin Gothic Condensed', 17))
    entry1.grid(row=1, column=1, padx=20, pady=15)

    entry2 = ctk.CTkEntry(frame, font=('Franklin Gothic Condensed', 17))
    entry2.grid(row=2, column=1, padx=20, pady=15)

    submit_btn = ctk.CTkButton(frame, text='Submit', command=lambda:Student.UpdatePassword(student, entry1.get(), entry2.get(), password_window), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    submit_btn.grid(row=3, column=1, pady=20)

    cancel_btn = ctk.CTkButton(frame, text='Cancel', command=password_window.destroy, font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    cancel_btn.grid(row=3, column=0, pady=20)

def S_LeaderboardsPage(student, StudentName, StudentClass,  color):
    RemoveWidgets()
    LeaderboardsPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    LeaderboardsPage_frame.pack(fill='both', expand=True)

    S_CommonWidgets(LeaderboardsPage_frame, student, StudentName, StudentClass,  color)

    page_frame = ctk.CTkFrame(LeaderboardsPage_frame, fg_color=default_color, width=1000, height=600)
    page_frame.place(x=200, y=75)

    Pagetitle = ctk.CTkButton(page_frame, text='Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    Pagetitle.place(x=50, y=20)

    StudentsLeaderboard(page_frame)
    
    gazelles_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Gazelles', command=lambda:SelectedHouseLeadeboard(page_frame, 1), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    gazelles_leaderboard.place(x=275, y=200)

    oryxes_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Oryxes', command=lambda:SelectedHouseLeadeboard(page_frame, 2), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    oryxes_leaderboard.place(x=475, y=200)

    foxes_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Foxes', command=lambda:SelectedHouseLeadeboard(page_frame, 3), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    foxes_leaderboard.place(x=675, y=200)

    falcons_leaderboard = ctk.CTkButton(LeaderboardsPage_frame, text='Falcons', command=lambda:SelectedHouseLeadeboard(page_frame, 4), text_color='black', font=('Franklin Gothic Condensed', 40), fg_color='white', border_width=2, border_color='black', width=160, height=60)
    falcons_leaderboard.place(x=875, y=200)

    def SelectedRanking(event):
        if event == "House Rankings":
            HousesLeaderboard(page_frame)
        else:
            StudentsLeaderboard(page_frame)

    options = ["House Rankings", "Student Rankings"]
    rankingscombobox = ctk.CTkComboBox(LeaderboardsPage_frame, values=options,state='readonly', command=SelectedRanking, width=200)
    rankingscombobox.place(x=700, y=125)
    rankingscombobox.set("Student Rankings")
    rankingscombobox.configure(font=('franklin gothic condensed', 20))

def S_PurchaseHistoryPage(student, StudentName, StudentClass, color):
    RemoveWidgets()
    Records = cursor.execute("SELECT purchase_id, token_name, purchase_date FROM Purchase_token JOIN Token ON Token.token_id = Purchase_token.token_id").fetchall()
    PurchaseHistory_frame = ctk.CTkFrame(window, fg_color=default_color)
    PurchaseHistory_frame.pack(fill='both', expand=True)

    S_CommonWidgets(PurchaseHistory_frame, student, StudentName, StudentClass, color)

    PageTitle_label = ctk.CTkButton(PurchaseHistory_frame, text='My Purchases', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=400, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=100)

    Records_frame = ctk.CTkScrollableFrame(window, fg_color=default_color, bg_color=default_color, border_width=2, border_color='black', width=700, height=450)
    Records_frame.place(x=245, y=190)

    columns = ['Purchase ID', 'Token', 'Date Purchased']
    for i in range(3):
        column = ctk.CTkButton(Records_frame, text=columns[i], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='dark grey', border_width=2, width=233, height=40, hover='disabled')
        column.grid(row=0, column=i)

    for i, record in enumerate(Records):
        for j, value in enumerate(record):
            button = ctk.CTkButton(Records_frame, text=f'{value}', text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=233, height=20, hover='disabled')
            button.grid(row=i+1, column=j)

def S_OwnedTokensPage(student, StudentName, StudentClass, color):
    RemoveWidgets()
    OwnedTokensPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    OwnedTokensPage_frame.pack(fill='both', expand=True)

    S_CommonWidgets(OwnedTokensPage_frame, student, StudentName, StudentClass, color)
    
    PageTitle_label = ctk.CTkButton(OwnedTokensPage_frame, text='My Tokens', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=100)

    tokens_frame = ctk.CTkScrollableFrame(OwnedTokensPage_frame, fg_color=default_color, border_width=2, border_color='black', width=800, height=100)
    tokens_frame.place(x=250, y=300)

    columns = ['Token', 'Total quantity', 'Last purchase date', 'Next purchase date']
    for i in range(4):
        ctk.CTkButton(tokens_frame, text=columns[i], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='dark grey', border_width=2, width=200, height=35, hover='disabled').grid(row=0, column=i)

    StudentTokens = cursor.execute("SELECT token_id, quantity, last_purchase_date, next_purchase_date FROM Owned_tokens WHERE student_id = ?", (student.student_id,)).fetchall()
    for i in range(len(StudentTokens)):
        Token = cursor.execute("SELECT token_name FROM Token WHERE token_id = ?", (StudentTokens[i][0],)).fetchone()
        ctk.CTkButton(tokens_frame, text=Token[0], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=35, hover='disabled').grid(row=i+1, column=0)
        for j in range(3):
            if StudentTokens[i][j+1] == None:
                ctk.CTkButton(tokens_frame, text='', font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=35, hover='disabled').grid(row=i+1, column=j+1)
            else:
                ctk.CTkButton(tokens_frame, text=StudentTokens[i][j+1], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=35, hover='disabled').grid(row=i+1, column=j+1)

def S_PointRecordsPage(student, StudentName, StudentClass, color):
    RemoveWidgets()
    S_PointRecordsPage_frame = ctk.CTkFrame(window, fg_color=default_color)
    S_PointRecordsPage_frame.pack(fill='both', expand=True)

    S_CommonWidgets(S_PointRecordsPage_frame, student, StudentName, StudentClass, color)

    PageTitle = ctk.CTkButton(S_PointRecordsPage_frame, text='My House Point records', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    PageTitle.place(x=250, y=100)

    Records_frame = ctk.CTkScrollableFrame(S_PointRecordsPage_frame, fg_color=default_color, border_width=2, border_color='black', width=800, height=550)    
    Records_frame.place(x=250, y=200)

    column = ['Teacher ID', 'Teacher Name', 'Points\nAdded/Deducted', 'Date']
    for i in range(4):
        ctk.CTkButton(Records_frame, text=column[i], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='dark grey', border_width=2, width=200, height=60, hover='disabled').grid(row=0, column=i)

    Records = cursor.execute("SELECT teacher_id, points, date_created FROM House_points_record WHERE student_id = ?", (student.student_id,)).fetchall()
    for i in range(len(Records)):
        for j in range(2):
            ctk.CTkButton(Records_frame, text=Records[i][0], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=40, hover='disabled').grid(row=i+1, column=0)

            name = cursor.execute("SELECT title, first_name, last_name FROM Teacher WHERE teacher_id = ?", (Records[i][0],)).fetchone()
            fullname = (name[0] + ' ' + name[1] + name[2])
            ctk.CTkButton(Records_frame, text=fullname, font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=40, hover='disabled').grid(row=i+1, column=1)

    for i in range(len(Records)):
        for j in range(1,3):
            ctk.CTkButton(Records_frame, text=Records[i][j], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=200, height=40, hover='disabled').grid(row=i+1, column=j+1)

def S_TokenShopPage(student, StudentName, StudentClass, color):
    RemoveWidgets()
    token_name = {1:"Dress code exemption", 2:"Cafeteria coupon", 3:"One day off", 4:"null"}
    Shop_frame = ctk.CTkFrame(window, fg_color=default_color)
    Shop_frame.pack(fill='both', expand=True)

    S_CommonWidgets(Shop_frame, student, StudentName, StudentClass, color)

    PageTitle_label = ctk.CTkButton(Shop_frame, text='Token Shop', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=95)

    Tokens_frame = ctk.CTkFrame(Shop_frame, fg_color=default_color)
    Tokens_frame.place(x=245, y=160)

    Token1_btn = ctk.CTkButton(Tokens_frame, text='Dress Code\nExemption', command=lambda:S_ConfirmPurchaseWindow(student, token_name[1]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='white',height= 120, width=150, border_width=1)
    Token1_btn.grid(row=0, column=0, padx=100, pady=(50, 0))

    Token1_desc = ctk.CTkLabel(Tokens_frame, text=('{}'.format(GetTokenDesc(1))), text_color='white', font=('Franklin Gothic Condensed', 17), width=100, height=2)
    Token1_desc.grid(row=1, column=0, padx=100, pady=(10, 0))

    Token2_btn = ctk.CTkButton(Tokens_frame, text='Cafeteria\nCoupon', command=lambda:S_ConfirmPurchaseWindow(student, token_name[2]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='white',height= 120, width=150, border_width=1)
    Token2_btn.grid(row=0, column=1, padx=50, pady=(50, 0))

    Token2_desc = ctk.CTkLabel(Tokens_frame, text=('{}'.format(GetTokenDesc(2))), text_color='white', font=('Franklin Gothic Condensed', 17), width=100, height=2)
    Token2_desc.grid(row=1, column=1, padx=50, pady=(10, 0))

    Token3_btn = ctk.CTkButton(Tokens_frame, text='1 day\noff', command=lambda:S_ConfirmPurchaseWindow(student, token_name[3]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='white',height= 120, width=150, border_width=1)
    Token3_btn.grid(row=2, column=0, padx=100, pady=(50, 0))

    Token3_desc = ctk.CTkLabel(Tokens_frame, text=('{}'.format(GetTokenDesc(3))), text_color='white', font=('Franklin Gothic Condensed', 17), width=100, height=2)
    Token3_desc.grid(row=3, column=0, padx=100, pady=(10, 0))

def S_ConfirmPurchaseWindow(student, token_name):
    token_id = GetTokenId(token_name)
    confirmPurchase_window = ctk.CTkToplevel(window, fg_color='dark grey')
    confirmPurchase_window.geometry('650x200')
    confirmPurchase_window.title('Confirm purchase')
    confirmPurchase_window.attributes('-topmost', True)
    confirmPurchase_window.resizable(False, False)

    frame = ctk.CTkFrame(confirmPurchase_window, fg_color='dark grey')
    frame.pack()

    ctk.CTkLabel(frame, text=('Are you sure you want to\npurchase this "{}" token?').format(token_name), font=('Franklin Gothic Condensed', 25)).grid(row=0, columnspan=2, pady=25)

    confirm_btn = ctk.CTkButton(frame, text='Yes', command=lambda: PurchaseAndClose(confirmPurchase_window, student, token_id), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    confirm_btn.grid(row=1, column=0, padx=30, pady=15)

    cancel_btn = ctk.CTkButton(frame, text='No', command=confirmPurchase_window.destroy, font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    cancel_btn.grid(row=1, column=1, padx=30, pady=15)

def PurchaseAndClose(window, student, token_id):
    student.PurchaseToken(token_id)
    S_HomePage(student)
    window.destroy()

def SelectedHouseLeadeboard(frame, input):
    for widget in frame.winfo_children():
        widget.destroy()

    if input == 1 or input == 2 or input == 3 or input == 4:
        if input == 1:
            ctk.CTkButton(frame, text='Gazelles Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled').place(x=50, y=20)
        elif input == 2:
            ctk.CTkButton(frame, text='Oryxes Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled').place(x=50, y=20)
        elif input == 3:
            ctk.CTkButton(frame, text='Foxes Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled').place(x=50, y=20)
        elif input == 4:
            ctk.CTkButton(frame, text='Falcons Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled').place(x=50, y=20)

        list_frame = ctk.CTkScrollableFrame(frame, fg_color=default_color, border_width=2, border_color='black', width=700, height=550)    
        list_frame.place(x=85, y=200)

        columns = ["Position", "Student ID", "Student name", "Points"]
        for i in range(4):
            ctk.CTkButton(list_frame, text=columns[i], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=175, height=40, hover='disabled').grid(row=0, column=i)
        
        students_in_house = cursor.execute("SELECT student_id FROM Student WHERE house_id = ? ORDER BY total_points DESC", (input,)).fetchall()
        for i in range(len(students_in_house)):
            cursor.execute("UPDATE Student SET position_in_house = ? WHERE student_id = ?", (i+1, students_in_house[i][0]))
            conn.commit()

        records = cursor.execute("SELECT position_in_house, student_id, first_name, last_name, total_points FROM Student WHERE house_id = ? ORDER BY position_in_house ASC", (input,)).fetchall()
        for i in range(len(records)):
            ctk.CTkButton(list_frame, text=records[i][0], text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=175, height=20, hover='disabled').grid(row=i+1, column=0)
            ctk.CTkButton(list_frame, text=records[i][1], text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=175, height=20, hover='disabled').grid(row=i+1, column=1)
            ctk.CTkButton(list_frame, text=str(records[i][2]+' '+records[i][3]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=175, height=20, hover='disabled').grid(row=i+1, column=2)      
            ctk.CTkButton(list_frame, text=records[i][4], text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=175, height=20, hover='disabled').grid(row=i+1, column=3)

def StudentsLeaderboard(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    
    Pagetitle = ctk.CTkButton(frame, text='Student Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    Pagetitle.place(x=50, y=20)

    list_frame = ctk.CTkScrollableFrame(frame, fg_color=default_color, border_width=2, border_color='black', width=700, height=550)    
    list_frame.place(x=85, y=200)

    students = cursor.execute("SELECT student_id FROM Student ORDER BY total_points DESC").fetchall()
    for i in range(len(students)):
        cursor.execute("UPDATE Student SET leaderboard_position = ? WHERE student_id = ?", (i+1, students[i][0]))
        conn.commit()

    columns = ["Position", "Student ID", "Student name", "House", "Points"]
    for i in range(5):
        ctk.CTkButton(list_frame, text=columns[i], font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='dark grey', border_width=2, width=140, height=40, hover='disabled').grid(row=0, column=i)

    records = cursor.execute("SELECT leaderboard_position, student_id, first_name, last_name, house_id, total_points FROM Student ORDER BY leaderboard_position ASC").fetchall()
    for i in range(len(records)):
        ctk.CTkButton(list_frame, text=records[i][0], text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=140, height=20, hover='disabled').grid(row=i+1, column=0)
        ctk.CTkButton(list_frame, text=records[i][1], text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=140, height=20, hover='disabled').grid(row=i+1, column=1)
        ctk.CTkButton(list_frame, text=str(records[i][2]+' '+records[i][3]), font=('Franklin Gothic Condensed', 17), text_color='black', fg_color='light grey', border_width=2, width=140, height=20, hover='disabled').grid(row=i+1, column=2)      
        ctk.CTkButton(list_frame, text=GetHouseName(records[i][4]), text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=140, height=20, hover='disabled').grid(row=i+1, column=3)
        ctk.CTkButton(list_frame, text=records[i][5], text_color='black', font=('Franklin Gothic Condensed', 17), fg_color='light grey', border_width=2, width=140, height=20, hover='disabled').grid(row=i+1, column=4)

def HousesLeaderboard(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    
    Pagetitle = ctk.CTkButton(frame, text='Houses Leaderboard', font=('Franklin Gothic Condensed', 45), text_color='white', fg_color=default_color, border_width=2, border_color='white', width=250, height=50, hover='disabled')
    Pagetitle.place(x=50, y=20)

    list_frame = ctk.CTkScrollableFrame(frame, fg_color=default_color, border_width=2, border_color='black', width=700, height=550)    
    list_frame.place(x=85, y=200)

    columns = ["Position", "House", "Total Points"]
    for i in range(3):
        ctk.CTkButton(list_frame, text=columns[i], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='dark grey', border_width=2, width=233, height=40, hover='disabled').grid(row=0, column=i)

    houses = cursor.execute("SELECT house_id FROM House ORDER BY house_totalpoints DESC").fetchall()
    for i in range(len(houses)):
        cursor.execute("UPDATE House SET house_leaderboard_position = ? WHERE house_id = ?", (i+1, houses[i][0],))
        conn.commit()

    house_records = cursor.execute("SELECT house_leaderboard_position, house_name, house_totalpoints FROM House ORDER BY house_totalpoints DESC").fetchall()
    for i in range(len(house_records)):
        for j in range(3):
            ctk.CTkButton(list_frame, text=house_records[i][j], font=('Franklin Gothic Condensed', 20), text_color='black', fg_color='light grey', border_width=2, width=233, height=40, hover='disabled').grid(row=i+1, column=j)

def ConfirmLogout(user):
    confirmLogout_window = ctk.CTkToplevel(window, fg_color='dark grey')
    confirmLogout_window.geometry('600x150')
    confirmLogout_window.title('Log Out?')
    confirmLogout_window.attributes('-topmost', True)
    confirmLogout_window.resizable(False, False)

    frame = ctk.CTkFrame(confirmLogout_window, fg_color='dark grey')
    frame.pack()

    ctk.CTkLabel(frame, text=('Are you sure you want to log out?'), font=('Franklin Gothic Condensed', 25)).grid(row=0, columnspan=2, pady=25)

    confirm_btn = ctk.CTkButton(frame, text='Yes', command=lambda: Logout(user), font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    confirm_btn.grid(row=1, column=0, padx=30, pady=15)

    cancel_btn = ctk.CTkButton(frame, text='No', command=confirmLogout_window.destroy, font=('Franklin gothic condensed', 20), text_color='black', fg_color='white', border_width=3, border_color='grey')
    cancel_btn.grid(row=1, column=1, padx=30, pady=15)

def Logout(user):
    del user
    RemoveWidgets()
    Loginpage()

if __name__ == "__main__":
    from House_points_database import database
    database()
    Loginpage()
    window.mainloop()
