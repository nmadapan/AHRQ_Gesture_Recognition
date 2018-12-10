import Tkinter as tk

def mmWindow():
    mmWindow = tk.Tk()
    mmWindow.geometry('600x600')

mWindow = tk.Tk()
# You can set any size you want
mWindow.geometry('500x500+0+0')
mWindow.title('DMX512 Controller')

wtitle = tk.Label(mWindow, text="Pi DMX", fg='blue')
wtitle.grid(row=0, column=1)

# You can set any height and width you want
mmbutton = tk.Button(mWindow, height=50, width=20, text="Main Menu", command=mmWindow)
mmbutton2 = tk.Button(mWindow, height=50, width=20, text="Main Menu", command=mmWindow)
mmbutton3 = tk.Button(mWindow, height=50, width=20, text="Main Menu", command=mmWindow)
mmbutton.grid(row=1, column=1)
mmbutton2.grid(row=2, column=1)
mmbutton3.grid(row=3, column=1)

mWindow.mainloop()
