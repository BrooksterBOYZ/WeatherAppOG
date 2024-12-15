from tkinter import messagebox
import requests
import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import time
import os

# --- Constants ---
API_URL = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=imperial'
FORECAST_API_URL = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}&units=imperial'
API_KEY = "efa60bf15337a9240c2e8261fa96f8d3"

# --- Color Palette ---
BG_COLOR = "#1A237E"  # Dark blue gradient for soothing background
PRIMARY_COLOR = "#00B0FF"  # Light blue for primary elements
ACCENT_COLOR = "#FFC107"  # Amber for accents
TEXT_COLOR = "white"  # White text for better contrast

# --- Functions ---
def get_weather(city):
    try:
        response = requests.get(API_URL.format(city, API_KEY))
        data = response.json()

        if data['cod'] != 200:
            raise ValueError(data['message'])

        # Extract current weather data
        weather = {
            'temp': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'pressure': data['main']['pressure'],
            'sunrise': datetime.datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p'),
            'sunset': datetime.datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p')
        }
        return weather

    except Exception as e:
        messagebox.showerror('Error', str(e))
        return None


def update_weather_ui(weather):
    temp_label.config(text=f"{weather['temp']:.0f}{unit_label}")
    description_label.config(text=weather['description'].title())
    humidity_label.config(text=f"Humidity: {weather['humidity']}%")
    wind_label.config(text=f"Wind: {weather['wind_speed']} mph")
    pressure_label.config(text=f"Pressure: {weather['pressure']} hPa")
    sunrise_label.config(text=f"Sunrise: {weather['sunrise']}")
    sunset_label.config(text=f"Sunset: {weather['sunset']}")
    update_weather_icon(weather['icon'])


def update_weather_icon(icon_code):
    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        icon_response = requests.get(icon_url, stream=True)
        icon_image = Image.open(icon_response.raw)
        icon_photo = ImageTk.PhotoImage(icon_image)
        icon_label.config(image=icon_photo)
        icon_label.image = icon_photo
    except requests.exceptions.RequestException as e:
        print(f"Error fetching icon: {e}")
        icon_label.config(text="Icon not available")


def search_city():
    city = city_entry.get()
    if city:
        weather = get_weather(city)
        if weather:
            update_weather_ui(weather)
            get_forecast(city)


def toggle_units():
    global API_URL, FORECAST_API_URL, unit_label
    if API_URL.endswith('metric'):
        API_URL = API_URL.replace('metric', 'imperial')
        FORECAST_API_URL = FORECAST_API_URL.replace('metric', 'imperial')
        unit_label = "°F"
        units_button.config(text="°C")
    else:
        API_URL = API_URL.replace('imperial', 'metric')
        FORECAST_API_URL = FORECAST_API_URL.replace('imperial', 'metric')
        unit_label = "°C"
        units_button.config(text="°F")
    search_city()


def clear_search():
    city_entry.delete(0, tk.END)
    icon_label.config(image=None)
    icon_label.image = None
    temp_label.config(text="")
    description_label.config(text="")
    humidity_label.config(text="")
    wind_label.config(text="")
    pressure_label.config(text="")
    sunrise_label.config(text="")
    sunset_label.config(text="")
    clear_forecast_ui()


def clear_forecast_ui():
    for widget in forecast_frame.winfo_children():
        widget.destroy()


# --- Forecast Functions ---
def get_forecast(city):
    try:
        response = requests.get(FORECAST_API_URL.format(city, API_KEY))
        data = response.json()

        if data['cod'] != '200':
            raise ValueError(data['message'])

        forecast_data = []
        current_date = None
        for entry in data['list']:
            dt_txt = entry['dt_txt']
            date, time = dt_txt.split()
            if time == "12:00:00" and date != current_date:
                temp = entry['main']['temp']
                temp_min = entry['main']['temp_min']
                temp_max = entry['main']['temp_max']
                icon = entry['weather'][0]['icon']
                forecast_data.append((date, temp, temp_min, temp_max, icon))
                current_date = date

        update_forecast_ui(forecast_data)

    except Exception as e:
        messagebox.showerror('Error', str(e))


def update_forecast_ui(forecast_data):
    clear_forecast_ui()  # Clear previous forecast data

    for i, (date, temp, temp_min, temp_max, icon) in enumerate(forecast_data[:7]):
        day_frame = create_rounded_frame(forecast_frame, 400, 100, 15, bg=PRIMARY_COLOR)

        day_label = tk.Label(day_frame, text=f"{date}", font=("Helvetica", 12, "bold"), bg=PRIMARY_COLOR, fg=TEXT_COLOR)
        day_label.grid(row=0, column=0, sticky="w")

        temp_label = tk.Label(day_frame, text=f"{temp:.0f}{unit_label}", font=("Helvetica", 14), bg=PRIMARY_COLOR,
                              fg=TEXT_COLOR)
        temp_label.grid(row=0, column=1, sticky="e")

        temp_range_label = tk.Label(day_frame,
                                    text=f"Min: {temp_min:.0f}{unit_label} / Max: {temp_max:.0f}{unit_label}",
                                    font=("Helvetica", 10), bg=PRIMARY_COLOR, fg=TEXT_COLOR)
        temp_range_label.grid(row=1, column=0, columnspan=2, sticky="e")

        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        try:
            icon_response = requests.get(icon_url, stream=True)
            icon_image = Image.open(icon_response.raw)
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label = tk.Label(day_frame, image=icon_photo, bg=PRIMARY_COLOR)
            icon_label.image = icon_photo
            icon_label.grid(row=0, column=2, rowspan=2, padx=5)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching icon: {e}")
            icon_label = tk.Label(day_frame, text="Icon not available", bg=PRIMARY_COLOR, fg=TEXT_COLOR)
            icon_label.grid(row=0, column=2, rowspan=2)


