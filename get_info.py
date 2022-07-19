import re
import regex
import cv2 as cv
import rules
import google_api
import enchant
from enchant.tokenize import en
from enchant.checker import SpellChecker
import datetime
from datetime import datetime
from pytesseract import Output
import pytesseract as tes
#import csv#for testing
#import os

def preproc(img_name):
    img = cv.imread(img_name)
    min_width = 1024
    min_height = 768
    img_height, img_width = img.shape[0], img.shape[1]

    if img_width < min_width:  # enlarge
        ratio = min_width / img_width
        img_height= round(img_height * ratio)
        img_width = min_width
        dim = (img_width, img_height)
        img = cv.resize(img, dim, interpolation=cv.INTER_CUBIC)

    if img_height < min_height:
        ratio = min_height / img_height
        img_width = round(img_width * ratio)
        img_height = min_height
        dim = (img_width, img_height)
        img = cv.resize(img, dim, interpolation=cv.INTER_CUBIC)

    # tes.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # text = tes.pytesseract.image_to_string(img, config='--psm 4')
    # with open('hello.txt', 'w') as f:
    #    f.write(text)
    # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # img = cv.GaussianBlur(img, (5,5), 0)
    # img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 3)
    # cv.imwrite('preproc.png', img) #testing
    # text = tes.pytesseract.image_to_string(img)
    # with open('hello.txt', 'w') as f:
    #   f.write(text)

    cv.imwrite(img_name, img)
    return img_height, img_width


def last_index_of_spaced_words(word_found, b_text):
    word_list = word_found.split()
    for i in range(len(b_text)-len(word_list)+1):
        for j in range(len(word_list)):
            if b_text[i+j].lower() != word_list[j].lower():
                break
        else:
            return i+len(word_list)-1


def find_index(b, word, type=None):
    if type:
        if ' ' in word:
            return b[type][last_index_of_spaced_words(word, b['text'])]
        else:
            for i, text in enumerate(b['text']):
                if regex.search(word, text, re.IGNORECASE):
                    return b[type][i]
    else:
        if ' ' in word:
            return last_index_of_spaced_words(word, b['text'])
        else:
            for i, text in enumerate(b['text']):
                if regex.search(word, text, re.IGNORECASE):
                    return i


def find_element(b, text, rule):
    element_found = regex.search(rule, text, re.IGNORECASE)
    element = ''
    element_line = -1
    if element_found:
        element = str(element_found.group(0))
        if 'o' in element.lower():
            element = element.lower().replace('o','0')

        element_block = find_index(b, element, 'block_num')
        if compare_with_addr_block(b, text, element_block):
            element_line = find_index(b, element, 'line_num')

    return element, element_line


def compare_with_addr_block(b, text, block_compared):
    addr_found = regex.search(rules.address, text, re.IGNORECASE)
    if addr_found:
        addr_found = addr_found.group(0)
        addr_block = find_index(b, addr_found, 'block_num')
        if addr_block == block_compared:
            return True
    else:
        return False


def find_address(b, text, im_height, **skip_lines):
    addr_found = regex.search('Malaysia', text, re.IGNORECASE)#country first
    if not addr_found:
        addr_found  = regex.search(rules.address, text, re.IGNORECASE)#states second
        if not addr_found: #search for cities if states not found
            with open('cities.txt') as file:
                for city in file:
                    addr_found = regex.search(city.rstrip('\n'), text, re.IGNORECASE)
                    if addr_found:
                        break

    address = ''
    if addr_found:
        addr_found = addr_found.group(0)
        addr_index = find_index(b, addr_found)
        addr_line = find_index(b, addr_found, 'line_num')#last address line
        if b['coor'][addr_index][0]['y'] < im_height / 2: # address at top half of img
            for i, text in enumerate(b['text']):
                if b['line_num'][i] not in skip_lines.values():#skip phone/date/time lines
                    if b['line_num'][i] > addr_line:
                        break
                    elif b['line_num'][i] == b['line_num'][i - 1]:#words lie in the same line
                        address = address + text + ' '
                    elif b['line_num'][i] != b['line_num'][i - 1]:#words lie in the different line
                        address = address + '\n' + text + ' '
        else:#address at bottom half
            addr_block = find_index(b, addr_found, 'block_num')
            for i, text in enumerate(b['text']):
                if b['block_num'][i] == addr_block:#uses block defined by GCV
                    if b['line_num'][i] not in skip_lines.values():
                        if b['line_num'][i] > addr_line:
                            break
                        elif b['line_num'][i] == b['line_num'][i - 1]:
                            address = address + text + ' '
                        elif b['line_num'][i] != b['line_num'][i - 1]:
                            address = address + '\n' + text + ' '

    return remove_blank_lines(address)


