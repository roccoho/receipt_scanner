import regex
import re
import rules
import get_info

def find_prices(b, im_width, im_height):
    price_text_list=[]
    max_price_index = get_max_price_index(b, im_width, im_height)
    if max_price_index:#found highest price
        price_lines = get_price_lines(b, max_price_index, im_width)#get all prices
        if price_lines:#found prices
            first_price_line = price_lines[0]
            last_price_line = price_lines[-1]
            header_line = get_price_header_line(b, first_price_line)
            text_to_bottom_price = item_to_price_above_below(b, header_line, first_price_line)
            price_text_list = get_price_text_list(b, header_line, last_price_line)
            has_price = check_price_in_string(price_text_list)#boolean list to check if each element has price
            price_text_list = combine_item_names(price_text_list, text_to_bottom_price, has_price)
            price_text, prices = separate_price_and_item(price_text_list)

    if not price_text_list:
        prices=[]
        prices.append('')
        price_text=[]
        price_text.append('')

    return price_text, prices

def check_has_space(price_lines):
    for i in range(len(price_lines)-1):
        if price_lines[i+1] - price_lines[i] != 1:
            return True
    else:
        return False

def get_price_text_list(b, header_line, last_price_line):
    add_one_index(b) #padding for loop in case the last line is the a price item
    price_text_list=[]
    price_text = ''
    for i in range(b['line_num'].index(header_line+1), b['line_num'].index(last_price_line+1)+1):
        if b['line_num'][i] == b['line_num'][i - 1]:
            price_text += b['text'][i] + ' '
        else:
            if not price_text.isspace() and price_text:
                price_text_list.append(price_text)
            price_text = b['text'][i] + ' '

    return price_text_list

def get_max_price_index(b, im_width, im_height):
    # get highest price to get column size
    max_price_index = -1
    max_price = -1
    for i, j in enumerate(b['text']):
        if b['coor'][i][0]['x'] > im_width/2 and b['coor'][i][0]['y'] > im_height/2:
            max_price_found = regex.search(rules.max_price, j)
            if max_price_found:
                price = str(max_price_found.group(0))
                price = float(get_info.alpha_to_num(price))
                if price > max_price:
                    max_price = price
                    max_price_index = i

    return max_price_index

#if an item name takes up more than one line, does it belong to the price above or below?
def item_to_price_above_below(b, header_line, first_price_line):
    text_to_bottom_price = False #by default, items without price at the right belongs to price in the bottom
    if header_line != -1: #check if there is header line
        if first_price_line - header_line > 1:# if there's a gap between price header and first price
            for i in range(b['line_num'].index(header_line + 1), b['line_num'].index(first_price_line)):
                if b['text'][i] and b['line_num'][i]!=first_price_line: #to confirm it is not an empty line
                    text_to_bottom_price = True
                    break

    return text_to_bottom_price

def get_price_lines(b, max_price_index, im_width):
    price_lines = []
    column_line = b['coor'][max_price_index][0]['x']-(0.2*im_width) #0.2 to for tilted img
    for i, lines in enumerate(b['line_num']):
        if b['coor'][i][0]['x'] >= column_line:
            all_price = regex.search(rules.all_price, b['text'][i])
            if all_price:
                price_lines.append(lines)

    return price_lines

def check_price_in_string(price_text_list):
    has_price = []
    for i in price_text_list:
        price = regex.search(rules.all_price, i)
        if price:
            has_price.append(True)
        else:
            has_price.append(False)

    return has_price

def combine_item_names(price_text_list, text_to_bottom_price, has_price):
    new_text_list = []
    new_text = ''
    if text_to_bottom_price:
        for i, price_text in enumerate(price_text_list):
            if not has_price[i]:
                new_text += price_text + '\n'
            else:
                new_text += price_text
                new_text_list.append(new_text)
                new_text = ''
    else:#text to upper price
        for i, price_text in enumerate(price_text_list):
            if has_price[i]:
                new_text_list.append(price_text)
            else:
                new_text_list[-1] += '\n' + price_text

    return new_text_list

#prices without items?
def separate_price_and_item(new_text_list):
    price_list = []
    for i in range(len(new_text_list)):
        found_rm = re.search(rules.rm_price, new_text_list[i])
        found_price = None

        for found_price in re.finditer(rules.all_price, new_text_list[i]):  # find for the last price in string
            pass

        if found_price:
            found_price = str(found_price.group(0))
            price_list.append(get_info.alpha_to_num(found_price))
            if found_rm:
                new_text_list[i] = new_text_list[i].replace('RM', '')  # .replace('|', ' ')
            new_text_list[i] = new_text_list[i].replace(found_price,' ')

    for i, j in enumerate(new_text_list):
        new_text_list[i] = get_info.remove_blank_lines(j)

    return new_text_list, price_list

def get_price_header_line(b, first_price_line):
    potential_header = False
    header_count = 0
    header_line = -1
    for i in range(b['line_num'].index(first_price_line)):
        header_found = regex.search(rules.price_header, b['text'][i], re.IGNORECASE)
        if header_found:
            if potential_header:
                if b['line_num'][i] == header_line:
                    header_count+=1
                    #header_line = b['line_num'][i]
                    if header_count>1:
                        break
                else:
                    potential_header = False
                    header_line = -1
            else:
                potential_header = True
                header_count += 1
                header_line = b['line_num'][i]

    if header_line == -1:  # assign a fake header line if header_line not found
        header_line = first_price_line - 1

    return header_line


def add_one_index(b):
    for i, j in b.items():
        if i == 'line_num':
            j.append((b['line_num'][-1]+1))
        else:
            j.append('last_line')