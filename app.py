import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

# Load secret values (like our API key) from a local .env file, if present.
load_dotenv()

app = Flask(__name__)

# Your secret WeatherAPI.com key. Read from the environment - never hard-coded.
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")


def pick_emoji(condition):
    """Choose an emoji based on words in the weather description."""
    text = condition.lower()
    if "thunder" in text:
        return "⛈️"
    if "snow" in text or "sleet" in text or "blizzard" in text:
        return "❄️"
    if "rain" in text or "drizzle" in text or "shower" in text:
        return "\U0001f327️"
    if "fog" in text or "mist" in text:
        return "\U0001f32b️"
    if "cloud" in text or "overcast" in text:
        return "☁️"
    if "sunny" in text or "clear" in text:
        return "☀️"
    return "\U0001f324️"  # default: sun behind small cloud


def get_weather(city):
    """Look up a city and return its current weather, or None if unavailable."""
    try:
        url = "https://api.weatherapi.com/v1/current.json"
        response = requests.get(
            url, params={"key": WEATHER_API_KEY, "q": city}, timeout=10
        )
        data = response.json()

        # WeatherAPI returns an "error" block for bad cities / key problems.
        if "current" not in data:
            print(f"[weather] no data. status={response.status_code} "
                  f"body={response.text[:300]}")
            return None

        location = data["location"]
        current = data["current"]
        condition = current["condition"]["text"]

        return {
            "city": location["name"],
            "country": location["country"],
            "temperature": current["temp_c"],
            "windspeed": current["wind_kph"],
            "description": condition,
            "emoji": pick_emoji(condition),
        }
    except requests.RequestException as error:
        # Network problem, timeout, etc. Log it and fail gracefully.
        print(f"Weather lookup failed for '{city}': {error}")
        return None


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = None
    if request.method == "POST":
        city = request.form["city"]
        weather = get_weather(city)
        if weather is None:
            error = f"Couldn't get weather for '{city}'. Check the spelling or try again."
    return render_template("index.html", weather=weather, error=error)


if __name__ == "__main__":
    app.run(debug=True)
