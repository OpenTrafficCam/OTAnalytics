from tkinter import *


def show_values(value=None):
    print(s1.get(), s2.get())


root = Tk()
s1 = Scale(root, from_=0, to=42, tickinterval=8, command=show_values)
#                                                ^^^^^^^^^^^^^^^^^^^
s1.set(19)
s1.pack()
s2 = Scale(
    root,
    from_=0,
    to=200,
    length=600,
    tickinterval=10,
    orient=HORIZONTAL,
    command=show_values,
)  # <---
s2.set(23)
s2.pack()
Button(root, text="Show", command=show_values).pack()
root.mainloop()