from tkinter import Tk
from tkinter import Label
import tkinter as tk
import time
import sys

root = Tk()
root.geometry("320x240")
root.title("DigiClock")
root.config(bg="white")

# Clock function, global display
def get_time():
    time_Var = time.strftime("%I:%M %p")
    date_Var = time.strftime("%Y-%m-%d")
    clock.config(text= time_Var)
    date.config(text= date_Var)
    clock.after(200, get_time)

# Display Parameters for the Clock
clock = Label(root, font= ("Calibri",10), bg="white", fg="black")
clock.place(x=34, y=20)
clkText= Label(text="Time:",font= ("Calibri",10), bg="white", fg="black")
clkText.place(x=2, y=20)

date = Label(root, font= ("Calibri",10), bg="white", fg="black")
date.place(x=34, y=2)
dteText= Label(text="Date:",font= ("Calibri",10), bg="white", fg="black")
dteText.place(x=2, y=2)
get_time()

# Focus Button
Fbtn = tk.Button(root, text="Focus",font= ("Calibri",10), bg="white", fg="black")
Fbtn.place(x=260, y=2)

# Profile Buttons
#EE= tk.Button(root, text="EE Intern",font= ("Calibri",10), bg="white", fg="black")
#EE.place(x=120, y=180)

#Skl = tk.Button(root, text="193b",font= ("Calibri",10), bg="white", fg="black")
#Fbtn.place(x=20, y=180)




root.mainloop()
