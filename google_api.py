from google.cloud import vision
from google.oauth2 import service_account
from googleapiclient.discovery import build
import rules
import json

#LIMITED TO 1000 CALLS PER MONTH
def google_vision(path):
    credentials = service_account.Credentials.from_service_account_file('receipt-scanner-336321-fb7b5d1e08c6.json')
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with open(path, 'rb') as f:
        content = f.read()

    image = vision.Image(content=content)
    res_dict = ''
    try:
        response = client.document_text_detection(image=image)
        res_dict = vision.AnnotateImageResponse.to_dict(response)
        #breaks = vision.TextAnnotation.DetectedBreak.BreakType

        with open('vision_response.json','w') as f:  # for debugging (save output to minimize API calls):
            json.dump(res_dict, f)

        return res_dict, True
    except:
        return res_dict, False



def google_search(search_term):
    text = ''
    try:
        service = build('customsearch','v1', developerKey=rules.api_key)
        res = service.cse().list(q=search_term, cx=rules.search_engine_id, gl='my').execute()

        if 'spelling' in res:#append correct spelling if exist
            text = res['spelling']['correctedQuery'] + ' '

        res_count = 5
        if 'items' in res:#if there are results
            for i in range(res_count):
                search_res = res['items'][i]
                text = text + ' ' + search_res['title'] + ' ' + search_res['link'] + ' ' + search_res['snippet']

    finally:
        return text




