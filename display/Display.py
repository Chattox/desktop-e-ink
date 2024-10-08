import os
import logging
import pytz
from PIL import Image, ImageDraw, ImageFont
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime
from waveshare_epd import epd2in13b_V4

logger = logging.getLogger(__name__)

font_dir = os.path.join(os.path.dirname(os.path.relpath(__file__)), "../font")

class Display:
    """Creation and display of reading image"""
    def __init__(self, reading):
        self.epd = epd2in13b_V4.EPD()
        self.font_header = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Regular.ttf'), 20)
        self.font_body = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Thin.ttf'), 16)
        self.font_caption = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Thin.ttf'), 12)
        self.BlackImage = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.RedImage = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw_black = ImageDraw.Draw(self.BlackImage)
        self.draw_red = ImageDraw.Draw(self.RedImage)
        self.reading = reading

    def get_polygon_coords(self, start, type):
        """Return coordinates for change indicator polygons
        
        Args
        -----
        start: `tuple`
            Starting position for polygon placement, assumes top right corner
        type: `str`
            Type of polygon to make, can be either `inc`, `dec`, or `same`

        Returns
        -----
        `tuple(tuple)`
            tuple containing indicator polygon coords
        """
        if type == "inc":
            bottom_left = (start[0], start[1] + 6)
            bottom_right = (start[0] + 6, start[1] + 6)
            top = (start[0] + 3, start[1])
            return (bottom_left, bottom_right, top)
        elif type == "dec":
            top_left = (start[0], start[1])
            top_right = (start[0] + 6, start[1])
            bottom = (start[0] + 3, start[1] + 6)
            return (top_left, top_right, bottom)
        elif type == "same":
            top_left = (start[0], start[1] + 3)
            top_right = (start[0] + 6, start[1] + 3)
            bottom_left = (start[0], start[1] + 4)
            bottom_right = (start[0] + 6, start[1] + 4)
            return (top_left, top_right, bottom_left, bottom_right)

    def get_weather_icon(self):
        """Returns most appropriate weather icon based on current conditions
        
        Returns
        -----
        `Image`
            Image object of weather icon bmp
        """
        sunrise, sunset = self.get_sunrise_sunset_times().values()

        if self.reading.rain > 0:
            return Image.open('./display/icons/rain.bmp')
        elif self.reading.wind_speed > 8:
            return Image.open('./display/icons/wind.bmp')
        elif self.reading.luminance >= 3000:
            return Image.open('./display/icons/sun.bmp')
        elif self.reading.luminance < 3000 and self.reading.luminance >= 800:
            return Image.open('./display/icons/cloudy.bmp')
        elif self.reading.luminance < 800:
            if sunrise < datetime.now(pytz.timezone("Europe/London")) < sunset:
                return Image.open('./display/icons/cloud.bmp')
            else:
                return Image.open('./display/icons/moon.bmp')

    def get_sunrise_sunset_times(self):
        """Returns times of sunrise and sunset
        
        Returns
        -----
        `dict`
            dict containing `sunrise` and `sunset` times
        """
        location = LocationInfo(os.environ.get("LATITUDE"), os.environ.get("LONGITUDE"))
        s = sun(location.observer, date = datetime.now(), tzinfo = location.timezone)
        
        return {
            "sunrise": s["sunrise"],
            "sunset": s["sunset"]
        }
        

    def init_display(self):
        """Initialise and clear e-ink display"""
        logger.info('Initialising and clearing display')
        self.epd.init()
        self.epd.Clear()

    def draw_reading(self, dev):
        """Create and display reading image on e-ink display
        
        Args
        -----
        dev: `bool`
            If true, will display image in window and not affect e-ink display
        """
        logger.info('Drawing reading display')
        # Create title, last reading time, and dividers
        self.draw_black.text((2, 2), 'Weathervane', font = self.font_header)
        self.draw_black.text((138, 9), f'As of: {self.reading.time_str}', font = self.font_caption)
        self.draw_black.line((0, 26, 250, 26), fill = 0)
        self.draw_black.line((124, 26, 124, 122), fill = 0)

        # Reading content
        line_spacing = 24
        red_l_start_x = 2
        red_r_start_x = 129
        blk_l_start_x = 18
        blk_r_start_x = 148
        start_y = 30
        ind_l_start_x = 114
        ind_r_start_x = 240
        ind_start_y = 36

        columns = ({
            "temperature": ("T:", f"{self.reading.temperature} °C"),
            "pressure": ("P:", f"{self.reading.pressure} hPA"),
            "humidity": ("H:", f"{self.reading.humidity} %"),
            "luminance": ("L:", f"{self.reading.luminance} Lx"),
        },
        {
            "rain": ("R:", f"{self.reading.rain} mm"),
            "wind_speed": ("W:", f"{self.reading.wind_speed} m/s"),
            "wind_direction": ("D:", f"{self.reading.wind_direction}")
        })

        # Programatically create reading display
        for i, column in enumerate(columns):
            for j, readingData in enumerate(column.items()):
                self.draw_red.text((red_l_start_x if i == 0 else red_r_start_x, start_y + (j * line_spacing)), readingData[1][0], font = self.font_body)
                self.draw_black.text((blk_l_start_x if i == 0 else blk_r_start_x, start_y + (j * line_spacing)), readingData[1][1], font = self.font_body)
                if readingData[0] != "wind_direction":
                    self.draw_red.polygon(self.get_polygon_coords((ind_l_start_x if i == 0 else ind_r_start_x, ind_start_y + (j * line_spacing)), self.reading.changes[readingData[0]]), fill = 0)

        # Add weather icon
        self.RedImage.paste(self.get_weather_icon(), (224, 96))


        # If dev == true, display in window
        if dev:
            dev_image = Image.composite(self.BlackImage, self.RedImage, self.RedImage)
            dev_image.show()
        else:
            # Flip images to compensate for display orientation in the case I'm using
            BlackDisplayImg = self.BlackImage.transpose(Image.ROTATE_180)
            RedDisplayImg = self.RedImage.transpose(Image.ROTATE_180)
            # Send image to e-ink display and draw
            self.epd.display(self.epd.getbuffer(BlackDisplayImg), self.epd.getbuffer(RedDisplayImg))

    def sleep(self, clear_display):
        """Set the e-ink display to sleep mode and optionally clear display
        
        Args
        -----
        clear_display: `bool`
            Whether or not to clear display before sleeping
        """
        if clear_display:
            logger.info("Clearing display")
            self.epd.Clear()
        
        logger.info("Sleeping")
        self.epd.sleep()

    def cleanup(self):
        """Run cleanup before exiting"""
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
