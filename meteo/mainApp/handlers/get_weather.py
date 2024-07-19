import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import requests


def get_weather(city):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    response = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&'
                            f'language=ru&format=json')
    result = response.json()
    if 'results' not in result or result['results'][0]['name'] != city:
        return None


    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": result['results'][0]['latitude'],
        "longitude": result['results'][0]['longitude'],
        "daily": "temperature_2m_max"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    daily_temperature = daily.Variables(0).ValuesAsNumpy()
    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    ).strftime("%B %d, %A")}
    daily_data["temperature_2m_max"] = [int(i) for i in daily_temperature]
    daily_dataframe = pd.DataFrame(data=daily_data)
    return daily_dataframe
