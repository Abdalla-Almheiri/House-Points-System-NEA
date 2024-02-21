import customtkinter as ctk
from tkinter import messagebox
import sqlite3

conn = sqlite3.connect("House points")
cursor = conn.cursor()

window = ctk.CTk()
window.title('House Points System')
window.geometry('1000x600')
ctk.set_appearance_mode("light")

class User:
    def __init__(self, password, first_name, last_name):
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def login(selected_value, Id_entry, password_entry):
        if selected_value.get() == 'Student':
            Id = Id_entry.get()
            password = password_entry.get()
            user = cursor.execute("SELECT * FROM Student WHERE student_id = ?", (Id,)).fetchall()
            if user[0][1] == password:
                first_name = user[0][2]
                last_name = user[0][3]
                StudentHouse = user[0][5]
                StudentPoints = user[0][6]
                student = Student(user, Id, password, first_name, last_name, StudentHouse, StudentPoints)
                StudentHome(student)
            else:
                messagebox.showerror("Login Failed", "Invalid Id or password.")
        elif selected_value.get() == 'Teacher':
            Id = Id_entry.get()
            password = password_entry.get()
            user = cursor.execute("SELECT * FROM Teacher WHERE teacher_id = ?", (Id,)).fetchall()
            if user[0][1] == password:
                messagebox.showinfo("Login Successful", "Welcome, {}!".format(Id))
            else:
                messagebox.showerror("Login Failed", "Invalid Id or password.")
        else:
            messagebox.showinfo("Login Failed", "Select Student or Teacher")

class Student(User):
        def __init__(self, user, Id, password, first_name, last_name, StudentHouse, StudentPoints):
            super().__init__(password, first_name, last_name)
            self.student_id = Id
            self.student_first_name = first_name
            self.student_last_name = last_name
            self.student_grade = user[0][4]
            self.student_house = StudentHouse
            self.student_points = StudentPoints

        def UpdateStudentFields(self, FirstName_entry, LastName_entry, student):
            NewFirstName = FirstName_entry.get()
            NewLastName = LastName_entry.get()
            cursor.execute("UPDATE Student SET first_name = ? WHERE student_id = ?", (NewFirstName, self.student_id,))
            cursor.execute("UPDATE Student SET last_name = ? WHERE student_id = ?", (NewLastName, self.student_id,))
            conn.commit()
            self.student_first_name = NewFirstName
            self.student_last_name = NewLastName
            messagebox.showinfo('',"Successfully updated account details")
            remove_widgets()
            StudentHome(student)

        def CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, EnterGrade, selected_house):
            first_name = EnterFirstName.get()
            last_name = EnterLastName.get()
            password = EnterPassword.get()
            Id = EnterId.get()
            grade = EnterGrade.get()
            houseId = HouseToHouseID(selected_house)
            cursor.execute("INSERT INTO Student (student_ID, password, first_name, last_name, grade, house_id, total_points, leaderboard_position) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (Id, password, first_name, last_name, grade, houseId, 0, 0))
            conn.commit()
            messagebox.showinfo('',"Account created successfully")
            remove_widgets()
            Loginpage()

def remove_widgets():
    for widget in window.winfo_children():
        widget.destroy()

def HouseToHouseID(selected_house):
    if selected_house == "Gazelles":
        houseId = 1
        return houseId
    elif selected_house == "Oryxes":
        houseId = 2
        return houseId
    elif selected_house == "Foxes":
        houseId = 3
        return houseId
    elif selected_house == "Falcons":
        houseId = 4
        return houseId

def GetHouseColor(user):
    if user.student_house == 1:
        color = '#0A8B0B'
        return color
    elif user.student_house == 2:
        color = '#FFC300'
        return color
    elif user.student_house == 3:
        color = '#000000'
        return color
    elif user.student_house == 4:
        color = '#0012C4'
        return color

def CreateStudentPage():
    remove_widgets()
    CreateAcc_frame = ctk.CTkFrame(window, fg_color='light grey')
    CreateAcc_frame.pack(fill='both', expand=True)

    ctk.CTkLabel(CreateAcc_frame, text='Enter your details', font=('Impact', 40), fg_color='light grey').place(x=350, y=100)

    ctk.CTkLabel(CreateAcc_frame, text='Enter your first name', font=('Impact', 17), fg_color='light grey').place(x=200, y=185)
    ctk.CTkLabel(CreateAcc_frame, text='Enter your last name', font=('Impact', 17), fg_color='light grey').place(x=525, y=185)
    ctk.CTkLabel(CreateAcc_frame, text='Enter an ID number', font=('Impact', 17), fg_color='light grey').place(x=200, y=230)
    ctk.CTkLabel(CreateAcc_frame, text='Enter your grade', font=('Impact', 17), fg_color='light grey').place(x=525, y=230)
    ctk.CTkLabel(CreateAcc_frame, text='Enter a password', font=('Impact', 17), fg_color='light grey').place(x=200, y=275)
    ctk.CTkLabel(CreateAcc_frame, text='Select your House', font=('Impact', 17), fg_color='light grey').place(x=525, y=275)

    EnterFirstName = ctk.CTkEntry(CreateAcc_frame)
    EnterFirstName.place(x=350, y=185)

    EnterLastName = ctk.CTkEntry(CreateAcc_frame)
    EnterLastName.place(x=675, y=185)

    EnterId = ctk.CTkEntry(CreateAcc_frame)
    EnterId.place(x=350, y=230)

    EnterPassword = ctk.CTkEntry(CreateAcc_frame)
    EnterPassword.place(x=350, y=275)

    EnterGrade = ctk.CTkEntry(CreateAcc_frame)
    EnterGrade.place(x=675, y=230)

    selected_house = ctk.StringVar()
    options = ["Gazelles", "Oryxes","Foxes","Falcons"]
    Housecombobox = ctk.CTkComboBox(CreateAcc_frame, values=options, state='readonly', variable=selected_house)
    Housecombobox.place(x=675, y=275)
    
    submit_btn = ctk.CTkButton(CreateAcc_frame, text='Create account', bg_color='black', command=lambda:Student.CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, EnterGrade, selected_house))
    submit_btn.place(x=450, y=400)

    back_btn = ctk.CTkButton(CreateAcc_frame, command=lambda:Loginpage(), text='Back', font=('Impact', 15), text_color='black', fg_color='white', width=50, border_width=1)
    back_btn.place(x=0, y=500)

