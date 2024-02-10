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
            pass_check = cursor.execute("SELECT password FROM Student WHERE student_id = ?", (Id,)).fetchall()
            if pass_check[0][0] == password:
                messagebox.showinfo("Login Successful", "Welcome, {}!".format(Id))
            else:
                messagebox.showerror("Login Failed", "Invalid Id or password.")
        elif selected_value.get() == 'Teacher':
            Id = Id_entry.get()
            password = password_entry.get()
            pass_check = cursor.execute("SELECT password FROM Teacher WHERE teacher_id = ?", (Id,)).fetchall()
            if pass_check[0][0] == password:
                messagebox.showinfo("Login Successful", "Welcome, {}!".format(Id))
            else:
                messagebox.showerror("Login Failed", "Invalid Id or password.")
        else:
            messagebox.showinfo("Login Failed", "Select Student or Teacher")

def remove_widgets():
    for widget in window.winfo_children():
        widget.destroy()

def StudentPage1():
    remove_widgets()
    


# class Student(User):
#     def __init__(self, password, first_name, last_name):
#         super().__init__(password, first_name, last_name)
#         #self.student_id = 


def Loginpage():
    login_frame = ttk.Frame(window)
    login_frame.pack()  

    ttk.Label(login_frame, text='Student House Points', font='Impact 50').pack(pady=50)

    input_frame = ttk.Frame(login_frame)
    input_frame.pack()

    ttk.Label(input_frame, text='Id', font='Impact 12').grid(row=0, column=0)
    ttk.Label(input_frame, text='Password', font='Impact 12').grid(row=1, column=0)
    Id_entry = ttk.Entry(input_frame)
    Id_entry.grid(row=0, column=1, padx=5, pady=10)
    password_entry = ttk.Entry(input_frame, show='*')
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    selected_value = tk.StringVar()
    options = ["Teacher", "Student"]
    combobox = ttk.Combobox(input_frame, values=options, state='readonly', textvariable=selected_value)
    combobox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    combobox.set("Select an option")

    ttk.Button(input_frame, text='Enter', command=lambda:User.login(selected_value, Id_entry, password_entry)).grid(row=3, columnspan=2, pady=10)

if __name__ == "__main__":
    from House_points_database import database
    database()
    Loginpage()
    window.mainloop()
