import tkinter as tk
from tkinter import messagebox as mb
from PIL import Image, ImageTk
import math
import copy
from datetime import datetime
import receipt_info
import dashboard
import os

class Rotate(tk.Toplevel):
    def __init__(self, root, geom_info, path):
        tk.Toplevel.__init__(self)
        self.root = root
        self.geom_info = geom_info
        self.path = path
        self.resizable(False, False)
        self.geometry(self.geom_info)
        self.title('Rotate Image')
        self.widgets()

    def widgets(self):
        self.canvas_width = 520
        self.canvas_height = 550
        self.angle = 0
        self.final_angle = 0
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, highlightthickness=1, highlightbackground="black")
        self.canvas.grid(row=0, column=1, pady=10, sticky='N', columnspan=3)
        #global
        self.ori_img = (Image.open(self.path)).convert('RGBA')
        self.new_img = copy.deepcopy(self.ori_img)
        self.new_img.thumbnail((self.canvas_width, self.canvas_height))#, Image.ANTIALIAS) omitted for performance
        self.tk_img = ImageTk.PhotoImage(self.new_img)
        self.canvas.create_image(self.canvas_width/2, self.canvas_height/2, image=self.tk_img, anchor='center')
        self.canvas.image = self.tk_img

        self.slider = tk.Scale(self, from_=-180, to=180, length=400, tickinterval=90, orient=tk.HORIZONTAL, command=self.rotate)
        self.slider.grid(row=1, column=1, sticky='S', columnspan=3)
        self.slider.bind('<Button-1>', self.draw_grid)
        self.slider.bind('<ButtonRelease-1>', self.delete_grid)
        self.slider.set(0)

        self.saveBut = tk.Button(self, text='Next', command=self.saveRot)
        self.saveBut.grid(row=2, column=3, padx=15, pady=15, sticky='E')

        self.flipped_hor = False
        self.flipHor = tk.Button(self, text='Horizontal Flip', command=self.horFlip)
        self.flipHor.grid(row=2, column=1, padx=15, pady=15, sticky='E')

        self.flipped_ver = False
        self.flipVer = tk.Button(self, text='Vertical Flip', command=self.verFlip)
        self.flipVer.grid(row=2, column=3, padx=15, pady=15, sticky='W')

        self.backBut = tk.Button(self, text='Back', command=self.back)
        self.backBut.grid(row=2, column=1, padx=15, pady=15, sticky='W')

        self.grid_columnconfigure((0,1,3,4), weight=1)

    def delete_grid(self, event):
        self.canvas.delete(self.ver_line)
        self.canvas.delete(self.hor_line)

    def draw_grid(self, event):
        self.ver_line = self.canvas.create_line(self.canvas_width/2, 0, self.canvas_width/2, self.canvas_height, width=1)
        self.hor_line = self.canvas.create_line(0, self.canvas_height/2, self.canvas_width, self.canvas_height/2, width=1)

    def horFlip(self):
        self.flipped_hor = not self.flipped_hor
        self.rotate(self.final_angle)

    def verFlip(self):
        self.flipped_ver = not self.flipped_ver
        self.rotate(self.final_angle)

    def rotate(self, angle):#display changes in canvas
        self.final_angle = int(angle)#scale value
        self.new_img = self.ori_img.rotate(self.final_angle, expand=1)#resample=Image.BICUBIC omitted for performance

        if self.flipped_hor:
            self.new_img = self.new_img.transpose(Image.FLIP_LEFT_RIGHT)
        if self.flipped_ver:
            self.new_img = self.new_img.transpose(Image.FLIP_TOP_BOTTOM)

        self.update_canvas()

    def saveRot(self):
        self.withdraw()#hide rotation window
        Crop(self, self.root, self.geom_info, self.new_img, self.final_angle, self.flipped_hor, self.flipped_ver, self.path)

    def back(self):
        self.destroy()
        dashboard.Dashboard(self.root)


    def update_canvas(self):
        self.new_img.thumbnail((self.canvas_width, self.canvas_height))  # , Image.ANTIALIAS)
        self.tk_img = ImageTk.PhotoImage(self.new_img)
        self.canvas.image = self.tk_img
        self.canvas.delete('IMG')
        self.canvas.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.tk_img, anchor='center')
        self.draw_grid('')

