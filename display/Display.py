import os
import logging
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13b_V4

# logging.basicConfig(level=logging.INFO)
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

    def init_display(self):
        """Initialise and clear e-ink display"""
        logger.info('Initialising and clearing display')
        self.epd.init()
        self.epd.Clear()

    def draw_reading(self):
        """Create and display reading image on e-ink display"""
        logger.info('Drawing reading display')
        self.draw_black.text((2, 2), 'Weathervane', font = self.font_header)
        self.draw_black.line((0, 26, 250, 26), fill = 0)
        self.draw_black.text((2, 28), f'Time of reading: {self.reading.time_str}', font = self.font_caption)
        self.draw_black.text((18, 44), f'{self.reading.temperature} °C\n' +
                              f'{self.reading.pressure} hPa\n' +
                              f'{self.reading.humidity} %\n' +
                              f'{self.reading.luminance} Lx', font = self.font_body)
        self.draw_black.text((143, 44), f'{self.reading.rain} mm\n' +
                                f'{self.reading.wind_speed} m/s\n' +
                                f'{self.reading.wind_direction}', font = self.font_body)
        self.draw_red.text((2, 44), 'T:\nP:\nH:\nL:\n', font = self.font_body)
        self.draw_red.text((124, 44), 'R:\nW:\nD:', font = self.font_body)

        self.epd.display(self.epd.getbuffer(self.BlackImage), self.epd.getbuffer(self.RedImage))

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