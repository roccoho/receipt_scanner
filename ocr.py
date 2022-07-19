import json
import google_api
from PIL import Image, ImageDraw
from shapely.geometry import LineString

def draw_boxes(c, img_name):
    im =  Image.open(img_name)
    draw = ImageDraw.Draw(im)
    for page in c['pages']:
        for block in page['blocks']:
            for paragraph in block['paragraphs']:
                for word in paragraph['words']:
                    coor = [word['bounding_box']['vertices'][0]['x'],
                            word['bounding_box']['vertices'][0]['y'],
                            word['bounding_box']['vertices'][1]['x'],
                            word['bounding_box']['vertices'][1]['y'],
                            word['bounding_box']['vertices'][2]['x'],
                            word['bounding_box']['vertices'][2]['y'],
                            word['bounding_box']['vertices'][3]['x'],
                            word['bounding_box']['vertices'][3]['y']]
                    draw_box(draw, coor)
    im.show()

def draw_line(coor, img, color):
    img.line((coor[0], coor[1], coor[2], coor[3]), fill=color, width=3)

def draw_box(coor):
    draw_line((coor[0], coor[1], coor[2], coor[3]))
    draw_line((coor[2], coor[3], coor[4], coor[5]))
    draw_line((coor[4], coor[5], coor[6], coor[7]))
    draw_line((coor[6], coor[7], coor[0], coor[1]))


def get_ocr(img_name):
    res, internet = google_api.google_vision(img_name)

    #with open('vision_response.json') as f: #for debugging (instead of calling GCV again)
    #    res = json.load(f)

    if res and internet:
        try:
            c = res['full_text_annotation']
            space = False
            symbols = ''
            b = {'coor': [], 'text': [], 'block_num': [], 'space': []}
            for page in c['pages']:
                for block_num, block in enumerate(page['blocks']):
                    for paragraph in block['paragraphs']:
                        for word in paragraph['words']:
                            for symbol in word['symbols']:
                                symbols += symbol['text']
                                if 'property' in symbol:
                                    if 'detected_break' in symbol['property']:
                                        break_type = symbol['property']['detected_break']['type_']
                                        # http://googleapis.github.io/googleapis/java/grpc-google-cloud-vision-v1/0.1.5/apidocs/com/google/cloud/vision/v1/TextAnnotation.DetectedBreak.BreakType.html
                                        if break_type == 2 or break_type == 1:
                                            space = True
                                        #elif break_type == 3 or break_type == 5:
                                        #    new_line = True

                            b['block_num'].append(block_num)
                            b['text'].append(symbols)
                            b['coor'].append(word['bounding_box']['vertices'])
                            b['space'].append(space)
                            space = False
                            symbols = ''

            b['coor'] = update_coor(b['coor'])
            new_b, full_text = get_line_num(b)
            error = None
        except:
            new_b = []
            full_text = ''
            error = 'empty'
        #for debugging
        #with open('text_ordering.txt','w',encoding="utf-8") as f:
        #    f.write(c['text'])
    else:
        new_b = []
        full_text = ''
        error = 'internet'

    return new_b, full_text, error

def update_coor(coor_arr):
    coor = []
    for i in coor_arr:
        coor.append(normalize_coor(i))
    return coor

def get_line_num(b):
    lines = []
    index_hist = []
    for current_index, coor in enumerate(b['coor']):
        line1 = get_line_coor(coor)
        #draw_line(line1, draw, 'red')
        left_index = left_word_index(b, line1)
        if left_index != -1:
            if left_index not in index_hist and current_index not in index_hist:
                index_hist.append(left_index)
                index_hist.append(current_index)
                line = [left_index, current_index]
                lines.append(line)
                #print('case1')
            elif left_index in index_hist and current_index not in index_hist:
                index_hist.append(current_index)
                #print('case2')
                for k in lines:
                    if left_index in k:
                        k.insert(k.index(left_index)+1, current_index)
                        break
            elif left_index not in index_hist and current_index in index_hist:
                index_hist.append(left_index)
                #print('case3')
                for k in lines:
                    if current_index in k:
                        k.insert(k.index(current_index), left_index)
                        break
            else:#left_index in index_hist and current_index in index_hist:
                current_index_list = -1
                left_index_list = -1
                for j, k in enumerate(lines):
                    if current_index == k[0]:
                        current_index_list = j
                    if left_index == k[-1]:
                        left_index_list = j

                if current_index_list != -1 and left_index_list != -1:
                    temp_list = lines[current_index_list]
                    lines[left_index_list] += temp_list
                    lines.pop(current_index_list)
                    #print('case4.1')
                #else:
                    #print('case4.2')
        else:#no left_index
            if current_index in index_hist:
                pass
            else:#current_index not in index_hist:
                #print('case6')
                index_hist.append(current_index)
                line = [current_index]
                lines.append(line)

    new_b = {'coor': [], 'text': [], 'block_num': [], 'line_num': [], 'space': [], 'break': []}
    for line_num, line in enumerate(lines):
        for index in line:
            for key in new_b:
                if key == 'line_num':
                    new_b[key].append(line_num)
                elif key == 'break':
                    if index == line[-1]:#last word in line
                        new_b[key].append(True)
                    else:
                        new_b[key].append(False)
                else:
                    new_b[key].append(b[key][index])

    #block_group = {}
    #for i, block_num in enumerate(new_b['block_num']):
    #    if str(block_num) in block_group:
    #        block_group[str(block_num)].append(i)
    #    else:
    #        block_group[str(block_num)] = [i]