class Crop(tk.Toplevel):
    def __init__(self, rotate, root, geom_info, new_img, final_angle, flipped_hor, flipped_ver, path):
        tk.Toplevel.__init__(self)
        self.root = root
        self.rotate = rotate
        self.geom_info = geom_info
        self.new_img = new_img
        self.final_angle = final_angle
        self.flipped_hor = flipped_hor
        self.flipped_ver = flipped_ver
        self.path = path
        self.resizable(False, False)
        self.geometry(self.geom_info)
        self.title('Crop Image')
        self.widgets()

    def widgets(self):
        self.canvas_width = 520
        self.canvas_height = 550
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, highlightthickness=1, highlightbackground="black")
        self.canvas.grid(row=0, column=1, pady=10, sticky='N', columnspan=3)
        global tk_img
        self.new_img.thumbnail((self.canvas_width, self.canvas_height))#, Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.new_img)
        self.canvas_im = self.canvas.create_image(self.canvas_width/2, self.canvas_height/2, image=self.tk_img, anchor='center')
        self.img_coor = self.canvas.bbox(self.canvas_im)

        self.dot = [[200, 200], [200, 350], [320, 350], [320, 200]]
        self.init_dot = copy.deepcopy(self.dot)
        self.draw_rect()

        self.info = tk.Label(self, text='Move the dots or rectangle to crop the photo.')
        self.info.grid(row=1, column=1, sticky='S', columnspan=3)

        self.info = tk.Label(self, text='Irrelevant information at the top and bottom should be cropped out.', fg='blue', font=('',10,'underline'))
        self.info.grid(row=2, column=1, sticky='S', columnspan=3)
        self.info.bind('<Button-1>', self.crop_info)
        self.info.bind('<Enter>',self.change_red)
        self.info.bind('<Leave>',self.change_blue)

        self.saveBut = tk.Button(self, text='Save', command=self.saveCrop)
        self.saveBut.grid(row=3, column=3, padx=15, pady=15, sticky='E')

        self.fitAll = tk.Button(self, text='Fit all', command=self.fullBox)
        self.fitAll.grid(row=3, column=3, padx=15, pady=15, sticky='W')

        self.smallBox = tk.Button(self, text='Reset Box', command=self.resetBox)
        self.smallBox.grid(row=3, column=1, padx=15, pady=15, sticky='E')

        self.backBut = tk.Button(self, text='Back', command=self.back)
        self.backBut.grid(row=3, column=1, padx=15, pady=15, sticky='W')

        self.grid_columnconfigure((0,1,3,4), weight=1)

    def change_red(self, event):
        event.widget.config(fg='red')

    def change_blue(self, event):
        event.widget.config(fg='blue')

    def crop_info(self,event):
        mb.showwarning('Crop Information','Examples of RELEVANT information are:'+
                                                         '\n-Store name' +
                                                         '\n-Address'+
                                                         '\n-Phone number'+
                                                         '\n-Date'+
                                                         '\n-Time' +
                                                         '\n-Prices'+
                                                         '\n-Item names'+
                                                         '\n-Total'+
                                                         '\n '+
                                                         '\nIt is advised to crop out background and information that are not listed.'+
                                                         '\n*Additional information can be added later in the \'Annotation\' field.', icon="question", parent=self, default='ok')
        #CropInfo(self).grab_set()

    def resetBox(self):
        self.dot = copy.deepcopy(self.init_dot)
        self.delete_rect()
        self.draw_rect()

    def fullBox(self):
        self.dot[0] = [self.img_coor[0], self.img_coor[1]]
        self.dot[1] = [self.img_coor[0], self.img_coor[3]]
        self.dot[2] = [self.img_coor[2], self.img_coor[3]]
        self.dot[3] = [self.img_coor[2], self.img_coor[1]]
        self.delete_rect()
        self.draw_rect()

    def moveDot(self, event):
        if (event.x > self.img_coor[0] and
            event.x < self.img_coor[2] and
            event.y > self.img_coor[1] and
            event.y < self.img_coor[3]):
            self.dot[self.dot_num][0] = event.x
            self.dot[self.dot_num][1] = event.y
            if self.dot_num == 0:
                self.dot[1][0] = event.x
                self.dot[3][1] = event.y
            elif self.dot_num == 1:
                self.dot[0][0] = event.x
                self.dot[2][1] = event.y
            elif self.dot_num == 2:
                self.dot[3][0] = event.x
                self.dot[1][1] = event.y
            elif self.dot_num == 3:
                self.dot[2][0] = event.x
                self.dot[0][1] = event.y

            self.delete_rect()
            self.draw_rect()

    def stopObj(self, event):
        self.canvas.unbind('<Motion>')

    def clickDot0(self, event):
        self.dot_num = 0
        self.canvas.bind('<Motion>', self.moveDot)

    def clickDot1(self, event):
        self.dot_num = 1
        self.canvas.bind('<Motion>', self.moveDot)

    def clickDot2(self, event):
        self.dot_num = 2
        self.canvas.bind('<Motion>', self.moveDot)

    def clickDot3(self, event):
        self.dot_num = 3
        self.canvas.bind('<Motion>', self.moveDot)

    def delete_rect(self):
        self.canvas.delete(self.dot0)
        self.canvas.delete(self.dot1)
        self.canvas.delete(self.dot2)
        self.canvas.delete(self.dot3)
        self.canvas.delete(self.rectangle)

    def clickRect(self, event):
        self.mouse_x_pos = event.x
        self.mouse_y_pos = event.y
        self.canvas.bind('<Motion>', self.rectMove)

    def rectMove(self, event):
        self.rect_info()
        dist_x = event.x - self.mouse_x_pos
        dist_y = event.y - self.mouse_y_pos
        if (self.rect_bbox[0] > self.img_coor[0] and
            self.rect_bbox[2] < self.img_coor[2] and
            self.rect_bbox[1] > self.img_coor[1] and
            self.rect_bbox[3] < self.img_coor[3]):
            for i in self.dot:
                i[0] = i[0] + dist_x
                i[1] = i[1] + dist_y

        elif self.rect_bbox[0] <= self.img_coor[0]:#prevents rectangle from leaving image area
            for i in self.dot:
                i[0] = i[0] + 1

        elif self.rect_bbox[2] >= self.img_coor[2]:
            for i in self.dot:
                i[0] = i[0] - 1

        elif self.rect_bbox[1] <= self.img_coor[1]:
            for i in self.dot:
                i[1] = i[1] + 1

        elif self.rect_bbox[3] >= self.img_coor[3]:
            for i in self.dot:
                i[1] = i[1] - 1

        self.delete_rect()
        self.draw_rect()
        self.mouse_x_pos = event.x
        self.mouse_y_pos = event.y

    def draw_rect(self):
        size = 7
        self.rectangle = self.canvas.create_polygon([self.dot[0][0], self.dot[0][1],
                                                     self.dot[1][0], self.dot[1][1],
                                                     self.dot[2][0], self.dot[2][1],
                                                     self.dot[3][0], self.dot[3][1]],
                                                    fill='', outline='red')#, width=2
        self.dot0 = self.canvas.create_oval(self.dot[0][0]-size, self.dot[0][1]-size, self.dot[0][0]+size, self.dot[0][1]+size, fill='red', outline='red')
        self.dot1 = self.canvas.create_oval(self.dot[1][0]-size, self.dot[1][1]-size, self.dot[1][0]+size, self.dot[1][1]+size, fill='red', outline='red')
        self.dot2 = self.canvas.create_oval(self.dot[2][0]-size, self.dot[2][1]-size, self.dot[2][0]+size, self.dot[2][1]+size, fill='red', outline='red')
        self.dot3 = self.canvas.create_oval(self.dot[3][0]-size, self.dot[3][1]-size, self.dot[3][0]+size, self.dot[3][1]+size, fill='red', outline='red')
        self.canvas.tag_bind(self.rectangle, '<Button-1>', self.clickRect)
        self.canvas.tag_bind(self.dot0, '<Button-1>', self.clickDot0)
        self.canvas.tag_bind(self.dot1, '<Button-1>', self.clickDot1)
        self.canvas.tag_bind(self.dot2, '<Button-1>', self.clickDot2)
        self.canvas.tag_bind(self.dot3, '<Button-1>', self.clickDot3)
        self.canvas.bind('<ButtonRelease-1>', self.stopObj)

    def rect_info(self):
        rect_coor = self.canvas.coords(self.rectangle)
        self.rect_bbox = [rect_coor[0], rect_coor[1], rect_coor[4], rect_coor[5]]

    def saveCrop(self):
        self.ori_img = (Image.open(self.path))
        image_format = self.ori_img.format #to preserve original file format when saving
        self.ori_img = self.ori_img.rotate(self.final_angle, expand=1, resample=Image.BICUBIC)

        if self.flipped_hor:
            self.ori_img = self.ori_img.transpose(Image.FLIP_LEFT_RIGHT)
        if self.flipped_ver:
            self.ori_img = self.ori_img.transpose(Image.FLIP_TOP_BOTTOM)

        crop_area = self.calc_crop_area()
        self.ori_img = self.ori_img.crop(crop_area)

        receipt_id = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        img_name = receipt_id + '.' + image_format.lower()

        if not os.path.exists('saved_receipt'):#create saved_receipt folder
            os.makedirs('saved_receipt')

        self.ori_img.save('saved_receipt\\'+img_name, subsampling=0, quality=100, format=image_format)

        self.withdraw()#hide crop window
        receipt_info.Receipt_info(crop=self, rotate=self.rotate, root=self.root, geom_info=self.geom_info,
                                  receipt_id=receipt_id, img_name=img_name, first_time=True)

    def calc_crop_area(self):
        self.rect_info() #list of rectangle coordinates in canvas

        #convert rect coord on canvas to coord on image
        rect_bbox_dist = [self.rect_bbox[0] - self.img_coor[0],
                          self.rect_bbox[1] - self.img_coor[1],
                          self.rect_bbox[2] - self.img_coor[0],
                          self.rect_bbox[3] - self.img_coor[1]]

        if self.img_coor[0] == 0: # image width reduced to canvas width
            ratio = self.ori_img.size[0]/self.canvas_width

        else: # image height reduced to canvas height
            ratio = self.ori_img.size[1]/self.canvas_height

        rect_bbox_dist = [math.floor(i * ratio) for i in rect_bbox_dist]
        return tuple(rect_bbox_dist)


    def back(self):
        self.destroy()
        self.rotate.update()
        self.rotate.deiconify()

