import tkinter as tk
import dashboard


class MainPage:
    def __init__(self, root):
        self.root = root
        win_width = 280
        win_height = 180
        #situate window in the middle of screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        win_x_pos = str(int((screen_width/2)-(win_width/2)))
        win_y_pos = str(int((screen_height/2)-(win_height/2)))
        self.geom_info = (str(win_width)+'x'+str(win_height)+'+'+win_x_pos+'+'+win_y_pos)
        self.root.geometry(self.geom_info)
        self.root.resizable(False, False)
        self.root.title('Welcome')
        self.widgets()

    def widgets(self):
        login_label = tk.Label(self.root, text='Welcome', font=('',20))
        login_label.grid(row=0, column=1, sticky='WE', pady=(10,0))
        login_label = tk.Label(self.root, text='to your Receipt Manager')
        login_label.grid(row=1, column=1, sticky='WE')

        login_but = tk.Button(self.root, text='Enter', command=self.login_win, font=('',15), width=5)
        login_but.grid(row=2, column=1, pady=15, sticky='NSEW')

        close_but = tk.Button(self.root, text='Close', command=self.close_win)
        close_but.grid(row=3, column=1, pady=(0,10))

        self.root.grid_columnconfigure((0,2), weight=1)

    def login_win(self):
        self.root.withdraw()
        dashboard.Dashboard(self.root)

    def close_win(self):
        self.root.destroy()

def main():
    try:
        root = tk.Tk()
        MainPage(root)
        root.mainloop()

    except:
        root = tk.Tk()
        MainPage(root)
        root.mainloop()

if __name__ == '__main__':
    main()
