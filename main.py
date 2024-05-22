import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13b_V4

font_dir = os.path.join(os.path.dirname(os.path.relpath(__file__)), "font")

load_dotenv()
API_URL = os.environ.get("WEATHERVANE_API_URL")

r = requests.get(url= API_URL)
data = r.json()
readings = data[0]['readings']
reading_time_obj = datetime.strptime(data[0]['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
timezone = pytz.timezone("Europe/London")
localised_time_obj = pytz.timezone("UTC").localize(reading_time_obj)
time_string = localised_time_obj.astimezone(pytz.timezone("Europe/London")).strftime('%d/%m/%y %H:%M')

print(f"time_string: {time_string}")

print(readings)

try:
    epd = epd2in13b_V4.EPD()
    print("Initialising and clearing display")
    epd.init()
    epd.Clear()

    print("Drawing")
    font_header = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Regular.ttf'), 20)
    font_body = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Thin.ttf'), 16)
    font_caption = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Thin.ttf'), 12)
    BlackImage = Image.new('1', (epd.height, epd.width), 255)
    RedImage = Image.new('1', (epd.height, epd.width), 255)
    draw_black = ImageDraw.Draw(BlackImage)
    draw_red = ImageDraw.Draw(RedImage)
    draw_black.text((2, 2), 'Weathervane', font = font_header)
    draw_black.line((0, 26, 250, 26), fill = 0)
    draw_black.text((2, 28), f'Time of reading: {time_string}', font = font_caption)
    draw_black.text((18, 44), f'{readings["temperature"]} C\n' +
                              f'{readings["pressure"]} hPa\n' +
                              f'{readings["humidity"]} %\n' +
                              f'{readings["luminance"]} Lx', font = font_body)
    draw_black.text((143, 44), f'{readings["rain"]} mm\n' +
                                f'{round(float(readings["wind_speed"]), 2)} m/s\n' +
                                f'{readings["wind_direction"]}', font = font_body)

    draw_red.text((2, 44), 'T:\nP:\nH:\nL:\n', font = font_body)
    draw_red.text((124, 44), 'R:\nW:\nD:', font = font_body)
    
    epd.display(epd.getbuffer(BlackImage), epd.getbuffer(RedImage))

    print("sleeping")
    # epd.Clear()
    epd.sleep()

    print("exiting")
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    exit()

except IOError as e:
    print(e)