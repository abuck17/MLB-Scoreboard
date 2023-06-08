import traceback
import time
import board
import busio
import displayio
import digitalio

from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.polygon import Polygon
from adafruit_matrixportal.matrix import Matrix

import adafruit_esp32spi.adafruit_esp32spi as esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests
import adafruit_datetime as datetime

import colors
import fonts
import display
from mlb_api import MLB_API

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

display.render({"Type": "Startup", "Team": secrets["team"]})

while True:

    esp.reset()
    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except ConnectionError as e:
            print("could not connect to AP, retrying: ", e)
            continue
    print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)

    socket.set_interface(esp)
    requests.set_socket(socket, esp) 

    mlb_api = MLB_API(team=secrets["team"], time_zone=secrets["timezone"], request_lib=requests)

    while True:
        
        try:
        
            games_info = mlb_api.get_info_on_todays_games()
            
            print(games_info)
                        
            if games_info:
                                                
                in_progess = [game_info["State"] == "In Progress" for game_info in games_info]
                scheduled = [game_info["State"] in ["Pre-Game", "Scheduled", "Warmup"] for game_info in games_info]
                delayed = [game_info["State"] in ["Postponed"] for game_info in games_info]
                final = [game_info["State"] in ["Final", "Game Over"] for game_info in games_info]
                        
                if any(in_progess):
                    
                    display.render(mlb_api.get_live_score(link=games_info[in_progess.index(True)]["Link"]))
                    continue
                
                if any(scheduled):
                    
                    display.render(mlb_api.get_scheduled_game_info(link=games_info[scheduled.index(True)]["Link"]))
                    continue
                
                if any(final):
                    
                    display.render(mlb_api.get_final_score(link=games_info[final.index(True)]["Link"]))
                    continue
                    
            display.render(mlb_api.get_standings())
    
        except Exception as e:
            print("------------------------------------------")
            traceback.print_exception(None, e, e.__traceback__)
            print("------------------------------------------")
            break
        
