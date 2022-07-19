import re
import regex
import tkinter as tk
from tkinter import messagebox as mb
import get_info
import get_price
import ocr
import rules
import json
import os.path
import os
import dashboard
from PIL import Image, ImageTk

class Receipt_info(tk.Toplevel):
    def __init__(self, crop=None, rotate=None, root=None, geom_info=None, receipt_id=None, img_name=None, first_time=False, data=None):
        tk.Toplevel.__init__(self)
        self.first_time = first_time
        self.data = data
        self.crop = crop
        self.root = root
        self.rotate = rotate
        self.geom_info = geom_info
        self.receipt_id = receipt_id
        self.img_name = img_name
        self.resizable(False, False)
        self.geometry(self.geom_info)
        self.title('Receipt Information')
        self.extract_info()
        self.widgets()

    def widgets(self):
        self.frame_height = 630
        self.content_canvas = tk.Canvas(self, highlightthickness=0)
        self.content_canvas.grid(row=0, column=0, sticky='NEWS', columnspan=3)

        self.content_frame = tk.Frame(self.content_canvas, highlightthickness=0)
        self.content_frame.grid(row=0, column=0, sticky='NEWS')
        self.content_canvas.create_window(0, 0, window=self.content_frame, anchor='nw')

        self.scroll = tk.Scrollbar(self.content_canvas, orient='vertical', command=self.content_canvas.yview)
        self.content_canvas.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=0, column=1, sticky='NSE')
        self.content_canvas.bind('<Configure>', self.scrollToFrame)

        self.date_label = tk.Label(self.content_frame, text='Date: ')
        self.date_label.grid(row=0, column=0, sticky='W', pady=10, padx=10)
        self.date_box = tk.Entry(self.content_frame)
        self.date_box.insert(tk.END, self.date)
        self.date_box.grid(row=0, column=1, sticky='W', pady=10, padx=10)
        if self.first_time:
            if not self.has_date:
                self.no_date = tk.Label(self.content_frame, text='*Date not found, current date is used.')
                self.no_date.grid(row=0, column=3, sticky='W', columnspan=3)

        self.time_label = tk.Label(self.content_frame, text='Time: ')
        self.time_label.grid(row=1, column=0, sticky='W', pady=10, padx=10)
        self.time_box = tk.Entry(self.content_frame)
        self.time_box.insert(tk.END, self.time)
        self.time_box.grid(row=1, column=1, sticky='W', pady=10, padx=10)

        self.phone_label = tk.Label(self.content_frame, text='Phone Number: ')
        self.phone_label.grid(row=2, column=0, sticky='W', pady=10, padx=10)
        self.phone_box = tk.Entry(self.content_frame)
        self.phone_box.insert(tk.END, self.phone)
        self.phone_box.grid(row=2, column=1, sticky='W', pady=10, padx=10)

        self.address_label = tk.Label(self.content_frame, text='Address: ')
        self.address_label.grid(row=3, column=0, sticky='NW', pady=10, padx=10)
        self.address_box = tk.Text(self.content_frame, height=5, width=53, font=('Helvetica',9))
        self.address_box.insert(tk.END, self.address)
        self.address_box.grid(row=3, column=1, sticky='NW', rowspan=5, columnspan=6, pady=10, padx=10)

        self.item_label = tk.Label(self.content_frame, text='Items: ')
        self.item_label.grid(row=9, column=0, sticky='NW', pady=(5,0), padx=10)

        self.price_label = tk.Label(self.content_frame, text='Prices (RM): ')
        self.price_label.grid(row=9, column=4, sticky='NW', pady=(5,0), padx=10)

        self.price_text_box_list = []
        self.price_box_list = []
        row_num = 10
        for i in range(len(self.prices)):
            height = self.price_text[i].count('\n') + 1
            self.price_text_box = tk.Text(self.content_frame, height=height, width=50, font=('Helvetica', 9))
            self.price_text_box.insert(tk.END, self.price_text[i])
            self.price_text_box.grid(row=row_num, column=0, columnspan=4, sticky='W', pady=10, padx=(10,0), rowspan=height)
            self.price_text_box_list.append(self.price_text_box)

            self.price_box = tk.Text(self.content_frame, height=1, width=10, font=('Helvetica', 9))
            self.price_box.insert(tk.END, self.prices[i])
            self.price_box.grid(row=row_num, column=4, sticky='W', pady=10, padx=(10,0), columnspan=2)
            self.price_box_list.append(self.price_box)

            self.remove_price_but = tk.Button(self.content_frame, text='-')
            self.remove_price_but.grid(row=row_num, column=5, pady=10, padx=5, sticky='E')
            self.remove_price_but.config(command=lambda row=i: self.remove_price(row))

            self.add_price_but = tk.Button(self.content_frame, text='+')
            self.add_price_but.grid(row=row_num, column=6, pady=10, sticky='W')
            self.add_price_but.config(command=lambda row=i: self.add_price(row))

            row_num += height

        self.total_items = tk.Label(self.content_frame, text='Total items: '+str(len(self.prices)))
        self.total_items.grid(row=row_num+1, column=4, sticky='E', pady=10, padx=5, columnspan=3)

        self.annotation_label = tk.Label(self.content_frame, text='Annotation: ')
        self.annotation_label.grid(row=row_num+2, column=0, sticky='W', pady=10, padx=10)
        self.annotation_box = tk.Text(self.content_frame, height=5, width=53, font=('Helvetica', 9))
        self.annotation_box.insert(tk.END, self.annotation)
        self.annotation_box.grid(row=row_num+2, column=1, sticky='NW', rowspan=5, columnspan=6, pady=10, padx=10)

        date_time = self.receipt_id.split('_')
        date_time_text = date_time[0] + ' ' + date_time[1].replace('-',':')
        self.upload_date = tk.Label(self.content_frame, text='Upload date & time: '+date_time_text)
        self.upload_date.grid(row=row_num+8, column=0, sticky='W', pady=10, padx=10, columnspan=3)

        self.saveBut = tk.Button(self, text='Save', command=self.save)
        self.saveBut.grid(row=1, column=2, sticky='E', padx=10, pady=(20,10))

        self.backBut = tk.Button(self, text='Back', command=self.back)
        self.backBut.grid(row=1, column=0, sticky='W', padx=10, pady=(20,10))

        self.showImgBut = tk.Button(self, text='Show\nReceipt', command=self.showImg)
        self.showImgBut.grid(row=1, column=1)

        self.content_canvas.grid_columnconfigure(0, weight=1)
        self.content_canvas.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure(0, minsize=self.frame_height)

        self.checkScroll()

    def add_price(self, row):
        self.updateData()
        self.prices.insert(row+1, '')
        self.price_text.insert(row+1,'')
        self.content_frame.destroy()
        self.widgets()

    def remove_price(self, row):
        self.updateData()
        del self.prices[row]
        del self.price_text[row]
        self.content_frame.destroy()
        self.widgets()

    def back(self):
        self.destroy()
        if self.first_time:
            os.remove('saved_receipt\\'+self.img_name)
            self.crop.update()
            self.crop.deiconify()
        else:
            dashboard.Dashboard(self.root)

    def showImg(self):
        ShowImage(self.root, self.img_name)

    def updateData(self):
        self.phone = self.phone_box.get()
        self.date = self.date_box.get()
        self.time = self.time_box.get()
        self.address = self.address_box.get('1.0','end-1c')
        self.prices = []
        self.price_text = []
        for i in range(len(self.price_box_list)):
            self.price_text.append(self.price_text_box_list[i].get('1.0','end-1c'))
            self.prices.append(self.price_box_list[i].get('1.0','end-1c'))
        self.annotation = self.annotation_box.get('1.0', 'end-1c')

    def save(self):
        self.updateData()
        #inform which price line incorrect
        only_numbers = all(regex.search(rules.confirmed_price, price, re.IGNORECASE) for price in self.prices)
        if not get_info.check_date_format(self.date):
            mb.showerror('Date error', 'Date format is incorrect.\ndd/mm/yyyy', parent=self)
            #ErrorWin(self, 'Date error', 'Date format is incorrect.\ndd/mm/yyyy').grab_set()
        elif not only_numbers:
            mb.showerror('Price error', 'Price format is incorrect', parent=self)
            #ErrorWin(self, 'Price error', 'Price format is incorrect.').grab_set()
        else:
            self.prices = [get_info.alpha_to_num(price) for price in self.prices]
            if self.first_time:
                new_data = {}
                new_data[self.receipt_id] = {}
                new_data[self.receipt_id]['img_name'] = self.img_name
                new_data[self.receipt_id]['phone'] = self.phone
                new_data[self.receipt_id]['date'] = self.date
                new_data[self.receipt_id]['time'] = self.time
                new_data[self.receipt_id]['address'] = self.address
                new_data[self.receipt_id]['price_text'] = self.price_text
                new_data[self.receipt_id]['prices'] = self.prices
                new_data[self.receipt_id]['annotation'] = self.annotation
                new_data[self.receipt_id]['full_text'] = (self.text + ' '
                                                          + self.img_name + ' '
                                                          + get_info.check_eng_dict(self.price_text) + '|'
                                                          + self.phone + ' '
                                                          + self.date + ' '
                                                          + self.time + ' '
                                                          + self.address + ' '
                                                          + str(self.price_text) + ' '
                                                          + str(self.prices) + ' '
                                                          + self.annotation)
                with open(rules.file_name, 'a') as f:
                    json.dump(new_data, f)
                    f.write('\n')
            else:
                self.data[self.receipt_id]['phone'] = self.phone
                self.data[self.receipt_id]['date'] = self.date
                self.data[self.receipt_id]['time'] = self.time
                self.data[self.receipt_id]['address'] = self.address
                self.data[self.receipt_id]['price_text'] = self.price_text
                self.data[self.receipt_id]['prices'] = self.prices
                self.data[self.receipt_id]['annotation'] = self.annotation
                self.data[self.receipt_id]['full_text'] = (self.data[self.receipt_id]['full_text'].split('|')[0] + '|'
                                                           + self.phone + ' '
                                                           + self.date + ' '
                                                           + self.time + ' '
                                                           + self.address + ' '
                                                           + str(self.price_text) + ' '
                                                           + str(self.prices) + ' '
                                                           + self.annotation)
                os.remove(rules.file_name)
                with open(rules.file_name, 'a') as f:
                    for i in self.data.items():
                        json.dump(dict([i]), f)
                        f.write('\n')

            if self.first_time:
                self.crop.destroy()
                self.rotate.destroy()

            self.destroy()
            dashboard.Dashboard(self.root)

    def checkScroll(self):
        self.content_frame.update()
        if self.content_frame.winfo_height() > self.frame_height:
            self.content_frame.bind('<Enter>', self.yesScroll)
            self.content_frame.bind('<Leave>', self.noScroll)

    def scrollToFrame(self, event):
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox('all'))

    def yesScroll(self, event):
        self.content_canvas.bind_all('<MouseWheel>', self.allowScroll)

    def noScroll(self, event):
        self.content_canvas.unbind_all('<MouseWheel>')

    def allowScroll(self, event):
        self.content_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

    def extract_info(self):
        if self.first_time:
            im_height, im_width = get_info.preproc('saved_receipt\\'+self.img_name)
            b, self.text, state = ocr.get_ocr('saved_receipt\\'+self.img_name)
            if not self.text:
                if state == 'internet':   # no internet
                    mb.showwarning('No internet', 'There is no internet connection', icon='question', parent=self, default='ok')
                if state == 'empty':  #no OCR output
                    mb.showwarning('Output error', 'No words detected in image.', icon='question', parent=self, default='ok')
                self.text = ''
                self.date, self.has_date = get_info.date_format('')
                self.phone = ''
                self.time = ''
                self.address = ''
                self.price_text = ['']
                self.prices = ['']
                self.annotation = ''
            else:
                self.phone, phone_line = get_info.find_element(b, self.text, rules.phone)
                self.date, date_line = get_info.find_element(b, self.text, rules.date)
                self.date, self.has_date = get_info.date_format(self.date)
                self.time, time_line = get_info.find_element(b, self.text, rules.time)
                self.address = get_info.find_address(b, self.text, im_height, phone_line=phone_line, date_line=date_line, time_line=time_line)
                self.price_text, self.prices = get_price.find_prices(b, im_width, im_height)
                self.annotation = ''

        else:
            self.img_name = self.data[self.receipt_id]['img_name']
            self.phone = self.data[self.receipt_id]['phone']
            self.date = self.data[self.receipt_id]['date']
            self.time = self.data[self.receipt_id]['time']
            self.address = self.data[self.receipt_id]['address']
            self.price_text = self.data[self.receipt_id]['price_text']
            self.prices = self.data[self.receipt_id]['prices']
            self.annotation = self.data[self.receipt_id]['annotation']

