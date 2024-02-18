import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

conn = sqlite3.connect("House points")
cursor = conn.cursor()

window = tk.Tk()
window.title('House Points System')
window.geometry('1000x600')

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
                StudentHome(student, Id, first_name, last_name)
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

        def UpdateFields(self, Id, FirstName_entry, LastName_entry):
            NewFirstName = FirstName_entry.get()
            NewLastName = LastName_entry.get()
            cursor.execute("UPDATE Student SET first_name = ? WHERE student_id = ?", (NewFirstName,Id,))
            cursor.execute("UPDATE Student SET last_name = ? WHERE student_id = ?", (NewLastName, Id,))
            conn.commit()
            self.student_first_name = NewFirstName
            self.student_last_name = NewLastName

def remove_widgets():
    for widget in window.winfo_children():
        widget.destroy()

def GetHouseColor(StudentHouse):
    if StudentHouse == 1:
        color = '#0A8B0B'
        return color
    elif StudentHouse == 2:
        color = '#FFC300'
        return color
    elif StudentHouse == 3:
        color = '#000000'
        return color
    elif StudentHouse == 4:
        color = '#0012C4'
        return color

def Loginpage():
    login_frame = tk.Frame(window, bg='light grey')
    login_frame.pack(fill='both', expand=True)

    titleLabel = tk.Label(login_frame, text='ASCS House Points', font='Impact 50', bg='light grey')
    titleLabel.pack(pady=50)

    input_frame = tk.Frame(login_frame, bg='light grey')
    input_frame.pack()

    tk.Label(input_frame, text='ID', font='Impact 12', bg='light grey').grid(row=0, column=0)
    tk.Label(input_frame, text='Password', font='Impact 12', bg='light grey').grid(row=1, column=0)

    Id_entry = tk.Entry(input_frame)
    Id_entry.grid(row=0, column=1, padx=5, pady=10)

    password_entry = tk.Entry(input_frame, show='*')
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    selected_value = tk.StringVar()
    options = ["Teacher", "Student"]
    combobox = ttk.Combobox(input_frame, values=options, state='readonly', textvariable=selected_value)
    combobox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    combobox.set("Select an option")

    tk.Button(input_frame, text='Submit', command=lambda:User.login(selected_value, Id_entry, password_entry)).grid(row=3, columnspan=2, pady=10)

def StudentHome(user, Id, first_name, last_name):
    remove_widgets()
    StudentName = str(first_name + ' ' + last_name)
    color = GetHouseColor(StudentHouse)

    StudentHome_frame = tk.Frame(window, bg='light grey')
    StudentHome_frame.pack(fill='both', expand=True)

    options_frame = tk.Frame(StudentHome_frame, bg=color, width=200, height=600, highlightthickness=1, highlightbackground="black")
    options_frame.pack(side=tk.LEFT, fill='y', expand=False)

    manage_acc_btn = tk.Button(options_frame, command=lambda:StudentAccManagement(user, Id, first_name, last_name, color), text='Account Management', font=('Impact', 13), fg='black', bg='light grey')
    manage_acc_btn.place(x=0, y=200)

    logout_btn = tk.Button(options_frame, command=lambda:logout(user), text='Log out', font=('Impact', 13), fg='black', bg='light grey')
    logout_btn.place(x=0, y=325)

    StudentPoints_label = tk.Label(StudentHome_frame, text=("Total Points:  {}".format(StudentPoints)), highlightthickness=1, highlightbackground="black")
    StudentPoints_label.config(font=('Impact', 13), width=20, height=2) 
    StudentPoints_label.place(relx=1, rely=0, x=-15, y=0, anchor='ne')
    
    StudentName_label = tk.Label(StudentHome_frame, text=StudentName, highlightthickness=1, highlightbackground="black")
    StudentName_label.config(font=('Impact', 13), width=15, height=2)
    StudentName_label.place(x=200, y=0)

def StudentAccManagement(user, Id, first_name, last_name, color):
    remove_widgets()
    StudentAccManagement_frame = tk.Frame(window, bg='light grey')
    StudentAccManagement_frame.pack(fill='both', expand=True)

    options_frame = tk.Frame(StudentAccManagement_frame, bg=color, width=200, height=600, highlightthickness=1, highlightbackground="black")
    options_frame.pack(side=tk.LEFT, fill='y', expand=False)

    back_btn = tk.Button(options_frame, command=lambda:StudentHome(user, Id ,first_name, last_name), text='Back', font=('Impact', 15), fg='black', bg='light grey')
    back_btn.place(x=0, y=500)

    tk.Label(StudentAccManagement_frame, text ='First name', font='Impact 11', bg='light grey').place(x=340, y=200)
    FirstName_entry =  tk.Entry(StudentAccManagement_frame)
    FirstName_entry.insert(0,first_name)
    FirstName_entry.place(x=440, y=200)

    tk.Label(StudentAccManagement_frame, text ='Last name', font='Impact 11', bg='light grey').place(x=340, y=225)
    LastName_entry = tk.Entry(StudentAccManagement_frame)
    LastName_entry.insert(0,last_name)
    LastName_entry.place(x=440, y=225)

    tk.Button(StudentAccManagement_frame, text='Submit', command=lambda:Student.UpdateFields(Id, FirstName_entry, LastName_entry)).place(x=500, y=300)

def logout(user):
    del user
    remove_widgets()
    Loginpage()

if __name__ == "__main__":
    from House_points_database import database
    database()
    Loginpage()
    window.mainloop()
