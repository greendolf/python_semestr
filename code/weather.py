import aiohttp
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import random

# token 0a994f265391dd3e6d0873e9bca7ac40
# current https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}
# hourly https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}

TOKEN = "0a994f265391dd3e6d0873e9bca7ac40"
URLS = [
    "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&lang=ru&appid={}",
    "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}{}&units=metric&lang=ru&appid={}",
    "https://anekdotov.net/anekdot/",
]


async def get_coordinates(city):
    geolocator = Nominatim(user_agent="my_app_name")
    location = geolocator.geocode(city, language="ru")
    if location:
        return (
            location.latitude,
            location.longitude,
            ", ".join(location.address.split(", ")[0::2]),
        )
    else:
        return None


async def get_weather(req, *args):
    lat, lon = args
    match req:
        case "/now":
            return await now(lat, lon)
        case "/today":
            return await today(lat, lon)
        case "/4days":
            return await forecast5(lat, lon)


async def now(lat, lon):
    async with aiohttp.ClientSession() as session:
        async with session.get(URLS[0].format(lat, lon, TOKEN)) as resp:
            result = await resp.json()
            reply = [
                f"Город: {result['name']}\n",
                f"Погода: {result['weather'][0]['description'].capitalize()}\n",
                f"Температура: {int(result['main']['temp'])} градусов по Цельсию\n",
                f"Ощущается как: {int(result['main']['feels_like'])} градусов по Цельсию\n",
                f"Скорость ветра: {result['wind']['speed']} м/c\n",
                f"Давление: {result['main']['pressure']} мм ртутного столба\n",
            ]
            return reply


async def today(lat, lon):
    tz_finder = TimezoneFinder()
    tz = pytz.timezone(tz_finder.timezone_at(lat=lat, lng=lon))
    time = datetime.now(tz)
    stamps = int(8 - time.hour / 3 + 3)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            URLS[1].format(lat, lon, f"&cnt={stamps}", TOKEN)
        ) as resp:
            result = await resp.json()
            reply = []
            for i in range(2, stamps):
                stamp_time = datetime.strptime(
                    result["list"][i]["dt_txt"], "%Y-%m-%d %H:%M:%S"
                )
                reply.append(
                    f"Время: {datetime.strftime(stamp_time, '%H:%M')}\n"
                    f"Погода: {result['list'][i]['weather'][0]['description']}\n"
                    f"Температура: {int(result['list'][i]['main']['temp'])} градусов по Цельсию\n"
                    f"Ощущается как: {int(result['list'][i]['main']['feels_like'])} градусов по Цельсию\n"
                    f"Скорость ветра: {result['list'][i]['wind']['speed']} м/c\n"
                    f"Давление: {result['list'][i]['main']['pressure']} мм ртутного столба\n\n"
                )
            return tuple(reply)


async def forecast5(lat, lon):
    tz_finder = TimezoneFinder()
    tz = pytz.timezone(tz_finder.timezone_at(lat=lat, lng=lon))
    time = datetime.now(tz)
    stamps = int(8 - time.hour / 3 + 3)
    async with aiohttp.ClientSession() as session:
        async with session.get(URLS[1].format(lat, lon, "", TOKEN)) as resp:
            result = await resp.json()
            reply = []
            for i in range(stamps, 40, 3):
                stamp_time = datetime.strptime(
                    result["list"][i]["dt_txt"], "%Y-%m-%d %H:%M:%S"
                )
                reply.append(
                    f"Дата и время: {datetime.strftime(stamp_time, '%d.%m %H:%M')}\n"
                    f"Погода: {result['list'][i]['weather'][0]['description']}\n"
                    f"Температура: {int(result['list'][i]['main']['temp'])} градусов по Цельсию\n"
                    f"Ощущается как: {int(result['list'][i]['main']['feels_like'])} градусов по Цельсию\n"
                    f"Скорость ветра: {result['list'][i]['wind']['speed']} м/c\n"
                    f"Давление: {result['list'][i]['main']['pressure']} мм ртутного столба\n\n"
                )
            return tuple(reply)


async def get_random_joke():
    async with aiohttp.ClientSession() as session:
        async with session.get(URLS[2]) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    jokes = soup.find_all("div", {"class": "anekdot"})

    random_joke = random.choice(jokes).text.strip()

    return random_joke


async def save_dialog(chat_id, message, user):
    filename = str(chat_id) + ".log"
    time = datetime.now(
        pytz.timezone((TimezoneFinder().timezone_at(lat=55.355198, lng=86.086847)))
    )
    with open("./logs/" + filename, "a") as file:
        file.write(time.strftime("[%H:%M:%S] ") + user + ":\n" + message + "\n\n")
