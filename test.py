import requests
import _datetime


def convert_from_unix_to_datetime(unix_time):
    datetime = _datetime.datetime.fromtimestamp(unix_time)
    return datetime


request = 'https://api.openweathermap.org/data/2.5/forecast?q=Москва,Россия&appid=942a25426a3b21ff180cfa7b0b01a248'
# Прогноз на 5 дней, молимся богу, чтобы api не отвалился

responce = requests.get(request).json()
print(responce)

sunrise_time, sunset_time = responce['city']['sunrise'], responce['city']['sunset']

print(convert_from_unix_to_datetime(sunrise_time))
