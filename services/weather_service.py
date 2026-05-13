import requests


class WeatherService:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.session = requests.Session()
        self.session.trust_env = False

    def get_weather_by_city(self, city: str) -> dict:
        if not self.api_key:
            return {"error": "OpenWeather API key is missing."}

        try:
            response = self.session.get(
                self.base_url,
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=10,
            )
            payload = response.json()
            response.raise_for_status()
        except requests.RequestException:
            try:
                error_message = payload.get("message")
            except UnboundLocalError:
                error_message = None
            if error_message:
                return {"error": f"OpenWeather error: {error_message}"}
            return {"error": f"Couldn't fetch weather for {city}."}

        weather = payload.get("weather", [{}])[0]
        main = payload.get("main", {})
        wind = payload.get("wind", {})
        sys = payload.get("sys", {})

        return {
            "city": payload.get("name", city.title()),
            "country": sys.get("country", ""),
            "description": weather.get("description", "Unavailable").title(),
            "condition": weather.get("main", "Weather"),
            "icon": weather.get("icon", "01d"),
            "icon_url": f"https://openweathermap.org/img/wn/{weather.get('icon', '01d')}@2x.png",
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "temp_min": main.get("temp_min"),
            "temp_max": main.get("temp_max"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
        }

    @staticmethod
    def format_weather_context(data: dict) -> str:
        return (
            f"{data['city']}, {data['country']}: {data['description']}, "
            f"{data['temperature']}C, feels like {data['feels_like']}C, "
            f"humidity {data['humidity']}%, wind {data['wind_speed']} m/s."
        )