class ShowImage(tk.Toplevel):
    def __init__(self, root, img_name):
        tk.Toplevel.__init__(self)
        self.title(img_name)
        try:
            img = Image.open('saved_receipt\\'+img_name)
            screen_width = root.winfo_screenwidth()*0.9
            screen_height = root.winfo_screenheight()*0.9

            if img.width > screen_width or img.height > screen_height:
                img.thumbnail((screen_width, screen_height))
            self.geometry(str(img.width)+'x'+str(img.height))

            tk_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(self, image=tk_img)
            img_label.pack()
            img_label.img = tk_img
        except:
            NoImage()
            self.destroy()

class ErrorWin(tk.Toplevel):
    def __init__(self, prev_win, title_, text_):
        self.prev_win = prev_win
        win_width = 300
        win_height = 100
        screen_width = self.prev_win.winfo_screenwidth()
        screen_height = self.prev_win.winfo_screenheight()
        win_x_pos = str(int((screen_width/2)-(win_width/2)))
        win_y_pos = str(int((screen_height/2)-(win_height/2)))
        tk.Toplevel.__init__(self)
        self.resizable(False, False)
        self.geometry(str(win_width)+'x'+str(win_height)+'+'+win_x_pos+'+'+win_y_pos)
        self.title(title_)

        self.info = tk.Label(self, text=text_)
        self.info.grid(row=0, column=1, pady=10)

        self.ok = tk.Button(self, text='OK', command=self.closeWindow, width=12)
        self.ok.grid(row=1, column=1, pady=10)

        self.grid_columnconfigure((0, 2), weight=1)

    def closeWindow(self):
        self.destroy()

class NoImage(tk.Toplevel):
    def __init__(self):
        win_width = 300
        win_height = 100
        tk.Toplevel.__init__(self)
        self.resizable(False, False)
        self.geometry(str(win_width)+'x'+str(win_height))
        self.title('No Image')
        self.info = tk.Label(self, text='Image not found.')
        self.info.grid(row=0, column=1, pady=10)

        self.ok = tk.Button(self, text='OK', command=self.closeWindow, width=12)
        self.ok.grid(row=1, column=1, pady=10)

        self.grid_columnconfigure((0, 2), weight=1)

    def closeWindow(self):
        self.destroy()