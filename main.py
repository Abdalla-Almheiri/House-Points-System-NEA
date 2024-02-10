import tkinter as tk
from tkinter import ttk  

window = tk.Tk()
window.title('House Points System')
window.geometry('1000x600')

def login_page():
        
    def on_combobox_change(event):
        selected_value = combobox.get()

    #Frames
    login_frame = ttk.Frame(window)
    login_frame.rowconfigure((0, 1), weight=1)
    login_frame.columnconfigure((0, 1), weight=1)
    
    #Widgets
    ttk.Label(window, text='Student House Points', font='Impact 50').pack(pady=50)
    login_frame.pack()

    ttk.Label(login_frame, text='Username', font='Impact 12').grid(row=0, column=0)
    ttk.Label(login_frame, text='Password', font='Impact 12').grid(row=1, column=0)
    ttk.Entry(login_frame).grid(row=0, column=1, padx=5, pady=10)
    ttk.Entry(login_frame).grid(row=1, column=1, padx=5, pady=5)
    
    #Variables
    options = ["Teacher", "Student"]
    combobox = ttk.Combobox(login_frame, values = options, state = 'readonly')
    combobox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    combobox.set("Teacher/Student")
    combobox.bind("<<ComboboxSelected>>", on_combobox_change)

    ttk.Button(window, text='Enter').pack()

if __name__ == "__main__":
    from House_points_database import database
    database()
    login_page()
    window.mainloop()