def alpha_to_num(text):
    return text.lower().replace('o','0').replace('s','5').replace('z','2').replace(' ','').replace(',','.')


def remove_blank_lines(text):
    text_list = text.splitlines()
    text = ''
    for i in text_list:
        if i and not i.isspace():
            if text:
                text += '\n' + i
            else:
                text = i

    return text


def check_has_space(price_lines):
    for i in range(len(price_lines)-1):
        if price_lines[i] - price_lines[i+1] > -1:
            return True

    return False

#remove numbers
def check_eng_dict(price_text):
    eng_checker = enchant.checker.SpellChecker('en')
    full_text = ''
    for i in price_text:
        eng_checker.set_text(i) #check if there are unknown words in sentence
        for error in eng_checker:
            if error.word:
                text = google_api.google_search(i)
                full_text += ' ' + text
                break

    return full_text

def check_date_format(date):
    try:
        datetime_format = datetime.strptime(date, '%d/%m/%Y')
        return True
    except:
        return False

def date_format(date):
    if date:
        date_list = re.split(rules.date_format, date)
        if len(date_list[0])==4:
            year = date_list[0]
            date_list[0] = date_list[2]
            date_list[2] = year

        elif len(date_list[2])==2:
            date_list[2] = '20'+str(date_list[2])

        for i in range(len(date_list)):
            if len(date_list[i])==1:
                date_list[i] = '0'+date_list[i]

        date = '/'.join(date_list)
        has_date= True
    else:
        date = datetime.today().strftime('%d/%m/%Y')
        has_date = False

    return date, has_date

def google_search(search_term):#remove
    return google_api.google_search(search_term)


#def test():
    #print(new_data)
    # a = last_index_of_spaced_words('pulau pinang', ['pulau','tioman','pulau','pinang'])
    # print(a)
    #a = regex.search(rules.max_price, 'O.00', re.IGNORECASE)
    #if a:
    #    a=a.group(0)
    #print(o_to_zero('2 1 0'))

    #results = google_search('subway steak & chse sub', api_key, search_engine_id)
    #for result in results:
    #    print(result)


#def get_info(img):#
    #b, text = tes.image_to_data(img, config='--psm 4', output_type=Output.DICT)
    #b1 = copy.deepcopy(b)
    #par_num_to_line_num(b1)
    #b2 = copy.deepcopy(b1)
    #block_num_to_line_num(b2)

    #if os.path.exists('ori.csv'):#for testing
    #    os.remove('ori.csv')
    #with open('ori.csv', 'w') as outfile:
    #    writer = csv.writer(outfile)
    #    writer.writerow(['block_num','par_num','line_num','block_num','par_num','line_num','block_num','par_num','line_num','text'])
    #    writer.writerows(zip(b['block_num'], b['par_num'], b['line_num'],
    #                         b1['block_num'], b1['par_num'], b1['line_num'],
    #                         b2['block_num'], b2['par_num'], b2['line_num'], b2['text'], b['left']))
    #return b, text

#convert par_num into line_num to remove the need of par_num
#def par_num_to_line_num(b):
#    for i in range(len(b['text'])):
#        if b['block_num'][i] == b['block_num'][i-1]:
#            if b['par_num'][i] != b['par_num'][i - 1]:
#                value = b['line_num'][i-1]
#            if b['par_num'][i] > 1:
#                b['line_num'][i] += value + 1

#convert block_num into line_num to remove the need of block_num
#def block_num_to_line_num(b):
#    for i in range(len(b['text'])):
#        if b['block_num'][i] != b['block_num'][i - 1]:
#            value = b['line_num'][i-1]
#        if b['block_num'][i] > 1:
#            b['line_num'][i] += value + 1
