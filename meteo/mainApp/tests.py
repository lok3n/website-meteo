from django.test import TestCase
import requests


def get_weather_city(city):
    url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json'
    response = requests.get(url)
    print(response.json())

get_weather_city('Барнаул')
