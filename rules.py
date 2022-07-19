address = ('(Johor|'
            'Kedah|'
            'Kelantan|'
            'Malacca|Melaka|'
            'Negeri Sembilan|'
            'Pahang|'
            'Perak|'
            'Perlis|'
            'Penang|Pulau Pinang|'
            'Sabah|'
            'Sarawak|'
            'Selangor|'
            'Terengganu)')

address_remove = r'(alamat|address)'
date_remove = r'date'
phone_remove = r'(Phone|Tel|Telephone)'
time_remove = r'time'

#  https://en.wikipedia.org/wiki/Telephone_numbers_in_Malaysia
phone = (r'(((?<![0-9]))\+?6?0([3-9]|[8][2-9])[ -]?\d{2,4}[ -]?\d{4}(?![0-9]))|'  #  landline: +604-xxx xxxx
         '(((?<![0-9]))(1(3|[5-9])00)[ -]?\d{2}[ -]?\d{4}(?![0-9]))|'   # 1300-xx-xxxx
         '((\+?6?01)[0-9][ -]?[0-9]{3,4}[ -]?[0-9]{4})')   # mobile 016-xxxx xxx

date = (r'((20[0-9]{2})[,\.\-\/]((0?[1-9])|(1[0-2]))[,\.\-\/]((0?[1-9])|([12][0-9])|(3[01])))|'
        '(((0?[1-9])|([12][0-9])|(3[01]))[,\.\-\/]((0?[1-9])|(1[0-2]))[,\.\-\/]((20)?[0-9]{2}))')

time = r'((0?[1-9]|1[0-9]|2[0-3]):([0-5][0-9])(:([0-5][0-9]))?)'

date_format = r'[,\.\-\/]'
max_price = r'(([1-9SZ](([0-9OSZ]{1,5})?))|[0O])[\.|,]([0-9OSZ][0O])'  # last digit must be 0
all_price = r'(([\-1-9SZ](([0-9OSZ]{1,5})?))|[0O])[\.|,]([0-9OSZ]{2})'  # last digit does not have to be 0
confirmed_price = r'(^[\s]*(([\-1-9](([0-9]{1,5})?))|[0])[\.]([0-9]{2})[\s]*$)'  # only digits and one dot, start and end with optional space
rm_price = r'([R][M])?(([1-9SZ](([0-9OSZ]{1,5})?))|[0O])[\.|,]([0-9OSZ]{2})'  # all_price including RM at the front

price_header = r'(Price|Item|qty|Quantity|total|subtotal|RM|Description|Name|Amount)'

api_key = ''
search_engine_id = 'e5acaed6eea867dcf'

file_name = 'receipt_data.json'

#level	page_num	block_num	par_num	line_num	word_num	left	top	    width	height	conf	text
#1	    1	        0	        0	    0	        0	        0	    0	    1024	800	    -1
#2	    1	        1	        0	    0	        0	        98	    66	    821	    596	    -1
#3	    1	        1	        1	    0	        0	        98	    66	    821	    596	    -1
#4	    1	        1	        1	    1	        0	        105	    66	    719	    48	    -1
#5	    1	        1	        1	    1	        1	        105	    66	    74	    32	    90	    The
#5	    1	        1	        1	    1	        2	        205	    67	    143	    40	    87	    (quick)
#5	    1	        1	        1	    1	        3	        376	    69	    153	    41	    89	    [brown]
#5	    1	        1	        1	    1	        4	        559	    71	    105	    40	    89	    {fox}
#5	    1	        1	        1	    1	        5	        687	    73	    137	    41	    89	    jumps!
#4	    1	        1	        1	    2	        0	        104	    115	    784	    51	    -1
#5	    1	        1	        1	    2	        1	        104	    115	    96	    33	    91	    Over
#5	    1	        1	        1	    2	        2	        224	    117	    60	    32	    89	    the
#5	    1	        1	        1	    2	        3	        310	    117	    224	    39	    88	    $43,456.78
#5	    1	        1	        1	    2	        4	        561	    121	    136	    42	    92	    <lazy>
#5	    1	        1	        1	    2	        5	        722	    123	    70	    32	    92	    #90
#5	    1	        1	        1	    2	        6	        818	    125	    70	    41	    89	    dog

#\d+((20[0-9]{2})[\.\-\/](0?[1-9]|1[0-2])[\.\-\/]((0?[1-9])|([12][0-9])|(3[01])))|(((0?[1-9])|([12][0-9])|(3[01]))[\.\-\/](0?[1-9]|1[0-2])[\.\-\/](20[0-9]{2}))