def Loginpage():
    remove_widgets()
    login_frame = ctk.CTkFrame(window, fg_color='light grey')
    login_frame.pack(fill='both', expand=True)

    titleLabel = ctk.CTkLabel(login_frame, text='ASCS House Points', font=('Impact', 60), fg_color='light grey')
    titleLabel.pack(pady=50)

    input_frame = ctk.CTkFrame(login_frame, fg_color='light grey')
    input_frame.pack()

    ctk.CTkLabel(input_frame, text='ID number', font=('Impact', 20), fg_color='light grey').grid(row=0, column=0)
    ctk.CTkLabel(input_frame, text='Password', font=('Impact', 20), fg_color='light grey').grid(row=1, column=0)

    Id_entry = ctk.CTkEntry(input_frame)
    Id_entry.grid(row=0, column=1, padx=5, pady=10)

    password_entry = ctk.CTkEntry(input_frame, show='*')
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    selected_value = ctk.StringVar()
    options = ["Teacher", "Student"]
    combobox = ctk.CTkComboBox(input_frame, values=options, state='readonly', variable=selected_value)
    combobox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    combobox.set("Select an option")

    ctk.CTkButton(input_frame, text='Submit', bg_color='black', command=lambda:User.login(selected_value, Id_entry, password_entry)).grid(row=3, columnspan=2, pady=10)
    ctk.CTkButton(input_frame, text='Create a new account', bg_color='black', command=lambda:CreateStudentPage()).grid(row=4, columnspan=2, pady=5)

def StudentHome(student):
    remove_widgets()
    StudentName = str(student.student_first_name + ' ' + student.student_last_name)
    color = GetHouseColor(student)

    StudentHome_frame = ctk.CTkFrame(window, fg_color='light grey')
    StudentHome_frame.pack(fill='both', expand=True)

    options_frame = ctk.CTkFrame(StudentHome_frame, fg_color=color, width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    manage_acc_btn = ctk.CTkButton(options_frame, command=lambda:StudentAccManagement(student,color), text='Account Management', font=('Impact', 13), text_color='black', fg_color='light grey')
    manage_acc_btn.place(x=0, y=200)

    logout_btn = ctk.CTkButton(options_frame, command=lambda:logout(student), text='Log out', font=('Impact', 13), text_color='black', fg_color='light grey')
    logout_btn.place(x=0, y=325)

    StudentPoints_label = ctk.CTkLabel(StudentHome_frame, text=("Total Points:  {}".format(student.student_points)))
    StudentPoints_label.configure(font=('Impact', 13), width=20, height=2) 
    StudentPoints_label.place(relx=1, rely=0, x=-15, y=0, anchor='ne')
    
    StudentName_label = ctk.CTkLabel(StudentHome_frame, text=StudentName)
    StudentName_label.configure(font=('Impact', 13), width=15, height=2)
    StudentName_label.place(x=200, y=0)

def StudentAccManagement(student, color):
    remove_widgets()
    StudentAccManagement_frame = ctk.CTkFrame(window, fg_color='light grey')
    StudentAccManagement_frame.pack(fill='both', expand=True)

    options_frame = ctk.CTkFrame(StudentAccManagement_frame, fg_color=color, width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    back_btn = ctk.CTkButton(options_frame, command=lambda:StudentHome(student), text='Back', font=('Impact', 15), text_color='black', fg_color='light grey', width=50, border_width=1)
    back_btn.place(x=0, y=500)

    ctk.CTkLabel(StudentAccManagement_frame, text ='First name', font=('Impact', 11), fg_color='light grey').place(x=340, y=200)
    FirstName_entry =  ctk.CTkEntry(StudentAccManagement_frame)
    FirstName_entry.insert(0,student.student_first_name)
    FirstName_entry.place(x=440, y=200)

    ctk.CTkLabel(StudentAccManagement_frame, text ='Last name', font=('Impact', 11), fg_color='light grey').place(x=340, y=225)
    LastName_entry = ctk.CTkEntry(StudentAccManagement_frame)
    LastName_entry.insert(0,student.student_last_name)
    LastName_entry.place(x=440, y=225)

    ctk.CTkButton(StudentAccManagement_frame, text='Submit', command=lambda:student.UpdateStudentFields(FirstName_entry, LastName_entry, student)).place(x=500, y=300)

def logout(user):
    del user
    remove_widgets()
    Loginpage()

if __name__ == "__main__":
    from House_points_database import database
    database()
    Loginpage()
    window.mainloop()