#
    #new_b['line_num'] = [None]*len(new_b['text'])
    #for block_num in block_group:
    #    for i, index in enumerate(block_group[block_num]):
    #        new_b['line_num'][index] = i

    full_text = ''
    for i, text in enumerate(new_b['text']):
        if new_b['break'][i]:
            full_text += text + '\n'
        elif new_b['space'][i]:
            full_text += text + ' '
        else:
            full_text += text

    #for testing
    #with open('b_data.json', 'w') as f:
    #    json.dump(new_b, f)
    #with open('full_text2.txt','w', encoding='utf-8') as f:
    #    f.write(full_text)
    #for i, text in enumerate(new_b['text']):
    #    print(text + ' ' + str(new_b['block_num'][i])+ ' ' + str(new_b['line_num'][i]))

    return new_b, full_text
    #im.show()

def left_word_index(b, line1):
    shortest_dist = float('inf')
    index = -1
    for i, j in enumerate(b['coor']):
        line2 = [j[1]['x'], j[1]['y'], j[2]['x'], j[2]['y']]
        #draw_line(line2, img, 'blue')
        line1string = LineString([(line1[0],line1[1]), (line1[2],line1[3])])
        line2string = LineString([(line2[0],line2[1]), (line2[2],line2[3])])
        inter_pt = line1string.intersection(line2string)
        if inter_pt:
            temp_dist = get_distance((inter_pt.x, inter_pt.y), (line1[0], line1[1]))
            if temp_dist < shortest_dist:
                shortest_dist = temp_dist
                index = i

    #if index == -1:
    #    print(b['text'][text_index])
    #else:
    #    print(b['text'][text_index] + '('+ str(text_index)+') cuts ' + b['text'][index] + '('+str(index)+ ') at distance ' + str(temp_dist))
    return index

#def cramers_rule(p1, p2, p3):
#    return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])
#
#def check_intersect(line1, line2):
#    p1 = (line1[0], line1[1])
#    p2 = (line1[2], line1[3])
#    p3 = (line2[0], line2[1])
#    p4 = (line2[2], line2[3])
#    return cramers_rule(p1, p2, p3) != cramers_rule(p1, p2, p4) and cramers_rule(p2, p3, p4) != cramers_rule(p1, p3, p4)

def get_distance(point1, point2):
    return ((point2[0]-point1[0])**2 + (point2[1]-point1[1])**2) ** 0.5

def get_line_coor(coor):
    midpoint1 = midpoint((coor[0]['x'],coor[0]['y']), (coor[3]['x'], coor[3]['y']))#midpoint of word start
    midpoint2 = midpoint((coor[1]['x'],coor[1]['y']), (coor[2]['x'], coor[2]['y']))#midpoint of word end
    centre_point = midpoint(midpoint1, midpoint2) #centre point of word
    gradient = (midpoint2[1]-midpoint1[1])/(midpoint2[0]-midpoint1[0])
    y_intercept = midpoint1[1] - (gradient*midpoint1[0])
    line = [centre_point[0], centre_point[1], 0, y_intercept] #x1, y1, x2, y2
    return [round(i) for i in line]

def midpoint(point1, point2):
    return [(point1[0]+point2[0])/2, (point1[1]+point2[1])/2]

def normalize_coor(coor):
    left_index = []
    pop_index = None
    for j in range(2):#get the smallest 2 x-coor
        x = float('inf')
        for index, i in enumerate(coor):
            if i['x'] <= x:
                x = i['x']
                pop_index = index
        left_index.append(coor.pop(pop_index))
    right_index = coor #2 coor that are not popped are right coor

    #get the smallest y-coor at left
    y = float('inf')
    pop_index = None
    for index, i in enumerate(left_index):
        if i['y'] <= y:
            y = i['y']
            pop_index = index
    top_left = left_index.pop(pop_index)
    bottom_left = left_index[0]

    # get the smallest y-coor at right
    y = float('inf')
    pop_index = None
    for index, i in enumerate(right_index):
        if i['y'] <= y:
            y = i['y']
            pop_index = index
    top_right = right_index.pop(pop_index)
    bottom_right = right_index[0]

    return [top_left, top_right, bottom_right, bottom_left]


