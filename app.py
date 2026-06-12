from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Open-Meteo "weather codes" mapped to a friendly description + emoji.
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "\U0001f324️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "\U0001f32b️"),
    48: ("Foggy", "\U0001f32b️"),
    51: ("Light drizzle", "\U0001f327️"),
    61: ("Light rain", "\U0001f327️"),
    63: ("Rain", "\U0001f327️"),
    65: ("Heavy rain", "⛈️"),
    71: ("Light snow", "\U0001f328️"),
    73: ("Snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "\U0001f326️"),
    95: ("Thunderstorm", "⛈️"),
}


def get_weather(city):
    """Look up a city and return its current weather, or None if not found."""
    # Step 1: turn the city name into coordinates (geocoding).
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_response = requests.get(geo_url, params={"name": city, "count": 1})
    results = geo_response.json().get("results")

    if not results:
        return None  # City not found.

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    # Step 2: get the current weather at those coordinates.
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_response = requests.get(weather_url, params={
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
    })
    current = weather_response.json()["current_weather"]

    description, emoji = WEATHER_CODES.get(current["weathercode"], ("Unknown", "❓"))

    return {
        "city": place["name"],
        "country": place.get("country", ""),
        "temperature": current["temperature"],
        "windspeed": current["windspeed"],
        "description": description,
        "emoji": emoji,
    }


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = None
    if request.method == "POST":
        city = request.form["city"]
        weather = get_weather(city)
        if weather is None:
            error = f"Sorry, couldn't find '{city}'. Try another city."
    return render_template("index.html", weather=weather, error=error)


if __name__ == "__main__":
    app.run(debug=True)
