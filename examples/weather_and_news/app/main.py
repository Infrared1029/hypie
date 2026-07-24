import pathlib
import time

import htpy
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.sse import ServerSentEvent, EventSourceResponse

from .ui.pages.app import WeatherAndNewsPage
from .ui.widgets.weather_widget.WeatherWidget import WeatherWidget
from .ui.widgets.news_widget.NewsWidget import NewsWidget

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=pathlib.Path(__file__).parent.resolve() / "static")
)


data = [
    {
        "id": "tokyo",
        "name": "Tokyo, JP",
        "weather": {"temp": 24, "condition": "Clear haze", "high": 27, "low": 19},
        "news": [
            {"time": "14m ago", "text": "Subway Line 4 delayed ninety seconds."},
            {"time": "1h ago", "text": "Nikkei closes up 0.3%."},
            {"time": "3h ago", "text": "Summer festival permits approved."},
        ],
    },
    {
        "id": "lisbon",
        "name": "Lisbon, PT",
        "weather": {"temp": 21, "condition": "Coastal breeze", "high": 23, "low": 16},
        "news": [
            {"time": "18m ago", "text": "Tram 28 adds an extra carriage."},
            {"time": "4h ago", "text": "Azulejo exhibit opens at the museum."},
            {"time": "7h ago", "text": "Fado houses report full bookings."},
        ],
    },
]


@app.get("/")
def index():
    tokyo_data = [d for d in data if d["id"] == "tokyo"][0]
    return HTMLResponse(
        WeatherAndNewsPage(
            weather_data={**tokyo_data["weather"], "name": tokyo_data["name"]},
            news_data={"news": tokyo_data["news"], "name": tokyo_data["name"]},
        )
    )


@app.get("/data")
def get_region_data(region_id: str):
    region_data = [d for d in data if d["id"] == region_id][0]
    # assume creating weather widget takes ~0.5 seconds
    time.sleep(0.5)
    weather_widget = WeatherWidget(**region_data["weather"], name=region_data["name"])
    time.sleep(0.5)
    news_widget = NewsWidget(news=region_data["news"], name=region_data["name"])
    return HTMLResponse(htpy.fragment[weather_widget, news_widget])


@app.get("/stream/data", response_class=EventSourceResponse)
def get_region_data_stream(region_id: str):
    region_data = [d for d in data if d["id"] == region_id][0]
    time.sleep(0.5)
    weather_widget = WeatherWidget(**region_data["weather"], name=region_data["name"])
    yield ServerSentEvent(event="server:fragment", raw_data=weather_widget.encode())
    time.sleep(0.5)
    news_widget = NewsWidget(news=region_data["news"], name=region_data["name"])
    yield ServerSentEvent(event="server:fragment", raw_data=news_widget.encode())
