import requests
import json
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlencode, unquote, quote_plus
import urllib
import pandas as pd


def weathers(nx, ny):
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    serviceKey = "your service key from 기상청" # Remove space after the service key
    pageNo = 1
    numOfRows = 500
    dataType = 'JSON'
    today = datetime.today().strftime("%Y%m%d")
    template = []
    template2 = []

    params = '?' + urlencode({
        quote_plus("serviceKey"): serviceKey,
        quote_plus("numOfRows"): numOfRows,
        quote_plus("pageNo"): pageNo,
        quote_plus("dataType"): dataType,
        quote_plus("base_date"): today,
        quote_plus("base_time"): "0500",
        quote_plus("nx"): nx,
        quote_plus("ny"): ny
    })
    req = urllib.request.Request(url + unquote(params))
    print(req)
    response_body = urlopen(req).read()
    data = json.loads(response_body)

    df = pd.DataFrame(data['response']['body']['items']['item'])
    informations = dict()

    for itemse in data['response']['body']['items']['item'] :
        cate = itemse['category']
        fcstTime = itemse['fcstTime']
        fcstValue = itemse['fcstValue']
        temp = dict()
        temp[cate] = fcstValue
        
        if fcstTime not in informations.keys() :
            informations[fcstTime] = dict()
        #print(items['category'], items['fcstTime'], items['fcstValue'])
        #print(informations[fcstTime])
        informations[fcstTime][cate] = fcstValue
    pyt_code = {0 : '비 없음', 1 : '비', 2 : '비/눈', 3 : '눈', 5 : '빗방울', 6 : '진눈깨비', 7 : '눈날림'}
    for key, val in zip(informations.keys(), informations.values()):
        if val['PTY'] :
            pty_temp = pyt_code[int(val['PTY'])]
    #         print("강수 여부 :",pty_temp)
            template2.append(pty_temp)
            
        if val['TMP'] :
            t1h_temp = float(val['TMP'])
    #         print(f"기온 : {t1h_temp}℃")
            template.append(t1h_temp) 
    return f'오늘 아침 온도는{template[1]}℃ 입니다. 날씨는 {template2[1]} 입니다.'

def school_menu(current_date_time):
    formatted_date = current_date_time.strftime("%Y%m%d")  
    service_key = "your service key from 교육청"  
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": service_key,
        "Type": "json",
        "pIndex": "1",
        "pSize": "100",
        "SD_SCHUL_CODE": "7010537",
        "ATPT_OFCDC_SC_CODE": "B10",
        "MLSV_YMD": formatted_date
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "mealServiceDietInfo" in data and "row" in data["mealServiceDietInfo"][1]:
            schul_info = data["mealServiceDietInfo"][1]["row"][0]
            school_name = schul_info["SCHUL_NM"]
            meal_date = schul_info["MLSV_YMD"]
            meal_menu = schul_info["DDISH_NM"].replace("<br/>", "\n")
            calories = schul_info.get("CAL_INFO", "")
            return f'오늘 급식은: {school_name} , {meal_date} , {meal_menu} , {calories} '

def message_send(message):
    # Your Kakao API credentials and URL
    manual_code = "your manual code"
    token_url = "https://kauth.kakao.com/oauth/token"
    send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    # Request a token using the authorization code
    data = {
        "grant_type": "authorization_code",
        "client_id": "your client id",
        "redirect_url": "https://localhost:3000",
        "code": manual_code
    }
    response = requests.post(token_url, data=data)
    tokens = response.json()

    # Save the refresh token for future use
    if "refresh_token" in tokens:
        with open("./kakao_code.json", "w") as fp:
            json.dump(tokens, fp)

    # Use the refresh token to get an access token
    with open("./kakao_code.json", "r") as fp:
        tokens = json.load(fp)

    refresh_token = tokens['refresh_token']
    data = {
        "grant_type": "refresh_token",
        "client_id": "your client id",
        "refresh_token": refresh_token
    }
    response = requests.post(token_url, data=data)
    tokens = response.json()

    if 'access_token' in tokens:
        access_token = tokens['access_token']

        # Send the message using the obtained access token
        headers = {"Authorization": "Bearer " + access_token}
        data = {
            "template_object": json.dumps({
                "object_type": "text",
                "text": message,
                "link": {"web_url": "www.google.co.kr"}
            })
        }
        response = requests.post(send_url, headers=headers, data=data)
        print(response.json())
    else:
        print("Error: Unable to obtain access token")

if __name__ == "__main__":
    weather_message = weathers(59,128)
    today_menu = school_menu(datetime.now())
    print(today_menu)
    message_send(weather_message)
    message_send(today_menu)
