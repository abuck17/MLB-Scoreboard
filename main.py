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
from mlb_api import MLB_API

matrix = Matrix()

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def rjust(string, length, character):
    while len(string) < length:
        string = character + string
    return string

def ljust(string, length, character):
    while len(string) < length:
        string = string + character
    return string

def display(payload):
    
    print(payload)
        
    if payload["Type"] == "Startup":
                
        group = displayio.Group()

        group.append(Label(fonts.small, x=0, y=16, color=colors.yellow, text="MLB Scoreboard\nLoading...\n%s" % payload["Team"]))
            
        matrix.display.show(group)
            
    elif payload["Type"] == "Division Standings":
        
        max_iter = 17
        
        pad = 1
        
        x_offset = 1
        y_offset = 4

        header_text = "   | W | L | GB "
                
        for iter in reversed(range(max_iter)):
            
            # Save memonry by only showing standing that are displayed on scroll
            if iter == 16:
                indices = [4,3,2]
            elif iter in [15,14,13,12,11,10,9]:
                indices = [4,3,2,1]
            elif iter == 8:
                indices = [3,2,1]
            elif iter in [7,6,5,4,3,2,1]:
                indices = [3,2,1,0]
            elif iter == 0:
                indices = [2,1,0]
            
            y_scroll_offset = y_offset - iter
            
            group = displayio.Group()
            
            for idx, team in enumerate(payload["Data"]):
                
                y_scroll_offset += 8
                
                if idx not in indices:
                    continue
                
                team_name = team["Team"]
                
                wins = rjust(str(team["Wins"]), 3, " ")
                losses = rjust(str(team["Losses"]), 3, " ")
                
                games_back = str(team["Games Back"])
                if games_back == "-":
                    games_back += " "
                games_back = rjust(games_back, 4, " ")
                
                team_name_text_data = "%s" % team_name
                                       
                # Team Names     
                group.append(Label(fonts.small, x=x_offset, y=y_scroll_offset, scale=1, 
                                   color=colors.yellow, text=team_name_text_data))
                
                team_stats_text_data = "   |%s|%s|%s" % (wins, losses, games_back)
                                 
                # Team Data           
                group.append(Label(fonts.small, x=x_offset - pad, y=y_scroll_offset, scale=1, 
                                   color=colors.yellow, text=team_stats_text_data))
                
                # Separators
                group.append(Polygon([(-1, 3+y_scroll_offset), (65, 3+y_scroll_offset), 
                                      (65, y_scroll_offset-5), (-1, y_scroll_offset-5)], outline=colors.grey))   
                
            # Header
            group.append(Label(fonts.small, x=x_offset - pad, y=y_offset, scale=1, 
                    color=colors.yellow, background_color=colors.green, text=header_text))
            
            # Stationary Boarder
            group.append(Polygon([(0, -1), (0, 32), (13, 32), (13, -1), (29, -1), (29, 32), (45, 32), (45, -1), 
                                (63, -1), (63, 31), (0, 31), (0, 0), (62, 0), (62, 6), (0, 6)], outline=colors.grey))       
                                 
            matrix.display.show(group)
            
            if iter == max_iter - 1:
                time.sleep(5.0)
        
    elif payload["Type"] == "Live Score":
                        
        group = displayio.Group()
                
        group.append(Polygon([(32, -1), (32, 33)], outline=colors.white))
        
        group.append(Rect(0, 0, 16, 16, fill=colors.team[payload["Away Team"]]["Secondary"]))
        group.append(Rect(16, 0, 16, 16, fill=colors.team[payload["Home Team"]]["Primary"]))
        
        group.append(Label(fonts.medium, x=1, y=5, color=colors.team[payload["Away Team"]]["Primary"], 
                        text=payload["Away Team"]))
        
        group.append(Label(fonts.small, x=7, y=12, color=colors.white, text=rjust(str(payload["Away Score"]), 2, " ")))
        
        group.append(Label(fonts.medium, x=17, y=5, color=colors.team[payload["Home Team"]]["Secondary"], 
                    text=payload["Home Team"]))
        
        group.append(Label(fonts.small, x=23, y=12, color=colors.white, text=rjust(str(payload["Home Score"]), 2, " ")))
        
        batter = str(payload["Batter"])
        batter_text = '%s' % batter.split()[-1]
        group.append(Label(fonts.small, x=0, y=28, color=colors.yellow, text=batter_text[:8]))

        
        pitcher = str(payload["Pitcher"])
        pitcher_text = '%s' % pitcher.split()[-1]
        group.append(Label(fonts.small, x=0, y=21, color=colors.yellow, text=pitcher_text[:8]))
         
        if payload["Is Inning Complete"] and payload["Outs"] >= 3:
            
            if payload["Half Inning"] == "bottom":
                inning_text = "END"
            elif payload["Half Inning"] == "top":
                inning_text = "MID"
            group.append(Label(fonts.medium, x=42, y=12, color=colors.yellow, text=inning_text))
                        
            inning_text = ordinal(payload["Inning"])
            if len(inning_text) == 3:
                group.append(Label(fonts.medium, x=42, y=20, color=colors.yellow, text=inning_text))
            else:
                group.append(Label(fonts.medium, x=39, y=20, color=colors.yellow, text=inning_text)) 
            
        else:
            
            # First
            group.append(Polygon([(50, 12), (54, 8), (58, 12), (54, 16)], outline=colors.yellow))
            if payload["Man On First"]:
                group.append(Polygon([(51, 12), (54, 9), (57, 12), (54, 15), (52, 13), (52, 12), (54, 10), (56, 12), 
                            (54, 14), (54, 9), (55, 12), (52, 13), (54, 12)], outline=colors.white))
            
            # Second
            group.append(Polygon([(44, 6), (48, 2), (52, 6), (48, 10)], outline=colors.yellow))
            if payload["Man On Second"]:
                group.append(Polygon([(45, 6), (48, 3), (51, 6), (48, 9), (46, 7), (46, 6), (48, 4), (50, 6),
                                    (48, 8), (48, 3), (49, 6), (46, 7), (48, 5)], outline=colors.white))
                
            # Third
            group.append(Polygon([(38, 12), (42, 8), (46, 12), (42, 16)], outline=colors.yellow))
            if payload["Man On Third"]:
                group.append(Polygon([(39, 12), (42, 9), (45, 12), (42, 15), (40, 13), (40, 12), (42, 10), (44, 12), 
                                    (42, 14), (42, 9), (43, 12), (40, 13), (42, 12)], outline=colors.white))
                
            # Inning
            inning_text = str(payload["Inning"])
            if len(inning_text) == 1:
                group.append(Label(fonts.medium, x=41, y=25, color=colors.yellow, text=inning_text))
            
                if payload["Half Inning"] == "bottom":
                    group.append(Polygon([(35, 24), (39, 24), (37, 26), (35, 24), (37, 24), (37, 26)], outline=colors.yellow))
                elif payload["Half Inning"] == "top":
                    group.append(Polygon([(35, 25), (39, 25), (37, 23), (35, 25), (37, 25), (37, 23)], outline=colors.yellow))
                
            # Count
            count_text = "%d-%d" % (payload["Balls"], payload["Strikes"])
            group.append(Label(fonts.small, x=50, y=22, color=colors.yellow, text=count_text))
            
            # Out One
            fill = None
            if payload["Outs"] > 0:
                fill = colors.white
            group.append(Rect(48, 26, 4, 4, outline=colors.yellow, fill=fill))
            
            # Out Two
            fill = None
            if payload["Outs"] > 1:
                fill = colors.white
            group.append(Rect(53, 26, 4, 4, outline=colors.yellow, fill=fill))

            # Out Three
            fill = None
            if payload["Outs"] > 2:
                fill = colors.white
            group.append(Rect(58, 26, 4, 4, outline=colors.yellow, fill=fill))  
            
        matrix.display.show(group)
        
    elif payload["Type"] == "Scheduled":
        
        group = displayio.Group()
                
        group.append(Polygon([(32, -1), (32, 33)], outline=colors.white))
        
        group.append(Rect(0, 0, 16, 16, fill=colors.team[payload["Away Team"]]["Secondary"]))
        group.append(Rect(16, 0, 16, 16, fill=colors.team[payload["Home Team"]]["Primary"]))
        
        group.append(Label(fonts.medium, x=1, y=5, color=colors.team[payload["Away Team"]]["Primary"], 
                        text=payload["Away Team"]))
        
        group.append(Label(fonts.small, x=7, y=12, color=colors.white, text=rjust(str(payload["Away Score"]), 2, " ")))
        
        group.append(Label(fonts.medium, x=17, y=5, color=colors.team[payload["Home Team"]]["Secondary"], 
                    text=payload["Home Team"]))
        
        group.append(Label(fonts.small, x=23, y=12, color=colors.white, text=rjust(str(payload["Home Score"]), 2, " ")))
        
        away_pitcher = str(payload["Away Pitcher"])
        away_batter_text = '%s' % away_pitcher.split()[-1]
        group.append(Label(fonts.small, x=0, y=21, color=colors.yellow, text=away_batter_text[:8]))

        
        home_pitcher = str(payload["Home Pitcher"])
        home_pitcher_text = '%s' % home_pitcher.split()[-1]
        group.append(Label(fonts.small, x=0, y=28, color=colors.yellow, text=home_pitcher_text[:8]))
                
        date_time = payload["Date Time"].split("T")
        
        year = int(date_time[0].split("-")[0])
        month = int(date_time[0].split("-")[1])
        day = int(date_time[0].split("-")[2])
        hour = int(date_time[1].split(":")[0])
        mintue = int(date_time[1].split(":")[1])
        second = int(date_time[1].split(":")[2][:-1])
        
        utc_date_time = datetime.datetime(year, month, day, hour, mintue, second)
        timezone_delta = datetime.timedelta(hours=mlb_api.get_timezone_offset())
        timezone_date_time = utc_date_time + timezone_delta
        
        hour = timezone_date_time.hour
        minute = timezone_date_time.minute
        
        if hour == 0:
            hour_str = "12"
            meridian = "AM"
        elif hour <= 12:
            hour_str = str(hour)
            meridian = "AM"
        else:
            hour_str = str(hour - 12)
            meridian = "PM"
            
        hour_str = rjust(hour_str, 2, "0")
        minute_str = rjust(str(minute), 2, "0")
        
        time_text = hour_str + ":" + minute_str
 
        group.append(Label(fonts.small, x=39, y=13, color=colors.yellow, text=time_text))
        group.append(Label(fonts.small, x=39, y=19, color=colors.yellow, text="Start"))
        matrix.display.show(group)
        
    elif payload["Type"] == "Final Score":
        
        group = displayio.Group()
                
        group.append(Polygon([(32, -1), (32, 33)], outline=colors.white))
        
        group.append(Rect(0, 0, 16, 16, fill=colors.team[payload["Away Team"]]["Secondary"]))
        group.append(Rect(16, 0, 16, 16, fill=colors.team[payload["Home Team"]]["Primary"]))
        
        group.append(Label(fonts.medium, x=1, y=5, color=colors.team[payload["Away Team"]]["Primary"], 
                        text=payload["Away Team"]))
        
        group.append(Label(fonts.small, x=7, y=12, color=colors.white, text=rjust(str(payload["Away Score"]), 2, " ")))
        
        group.append(Label(fonts.medium, x=17, y=5, color=colors.team[payload["Home Team"]]["Secondary"], 
                    text=payload["Home Team"]))
        
        group.append(Label(fonts.small, x=23, y=12, color=colors.white, text=rjust(str(payload["Home Score"]), 2, " ")))
        
        if int(payload["Away Score"]) > int(payload["Home Score"]):
            away_pitcher = str(payload["Winner"])
            home_pitcher = str(payload["Loser"])
        else:
            away_pitcher = str(payload["Loser"])
            home_pitcher = str(payload["Winner"])
        
        away_batter_text = '%s' % away_pitcher.split()[-1]
        group.append(Label(fonts.small, x=0, y=21, color=colors.yellow, text=away_batter_text[:8]))

        home_pitcher_text = '%s' % home_pitcher.split()[-1]
        group.append(Label(fonts.small, x=0, y=28, color=colors.yellow, text=home_pitcher_text[:8]))
        
        group.append(Label(fonts.small, x=39, y=16, color=colors.yellow, text="Final"))
        matrix.display.show(group)

    else:
        print("Current support does not include type '%s'" % payload["Type"])
                
# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

display({"Type": "Startup", "Team": secrets["team"]})

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

    # Initialize a requests object with a socket and esp32spi interface
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
                    
                    display(mlb_api.get_live_score(link=games_info[in_progess.index(True)]["Link"]))
                    continue
                
                if any(scheduled):
                    
                    display(mlb_api.get_scheduled_game_info(link=games_info[scheduled.index(True)]["Link"]))
                    continue
                
                if any(final):
                    
                    display(mlb_api.get_final_score(link=games_info[final.index(True)]["Link"]))
                    continue
                    
            display(mlb_api.get_standings())
    
        except Exception as e:
            print("------------------------------------------")
            traceback.print_exception(None, e, e.__traceback__)
            print("------------------------------------------")
            break
        