class CropInfo(tk.Toplevel):
    def __init__(self, prev_win):
        self.prev_win = prev_win
        win_width = 400
        win_height = 250
        screen_width = self.prev_win.winfo_screenwidth()
        screen_height = self.prev_win.winfo_screenheight()
        win_x_pos = str(int((screen_width/2)-(win_width/2)))
        win_y_pos = str(int((screen_height/2)-(win_height/2)))
        tk.Toplevel.__init__(self)
        self.resizable(False, False)
        self.geometry(str(win_width)+'x'+str(win_height)+'+'+win_x_pos+'+'+win_y_pos)
        self.title('Crop Information')
        self.widgets()

    def widgets(self):
        self.info = tk.Label(self, justify='left', text=('Examples of RELEVANT information are:'+
                                                         '\n-Store name' +
                                                         '\n-Address'+
                                                         '\n-Phone number'+
                                                         '\n-Date'+
                                                         '\n-Time' +
                                                         '\n-Prices'+
                                                         '\n-Item names'+
                                                         '\n-Total'+
                                                         '\n '+
                                                         '\nIt is advised to crop out background and information that are not listed.'+
                                                         '\n*Additional information can be added later in the \'Annotation\' field.'))
        self.info.grid(row=0, column=1, pady=10)

        self.ok = tk.Button(self, text='OK', command=self.closeWindow, width=12)
        self.ok.grid(row=1, column=1, pady=10)
        self.grid_columnconfigure((0, 2), weight=1)

    def closeWindow(self):
        self.destroy()