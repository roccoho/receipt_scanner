import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox as mb
import edit
import json
import os
import receipt_info
import manage_receipt
import copy
import rules
import math

class Dashboard(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self)
        self.root = root
        win_width = 540
        win_height = 700
        #situate window in the middle of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_x_pos = str(int((screen_width/2)-(win_width/2)))
        win_y_pos = str(int((screen_height/2)-(win_height/2)))
        self.geom_info = str(win_width)+'x'+str(win_height)+'+'+win_x_pos+'+'+win_y_pos
        self.geometry(self.geom_info)
        self.resizable(False, False)
        self.title('Dashboard')
        self.widgets()

    def widgets(self):
        self.frame_height = 520
        self.bg_frame = tk.Frame(self)
        self.bg_frame.pack(expand='YES', fill='both')

        self.delete_but = tk.Button(self.bg_frame, text='Delete\nReceipt', command=self.delete_receipt)
        self.delete_but.grid(row=4, column=5, sticky='E')

        self.logout_but = tk.Button(self.bg_frame, text='Exit', command=self.logout)
        self.logout_but.grid(row=4, column=1, sticky='W')

        self.upload_but = tk.Button(self.bg_frame, text='Upload\nReceipt',command=self.upload_img)
        self.upload_but.grid(row=4, column=3, sticky='W')

        self.searchBar = tk.Entry(self.bg_frame, width=40)
        self.searchBar.grid(row=0, column=3, sticky='EW', pady=10, columnspan=2)
        self.searchBar.bind('<Return>', self.search_receipt2)

        self.searchBut = tk.Button(self.bg_frame, text='Search', command=self.search_receipt)
        self.searchBut.grid(row=0, column=5, pady=10)

        self.sortOpt = ttk.Combobox(self.bg_frame, state='readonly', values=('Upload Date','Receipt date','Total'), width=12)
        self.sortOpt.set('Upload Date')
        self.sortOpt.grid(row=0, column=1, pady=10, sticky='E')
        self.sortOpt.bind('<<ComboboxSelected>>', self.search_receipt2)

        self.orderBy = ttk.Combobox(self.bg_frame, state='readonly', values=('Descending','Ascending'), width=10)
        self.orderBy.set('Descending')
        self.orderBy.grid(row=0, column=2, pady=10)
        self.orderBy.bind('<<ComboboxSelected>>', self.search_receipt2)

        self.build_header()

        self.outline_frame = tk.Frame(self.bg_frame, highlightbackground='black', highlightthickness=1)
        self.outline_frame.grid(row=2, column=1, sticky='NEWS', columnspan=5, pady=(0,2))

        self.content_canvas = tk.Canvas(self.outline_frame)
        self.content_canvas.pack(expand='YES', fill='both')

        self.content_frame = tk.Frame(self.content_canvas)
        self.content_frame.grid(row=0, column=0, sticky='NEWS')
        self.content_canvas.create_window(0, 0, window=self.content_frame, anchor='nw')#attach content_frame to scrollbar

        self.open_file()
        self.new_data = manage_receipt.find_receipt(self.data, self.searchBar.get(), self.sortOpt.get(), self.orderBy.get())
        self.change_page(1)
        self.count_page_num()

        self.scroll = tk.Scrollbar(self.content_canvas, orient="vertical", command=self.content_canvas.yview)
        self.content_canvas.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=0, column=1, sticky='NSE')
        self.content_canvas.bind('<Configure>', self.scroll_to_frame)

        self.content_canvas.grid_columnconfigure(0, weight=1)
        self.content_canvas.grid_rowconfigure(0, weight=1)
        self.bg_frame.grid_columnconfigure((0,6), weight=1)
        self.bg_frame.grid_rowconfigure(2, minsize=self.frame_height)

        self.check_scroll()

    def logout(self):
        self.destroy()
        self.root.destroy()

    def delete_receipt(self):
        if self.counter > 0:
            delete = mb.askyesno('Delete Receipt', f'Delete {self.counter} receipt(s)?', parent=self)
            if delete:
                data_list = list(self.new_data)
                for i in range(len(self.boxstate_list)):
                    if self.boxstate_list[i].get() == 1:
                        try:
                            os.remove('saved_receipt\\'+self.data[data_list[self.pg-10+i]]['img_name'])
                        except:
                            pass
                        self.data.pop(data_list[self.pg-10+i], None)

                os.remove(rules.file_name)
                with open(rules.file_name, 'a') as f:
                    for i in self.data.items():
                        json.dump(dict([i]), f)
                        f.write('\n')
                self.open_file()
                self.change_page(1)
                self.count_page_num()

    def build_header(self):
        self.header_frame = tk.Frame(self.bg_frame, highlightbackground='black', highlightthickness=1)
        self.header_frame.grid(row=1, column=1, sticky='NEWS', columnspan=5)

        header_title = ['No', 'Date', 'Address', 'Total', ' ', ' ']
        header_width = [3, 9, 31, 6, 3, 2]  # preset column width for each header
        for i in range(len(header_title)):
            self.header = tk.Entry(self.header_frame, width=header_width[i], relief='groove', font=('bold'),
                                   justify='center')
            self.header.insert(tk.END, header_title[i])
            self.header.configure(state='readonly')
            self.header.grid(row=0, column=i, sticky='EW')
            if i == 4:
                self.counter_header = self.header #to count ticked checkboxes

    def search_receipt2(self, event):
        self.search_receipt()

    def search_receipt(self):
        self.new_data = manage_receipt.find_receipt(self.data, self.searchBar.get(), self.sortOpt.get(), self.orderBy.get())
        self.clear_frame()
        self.change_page(1)
        self.count_page_num()

    #def to_literal_string(self, string):
    #    return fr'{string}'

    def open_file(self):
        if os.path.exists(rules.file_name):
            self.data = {}
            with open(rules.file_name) as f:
                for line in f:
                    self.data |= json.loads(line)  # append to dictionary

            self.new_data = copy.deepcopy(self.data)

    def clear_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.counter = 0
        self.update_counter()
        self.insert_data()

    def insert_data(self):
        self.display_data = list(self.new_data.items())
        start = self.pg-10
        if self.pg > len(self.display_data):
            end = len(self.display_data)
        else:
            end = self.pg

        table_data = []
        try:
            counter = 1 + ((self.page_num_slider.get()-1)*10)
        except:
            counter = 1

        for i in range(start, end):
            j=[]
            j.append(counter)
            j.append(self.display_data[i][1]['date'])
            j.append(self.display_data[i][1]['address'])
            j.append(manage_receipt.final_total(self.display_data[i][1]['prices'], self.display_data[i][1]['price_text']))
            counter += 1
            table_data.append(j)

        columnWidth = [4, 11, 40, 5]
        self.boxstate_list = []
        for i in range(len(table_data)):
            for j in range(4):
                data_label = tk.Label(self.content_frame, text=table_data[i][j], width=columnWidth[j], justify='left', anchor='w', cursor='hand2')
                data_label.grid(row=i, column=j, sticky='NW')
                data_label.bind('<Button-1>', self.select_receipt)

            boxstate = tk.IntVar()
            self.counter = 0
            checkbut = tk.Checkbutton(self.content_frame, width=5, variable=boxstate, command=self.count_receipt)
            self.boxstate_list.append(boxstate)
            checkbut.grid(row=i, column=4, sticky='NW')

        self.check_scroll()

    def count_page_num(self):
        total_pg = math.ceil(len(self.new_data)/10)
        if total_pg < 1:
            total_pg = 1
            self.no_results()
        self.page_num_slider = tk.Scale(self.bg_frame, from_=1, to=total_pg, tickinterval=1, orient=tk.HORIZONTAL, command=self.change_page)
        self.page_num_slider.grid(row=3, column=1, columnspan=5, sticky='EW')
        self.page_num_slider.set(1)

    def no_results(self):
        no_res = tk.Label(self.content_frame, text='no results found', font=('',20))
        no_res.grid(row=1, column=0, columnspan=5, sticky='WE')

    def change_page(self, pg):
        self.pg = int(pg)*10
        self.clear_frame()

    def count_receipt(self):
        self.counter = 0
        for i in self.boxstate_list:
            if i.get() == 1:
                self.counter+=1
        self.update_counter()

    def update_counter(self):
        self.counter_header.configure(state='normal')
        self.counter_header.delete(0, tk.END)
        if self.counter == 0:
            self.counter_header.insert(tk.END, ' ')
        else:
            self.counter_header.insert(tk.END, str(self.counter))
        self.counter_header.configure(state='readonly')

    def select_receipt(self, event):
        current_row = event.widget.grid_info()['row']+(self.pg-10)
        receipt_id = list(self.new_data)[current_row]
        self.withdraw()
        receipt_info.Receipt_info(data=self.data, root=self.root, receipt_id=receipt_id, geom_info=self.geom_info)

    def check_scroll(self):
        self.content_frame.update()
        if self.content_frame.winfo_height() > self.frame_height:
            self.outline_frame.bind('<Enter>', self.yes_scroll)
            self.outline_frame.bind('<Leave>', self.no_scroll)

    def yes_scroll(self, event):
        self.content_canvas.bind_all('<MouseWheel>', self.allow_scroll)

    def no_scroll(self, event):
        self.content_canvas.unbind_all('<MouseWheel>')

    def allow_scroll(self, event):
        self.content_canvas.yview_scroll(int(-1*(event.delta//120)), 'units')

    def scroll_to_frame(self, event):
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox('all'))

    def upload_img(self):
        path = askopenfilename(parent=self)
        if len(path) > 0:
            if path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg'):
                self.withdraw()
                edit.Rotate(self.root, self.geom_info, path)
            else:
                mb.showerror('File Unsupported', 'File type not supported\n(Only .png, .jpg, and .jpeg are supported)', parent=self, default='ok')#FileUnsupported(self.root).grab_set()

#class FileUnsupported(tk.Toplevel):
#    def __init__(self, root):
#        tk.Toplevel.__init__(self)
#        self.root = root
#        win_width = 300
#        win_height = 100
#        screen_width = self.root.winfo_screenwidth()
#        screen_height = self.root.winfo_screenheight()
#        win_x_pos = str(int((screen_width/2)-(win_width/2)))
#        win_y_pos = str(int((screen_height/2)-(win_height/2)))
#        self.resizable(False, False)
#        self.geometry(str(win_width)+'x'+str(win_height)+'+'+win_x_pos+'+'+win_y_pos)
#        self.title('Invalid File Type')
#
#        self.info = tk.Label(self, text='')
#        self.info.grid(row=0, column=1, pady=10)
#
#        self.ok = tk.Button(self, text='OK', command=self.closeWindow, width=12)
#        self.ok.grid(row=1, column=1, pady=10)
#
#        self.grid_columnconfigure((0, 2), weight=1)
#
#    def closeWindow(self):
#        self.destroy()


