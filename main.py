import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13b_V4

font_dir = os.path.join(os.path.dirname(os.path.relpath(__file__)), "font")

load_dotenv()
API_URL = os.environ.get("WEATHERVANE_API_URL")

r = requests.get(url= API_URL)
data = r.json()
readings = data[0]['readings']
reading_time = datetime.strptime(data[0]['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
time_string = reading_time.strftime('%d/%m/%y %H:%M')

print(readings)

try:
    epd = epd2in13b_V4.EPD()
    print("Initialising and clearing display")
    epd.init()
    epd.Clear()

    print("Drawing")
    font_header = ImageFont.truetype(os.path.join(font_dir, 'Font.ttc'), 20)
    font_body = ImageFont.truetype(os.path.join(font_dir, 'Font.ttc'), 16)
    font_caption = ImageFont.truetype(os.path.join(font_dir, 'Font.ttc'), 12)
    BlackImage = Image.new('1', (epd.height, epd.width), 255)
    RedImage = Image.new('1', (epd.height, epd.width), 255)
    draw_black = ImageDraw.Draw(BlackImage)
    draw_red = ImageDraw.Draw(RedImage)
    draw_black.text((2, 2), 'Weathervane', font = font_header)
    draw_black.line((0, 26, 250, 26), fill = 0)
    draw_black.text((2, 28), f'Time of reading: {time_string}', font = font_caption)
    draw_black.text((2, 44), f'T: {readings["temperature"]} C\n' +
                              f'P: {readings["pressure"]} hPa\n' +
                              f'H: {readings["humidity"]} %\n' +
                              f'L: {readings["luminance"]} Lx', font = font_body)
    draw_black.text((125, 44), f'R: {readings["rain"]} mm\n' +
                                f'W: {readings["wind_speed"]} m/s\n' +
                                f'D: {readings["wind_direction"]}', font = font_body)
    
    epd.display(epd.getbuffer(BlackImage), epd.getbuffer(RedImage))

    print("sleeping")
    epd.sleep()

    print("exiting")
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    exit()

except IOError as e:
    print(e)