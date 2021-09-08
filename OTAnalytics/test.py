import tkinter as tk

root = tk.Tk()

cv = tk.Canvas(root, height=800, width=800)
cv.pack()

def onclick(event):
    item = cv.find_closest(event.x, event.y)

    current_color = cv.itemcget(item, 'fill')

    if current_color == 'black':
        cv.itemconfig(item, fill='white')

    else:
        cv.itemconfig(item, fill='black')


cv.bind('<Button-1>', onclick)

cv.create_line(50, 50, 60, 60, width=2)

cv. create_rectangle(80, 80, 100, 100)

root.mainloop()