import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def weathers(lat, lon):
    url = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=6fc3bac96f01ebc8e27a717aad48218a&units=metric'.format(lat, lon)

    res = requests.get(url)
    data = res.json()
    
    temp = data['main']['temp']
    max_temp = data['main']['temp_max']
    min_temp = data['main']['temp_min']

    return f'오늘 날씨는 {temp}입니다. 최고기온은 {max_temp}입니다. 최저기온은 {min_temp}입니다.'

def school_menu(current_date_time):
    next_day = current_date_time + timedelta(days=1)
    formatted_date = today.strftime("%Y%m%d")
    fields = ("MMEAL_SC_NM", "MLSV_YMD", "DDISH_NM", "CAL_INFO")
    service_key = ("15f44e0238a34188b681b4c7225143fd", "")
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": service_key[0],
        "Type": "json",
        "pIndex": "1",
        "pSize": "100",
        "SD_SCHUL_CODE": "7010537",
        "ATPT_OFCDC_SC_CODE": "B10",
        "MLSV_YMD": formatted_date
    }

    response = requests.get(url, params=params)
    # Parse the JSON response
    data = response.json()

    # Now you can extract the necessary information as shown in the previous example
    schul_info = data["mealServiceDietInfo"][1]["row"][0]
    school_name = schul_info["SCHUL_NM"]
    meal_date = schul_info["MLSV_YMD"]
    meal_menu = schul_info["DDISH_NM"].replace("<br/>", "\n")
    calories = schul_info["CAL_INFO"]
    nutrient_info = schul_info["NTR_INFO"].replace("<br/>", "\n")

    return f'오늘 급식은: {school_name} , {meal_date} , {meal_menu} , {calories} '



def message_send(message):
    # Your Kakao API credentials and URL
    manual_code = "WUBg0pkPR0u9CyaS7FiWAUJhz655tvTde1sVEy_WAV_rLJkrhWfKECzneggKKcjZAAABjMQkykhDz1szkZmFRA"
    token_url = "https://kauth.kakao.com/oauth/token"
    send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    # Request a token using the authorization code
    data = {
        "grant_type": "authorization_code",
        "client_id": "92c44268fe79aba5f10c8d4ed21c22a2",
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
        "client_id": "92c44268fe79aba5f10c8d4ed21c22a2",
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


# 날씨 정보를 가져와 메시지로 전송
weather_message = weathers(37.588, 126.978)
today_menu = school_menu(datetime.now())
print(today_menu)
message_send(weather_message)
message_send(today_menu)
    
