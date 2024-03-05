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
            if user[0][1] == password:
                first_name = user[0][2]
                last_name = user[0][3]
                grade = user[0][4]
                StudentHouse = user[0][5]
                StudentPoints = user[0][6]
                student = Student(Id, password, first_name, last_name, grade, StudentHouse, StudentPoints)
                StudentHome(student)
            else:
                messagebox.showerror("Login Failed", "Invalid Id or password.")
        elif selected_role.get() == 'Teacher':
            Id = Id_entry.get()
            password = password_entry.get()
            user = cursor.execute("SELECT * FROM Teacher WHERE teacher_id = ?", (Id,)).fetchall()
            if user[0][1] == password:
                first_name = user[0][2]
                last_name = user[0][3]
            else:
                messagebox.showerror("Login Failed", "Invalid Id or password.")
        else:
            messagebox.showinfo("Login Failed", "Select Student or Teacher")

class Student(User):
        def __init__(self, Id, password, first_name, last_name, grade, StudentHouse, StudentPoints):
            super().__init__(password, first_name, last_name)
            self.student_id = Id
            self.student_first_name = first_name
            self.student_last_name = last_name
            self.student_grade = grade
            self.student_houseId = StudentHouse
            self.student_points = StudentPoints

        def CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_class, selected_house):
            if KeyError:
                messagebox.showerror('',"Account not created, all fields must be filled to create account")
            else:
                first_name = EnterFirstName.get()
                last_name = EnterLastName.get()
                password = EnterPassword.get()
                Id = EnterId.get()
                grade = selected_class.get()
                houseId = GetHouseID(selected_house)
                cursor.execute("INSERT INTO Student (student_ID, password, first_name, last_name, grade, house_id, total_points, leaderboard_position) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (Id, password, first_name, last_name, grade, houseId, 0, 0))
                conn.commit()
                for i in range(1,4):
                    cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (?, ?, ?)", (Id, i, 0))
                    conn.commit()
                messagebox.showinfo('',"Account created successfully")
                remove_widgets()
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
            remove_widgets()
            StudentHome(student)

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
    def __init__(self, Id, password, first_name, last_name):
        super().__init__(password, first_name, last_name)
        self.teacher_id = Id
        self.teacher_first_name = first_name
        self.teacher_last_name = last_name

def remove_widgets():
    for widget in window.winfo_children():
        widget.destroy()

def GetHouseID(selected_house):
    Houses = {"Gazelles": 1, "Oryxes": 2, "Foxes": 3, "Falcons": 4}
    houseId = Houses[selected_house]
    return houseId

def GetHouseColor(user):
    colors = {1: '#0A8B0B', 2: '#FFC300', 3: '#000000', 4:  '#0012C4'}
    color = colors[user.student_houseId]
    return color

def GetTokenId(token_name):
    tokens = {"Dress code exemption":1, "Cafeteria coupon":2, "One day off":3, "null":4}
    token_id = tokens[token_name]
    return  token_id

def GetTokenDesc(token_id):
    desc = cursor.execute("SELECT description FROM Token where token_id = ?",(token_id,)).fetchone()
    return desc[0]

def CreateStudentPage():
    remove_widgets()
    CreateAcc_frame = ctk.CTkFrame(window, fg_color='light grey')
    CreateAcc_frame.pack(fill='both', expand=True)

    ctk.CTkLabel(CreateAcc_frame, text='Enter your details', font=('Impact', 40), fg_color='light grey').place(x=350, y=100)

    ctk.CTkLabel(CreateAcc_frame, text='Enter your first name', font=('Impact', 17), fg_color='light grey').place(x=200, y=185)
    ctk.CTkLabel(CreateAcc_frame, text='Enter your last name', font=('Impact', 17), fg_color='light grey').place(x=525, y=185)
    ctk.CTkLabel(CreateAcc_frame, text='Enter an ID number', font=('Impact', 17), fg_color='light grey').place(x=200, y=230)
    ctk.CTkLabel(CreateAcc_frame, text='Select your class', font=('Impact', 17), fg_color='light grey').place(x=525, y=230)
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

    selected_class = ctk.StringVar()
    year_groups = ["9A", "9B", "9C", "9D", "10A", "10B", "10C", "10D", "11A", "11B", "11C", "11D", "12A", "12B", "12C", "12D", "13A", "13B", "13C", "13D"]
    combobox = ctk.CTkComboBox(CreateAcc_frame, values=year_groups,state='readonly', variable=selected_class)
    combobox.place(x=675, y=230)
    combobox.set("Classes (9-13)")

    selected_house = ctk.StringVar()
    options = ["Gazelles", "Oryxes","Foxes","Falcons"]
    Housecombobox = ctk.CTkComboBox(CreateAcc_frame, values=options, state='readonly', variable=selected_house)
    Housecombobox.place(x=675, y=275)
    
    submit_btn = ctk.CTkButton(CreateAcc_frame, text='Create account', bg_color='black', command=lambda:Student.CreateNewStudent(EnterFirstName, EnterLastName, EnterPassword, EnterId, selected_class, selected_house.get()))
    submit_btn.place(x=450, y=350)

    back_btn = ctk.CTkButton(CreateAcc_frame, command=lambda:Loginpage(), text='Back', font=('Impact', 20), text_color='black', fg_color='white', width=190, height=50, border_width=1)
    back_btn.place(x=3, y=500)

def CommonWidgets(Mainframe, student, StudentName, color):
    topbar_frame = ctk.CTkFrame(Mainframe, fg_color='white', border_width=2, border_color='black', width=800, height=60)
    topbar_frame.place(x=198, y=0)
    
    StudentName_label = ctk.CTkButton(topbar_frame, text=StudentName, font=('Impact', 25), text_color='black', fg_color='white', border_width=2, width=150, height=60, hover='disabled')
    StudentName_label.place(x=0, y=0)

    StudentPoints_label = ctk.CTkLabel(topbar_frame, text=("Total Points:  {}".format(student.student_points)), font=('Impact', 25), width=35, height=20)
    StudentPoints_label.place(x=600, y=10)
    options_frame = ctk.CTkFrame(Mainframe, fg_color=color, border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    back_btn = ctk.CTkButton(options_frame, command=lambda:StudentHome(student), text='Back', font=('Impact', 20), text_color='black', fg_color='light grey', width=190, height=50, border_width=1)
    back_btn.place(x=3, y=500)

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

    selected_role = ctk.StringVar()
    options = ["Teacher", "Student"]
    combobox = ctk.CTkComboBox(input_frame, values=options, state='readonly', variable=selected_role)
    combobox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    combobox.set("Select a role")

    ctk.CTkButton(input_frame, text='Submit', bg_color='black', command=lambda:User.login(selected_role, Id_entry, password_entry)).grid(row=3, columnspan=2, pady=10)
    ctk.CTkButton(input_frame, text='Create a student account', bg_color='black', command=lambda:CreateStudentPage()).grid(row=4, column=1, padx=10, pady=5)
    ctk.CTkButton(input_frame, text='Create a teacher account', bg_color='black').grid(row=4, column=0, padx=10,pady=5)

def StudentHome(student):
    remove_widgets()
    StudentName = str(student.student_first_name + ' ' + student.student_last_name)
    StudentClass = str(student.student_grade)
    color = GetHouseColor(student)

    StudentHome_frame = ctk.CTkFrame(window, fg_color='light grey')
    StudentHome_frame.pack(fill='both', expand=True)

    topbar_frame = ctk.CTkFrame(StudentHome_frame, fg_color='white', border_width=2, border_color='black', width=800, height=60)
    topbar_frame.place(x=198, y=0)
    
    StudentName_label = ctk.CTkButton(topbar_frame, text=StudentName, font=('Impact', 25), text_color='black', fg_color='white', border_width=2, width=150, height=60, hover='disabled')
    StudentName_label.place(x=0)

    StudentClass_label = ctk.CTkButton(topbar_frame, text=StudentClass, font=('Impact', 25), text_color='black', fg_color='white', border_width=2, width=150, height=60, hover='disabled')
    StudentClass_label.place(x=150)

    StudentPoints_label = ctk.CTkLabel(topbar_frame, text=("Total Points:  {}".format(student.student_points)), font=('Impact', 25), width=35, height=20)
    StudentPoints_label.place(x=600, y=10)

    options_frame = ctk.CTkFrame(StudentHome_frame, fg_color=color, border_width=2, border_color='black', width=200, height=600)
    options_frame.pack(side='left', fill='y', expand=False)

    manage_acc_btn = ctk.CTkButton(options_frame, command=lambda:StudentAccManagementPage(student, StudentName, color), text='Account\nManagement', font=('Impact', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    manage_acc_btn.place(x=3, y=275)

    empty_btn = ctk.CTkButton(options_frame, text='', font=('Impact', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    empty_btn.place(x=3, y=340)

    logout_btn = ctk.CTkButton(options_frame, command=lambda:logout(student), text='Log out', font=('Impact', 20), text_color='black', fg_color='light grey', border_width=1, width=190, height=50)
    logout_btn.place(x=3, y=400)

    Shop_btn = ctk.CTkButton(StudentHome_frame, command=lambda:TokenShopPage(student, color, StudentName), text='Token\nShop', font=('Impact', 25), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    Shop_btn.place(x=665, y=300)

    history_btn = ctk.CTkButton(StudentHome_frame, command=lambda:ViewPurchaseHistoryPage(student, StudentName, color), text='View\nPurchase\nHistory', font=('Impact', 25), text_color='black', fg_color='white', height= 150, width=150, border_width=1)
    history_btn.place(x=365, y=300)

def StudentAccManagementPage(student, StudentName, color):
    remove_widgets()
    StudentAccManagement_frame = ctk.CTkFrame(window, fg_color='light grey')
    StudentAccManagement_frame.pack(fill='both', expand=True)

    CommonWidgets(StudentAccManagement_frame, student, StudentName, color)

    ctk.CTkLabel(StudentAccManagement_frame, text ='First name', font=('Impact', 11), fg_color='light grey').place(x=340, y=200)
    FirstName_entry =  ctk.CTkEntry(StudentAccManagement_frame)
    FirstName_entry.insert(0,student.student_first_name)
    FirstName_entry.place(x=440, y=200)

    ctk.CTkLabel(StudentAccManagement_frame, text ='Last name', font=('Impact', 11), fg_color='light grey').place(x=340, y=225)
    LastName_entry = ctk.CTkEntry(StudentAccManagement_frame)
    LastName_entry.insert(0,student.student_last_name)
    LastName_entry.place(x=440, y=225)

    #!!Add more fields!! 

    ctk.CTkButton(StudentAccManagement_frame, text='Submit', command=lambda:student.UpdateStudentFields(FirstName_entry, LastName_entry, student)).place(x=500, y=300)

def ViewPurchaseHistoryPage(student, StudentName, color):
    remove_widgets()
    Records = cursor.execute("SELECT pt.purchase_id, t.token_name, pt.purchase_date FROM Purchase_token pt JOIN Token t ON pt.token_id = t.token_id").fetchall()
    PurchaseHistory_frame = ctk.CTkFrame(window, fg_color='light grey')
    PurchaseHistory_frame.pack(fill='both', expand=True)

    CommonWidgets(PurchaseHistory_frame, student, StudentName, color)

    PageTitle_label = ctk.CTkButton(PurchaseHistory_frame, text='My Purchases', font=('Impact', 50), text_color='black', fg_color='white', border_width=2, width=400, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=100)

    Records_frame = ctk.CTkScrollableFrame(window, bg_color='light grey', border_width=2, border_color='black', width=700, height=450)
    Records_frame.place(x=245, y=190)

    column1 = ctk.CTkButton(Records_frame, text='Purchase ID', font=('Impact', 17), text_color='black', fg_color='white', border_width=2, width=233, height=20, hover='disabled')
    column1.grid(row=0, column=0)

    column2 = ctk.CTkButton(Records_frame, text='Token', font=('Impact', 17), text_color='black', fg_color='white', border_width=2, width=233, height=20, hover='disabled')
    column2.grid(row=0, column=1)
    
    column3 = ctk.CTkButton(Records_frame, text='Date Purchased', font=('Impact', 17), text_color='black', fg_color='white', border_width=2, width=233, height=20, hover='disabled')
    column3.grid(row=0, column=2)

    for i, record in enumerate(Records):
        for j, value in enumerate(record):
            button = ctk.CTkButton(Records_frame, text=f'{value}', font=('Impact', 17), text_color='black', fg_color='white', border_width=2, width=233, height=20, hover='disabled')
            button.grid(row=i+1, column=j)

def TokenShopPage(student, color, StudentName):
    remove_widgets()
    token_name = {1:"Dress code exemption", 2:"Cafeteria coupon", 3:"One day off", 4:"null"}
    Shop_frame = ctk.CTkFrame(window, fg_color='light grey')
    Shop_frame.pack(fill='both', expand=True)

    CommonWidgets(Shop_frame, student, StudentName, color)

    PageTitle_label = ctk.CTkButton(Shop_frame, text='Token Shop', font=('Impact', 45), text_color='black', fg_color='white', border_width=2, width=250, height=50, hover='disabled')
    PageTitle_label.place(x=245, y=90)

    Token1_btn = ctk.CTkButton(Shop_frame, text='Dress Code\nExemption', command=lambda:ConfirmPurchaseWindow(token_name[1]), font=('Impact', 17), text_color='black', fg_color='white',height= 120, width=120, border_width=1)
    Token1_btn.place(x=400, y=190)

    Token1_desc = ctk.CTkLabel(Shop_frame, text=('{}'.format(GetTokenDesc(GetTokenId(token_name[1])))), font=('Impact', 17), width=100, height=2)
    Token1_desc.place(x=335, y=315)

    Token2_btn = ctk.CTkButton(Shop_frame, text='Cafeteria\nCoupon', command=lambda:ConfirmPurchaseWindow(token_name[2]), font=('Impact', 17), text_color='black', fg_color='white',height= 120, width=120, border_width=1)
    Token2_btn.place(x=650, y=190)

    Token2_desc = ctk.CTkLabel(Shop_frame, text=('{}'.format(GetTokenDesc(GetTokenId(token_name[2])))), font=('Impact', 17), width=100, height=2)
    Token2_desc.place(x=615, y=315)

    Token3_btn = ctk.CTkButton(Shop_frame, text='1 day\noff', command=lambda:ConfirmPurchaseWindow(token_name[3]), font=('Impact', 17), text_color='black', fg_color='white',height= 120, width=120, border_width=1)
    Token3_btn.place(x=400, y=390)

    Token3_desc = ctk.CTkLabel(Shop_frame, text=('{}'.format(GetTokenDesc(GetTokenId(token_name[3])))), font=('Impact', 17), width=100, height=2)
    Token3_desc.place(x=365, y=515)

    def ConfirmPurchaseWindow(token_name):
        token_id = GetTokenId(token_name)
        confirmPurchase_window = ctk.CTkToplevel(window, fg_color='light grey')
        confirmPurchase_window.geometry('750x150')
        confirmPurchase_window.title('Confirm purchase')
        confirmPurchase_window.resizable(False, False)

        ctk.CTkLabel(confirmPurchase_window, text=('Are you sure you want to purchase this "{}" token?').format(token_name), font=('Impact', 17)).place(x=125, y=35)

        confirm_btn = ctk.CTkButton(confirmPurchase_window, text='Yes', command=lambda: purchase_and_close(confirmPurchase_window, student, token_id))
        confirm_btn.place(x=175, y=85)

        cancel_btn = ctk.CTkButton(confirmPurchase_window, text='No', command=confirmPurchase_window.destroy)
        cancel_btn.place(x=425, y=85)

def purchase_and_close(window, student, token_id):
    student.PurchaseToken(token_id)
    StudentHome(student)
    window.destroy()

def logout(user):
    del user
    remove_widgets()
    Loginpage()

if __name__ == "__main__":
    # from House_points_database import database
    # database()
    Loginpage()
    window.mainloop()
