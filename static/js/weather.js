window.weatherModule = (() => {
  const weatherCard = document.getElementById("weather-card");

  async function fetchWeather(city) {
    const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    return { ok: response.ok, data: await response.json() };
  }

  function renderWeatherCard(data) {
    if (!weatherCard) return;

    if (data.error) {
      weatherCard.classList.remove("hidden");
      weatherCard.innerHTML = `<p class="weather-title">${data.error}</p>`;
      return;
    }

    weatherCard.classList.remove("hidden");
    weatherCard.innerHTML = `
      <p class="weather-title">Live weather for ${data.city}, ${data.country}</p>
      <div class="weather-main">
        <div class="weather-summary">
          <img class="weather-icon" src="${data.icon_url}" alt="${data.description}" />
          <div>
            <div class="weather-temp">${Math.round(data.temperature)}C</div>
            <div class="weather-condition">${data.condition} - ${data.description}</div>
          </div>
        </div>
        <div class="weather-condition">Feels like ${Math.round(data.feels_like)}C</div>
      </div>
      <div class="weather-meta">
        <div class="weather-stat">
          <span class="weather-stat-label">Humidity</span>
          ${data.humidity}%
        </div>
        <div class="weather-stat">
          <span class="weather-stat-label">Wind</span>
          ${data.wind_speed} m/s
        </div>
        <div class="weather-stat">
          <span class="weather-stat-label">Range</span>
          ${Math.round(data.temp_min)}C - ${Math.round(data.temp_max)}C
        </div>
        <div class="weather-stat">
          <span class="weather-stat-label">Pressure</span>
          ${data.pressure} hPa
        </div>
      </div>
    `;
  }

  return { fetchWeather, renderWeatherCard };
})();