def create_rounded_frame(parent, width, height, radius, **kwargs):
    """Creates a frame with rounded corners using a Canvas widget"""
    canvas = tk.Canvas(parent, width=width, height=height, bg=kwargs.get("bg", "white"), bd=0, highlightthickness=0)
    canvas.grid(row=0, column=0, padx=10, pady=10)

    # Draw rounded rectangle
    canvas.create_arc((0, 0, radius, radius), start=90, extent=90, fill=kwargs.get("bg", "white"),
                      outline=kwargs.get("bg", "white"))
    canvas.create_arc((width - radius, 0, width, radius), start=0, extent=90, fill=kwargs.get("bg", "white"),
                      outline=kwargs.get("bg", "white"))
    canvas.create_arc((0, height - radius, radius, height), start=180, extent=90, fill=kwargs.get("bg", "white"),
                      outline=kwargs.get("bg", "white"))
    canvas.create_arc((width - radius, height - radius, width, height), start=270, extent=90,
                      fill=kwargs.get("bg", "white"), outline=kwargs.get("bg", "white"))

    canvas.create_rectangle((radius, 0, width - radius, height), fill=kwargs.get("bg", "white"),
                            outline=kwargs.get("bg", "white"))
    canvas.create_rectangle((0, radius, width, height - radius), fill=kwargs.get("bg", "white"),
                            outline=kwargs.get("bg", "white"))

    return canvas

# --- UI Setup ---
root = tk.Tk()
root.title("Weather App")
root.config(bg=BG_COLOR)

# --- App Logo and Company Name ---
try:
    logo_image = Image.open("logo.png")  # Ensure you have an app logo file
    logo_image = logo_image.resize((100, 100))  # Resize the logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo, bg=BG_COLOR)
    logo_label.image = logo_photo
    logo_label.pack(pady=10)
except FileNotFoundError:
    print("Logo file not found, skipping logo display.")

company_name_label = tk.Label(root, text="WeatherMaster Inc.", font=("Helvetica", 20, "bold"), fg=TEXT_COLOR,
                              bg=BG_COLOR)
company_name_label.pack()

# Continue with the rest of your UI setup...

# --- Forecast UI ---
forecast_frame = tk.Frame(root, bg=BG_COLOR)
forecast_frame.pack(fill="both", expand=True, pady=10, padx=20)

# --- Footer ---
footer_label = tk.Label(root, text="© 2024 WeatherMaster Inc.", font=("Helvetica", 10), fg=TEXT_COLOR, bg=BG_COLOR)
footer_label.pack(side="bottom", pady=5)

# --- Initialize ---
unit_label = "°F"  # Default to Fahrenheit

# --- UI Elements ---
city_entry = tk.Entry(root, font=("Helvetica", 14), width=20)
city_entry.pack(pady=10)

search_button = tk.Button(root, text="Search", font=("Helvetica", 14), command=search_city)
search_button.pack(pady=10)

temp_label = tk.Label(root, font=("Helvetica", 24), fg=TEXT_COLOR, bg=BG_COLOR)
temp_label.pack(pady=10)

description_label = tk.Label(root, font=("Helvetica", 18), fg=TEXT_COLOR, bg=BG_COLOR)
description_label.pack(pady=10)

humidity_label = tk.Label(root, font=("Helvetica", 14), fg=TEXT_COLOR, bg=BG_COLOR)
humidity_label.pack(pady=5)

wind_label = tk.Label(root, font=("Helvetica", 14), fg=TEXT_COLOR, bg=BG_COLOR)
wind_label.pack(pady=5)

pressure_label = tk.Label(root, font=("Helvetica", 14), fg=TEXT_COLOR, bg=BG_COLOR)
pressure_label.pack(pady=5)

sunrise_label = tk.Label(root, font=("Helvetica", 14), fg=TEXT_COLOR, bg=BG_COLOR)
sunrise_label.pack(pady=5)

sunset_label = tk.Label(root, font=("Helvetica", 14), fg=TEXT_COLOR, bg=BG_COLOR)
sunset_label.pack(pady=5)

icon_label = tk.Label(root, bg=BG_COLOR)
icon_label.pack(pady=10)

units_button = tk.Button(root, text="°C", font=("Helvetica", 14), command=toggle_units)
units_button.pack(pady=10)

# --- Start the main loop ---
root.mainloop()
