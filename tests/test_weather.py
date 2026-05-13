from services.weather_service import WeatherService


def test_format_weather_context_builds_readable_sentence():
    data = {
        "city": "Mumbai",
        "country": "IN",
        "description": "Clear Sky",
        "temperature": 31,
        "feels_like": 35,
        "humidity": 70,
        "wind_speed": 3.2,
    }

    result = WeatherService.format_weather_context(data)

    assert "Mumbai, IN" in result
    assert "31C" in result
    assert "humidity 70%" in result
