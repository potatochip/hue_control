#!/usr/bin/env python
'''
Requires pyowm in virtualenv

Originally was going to detect when a phone connected to wifi but looks like that only happens when the phone screen is turned on
Second best option is probably to have the IFTTT on the phone work with a geofence to send an email and have a cron procedure checking for that email. When that email arrives then call procedures here.
'''

import phue
import datetime
import json
import logging


with open('body_list.json') as json_file:
    body_list = json.load(json_file)

log_file = "hue_control.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

currently = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

b = phue.Bridge('192.168.1.110')
allthelights = phue.AllLights()
mainroomlights = phue.Group(b, "Main Room")
notificationlight = phue.Light(b, "Main Table")

def update_bodies(user_id):
    body_list[user_id]['status'] = 'home' if body_list[user_id]['status'] == 'away' else 'away'
    with open('body_list.json', 'w') as f:
        f.write(json.dumps(body_list, indent=4, sort_keys=True))

def anybody_home():
    for user in body_list.values():
        if user['status'] == 'home': return True
    return False

def device_to_name(device_id):
    for user in body_list:
        if body_list[user]['device_id'] == device_id: return user
    return 'Error'

#cron these procedures whenever a device connects or disconnects to the network
def welcome_back(device_id):
    user_name = device_to_name(device_id)
    update_bodies(user_name)
    if anybody_home() == True:
        pass
    else:
        mainroomlights.on = True
        mainroomlights.brightness = 219
        mainroomlights.colortemp_k = 4274
    print("%s got home at %s" % (body_list[user_name]['name'], currently))
    logging.info("%s got home at %s" % (body_list[user_name]['name'], currently))
    
def see_you_later(name):
    user_name = device_to_name(device_id)
    update_bodies(user_name)
    if anybody_home() == True:
        pass
    else: 
        allthelights.on = False
    print("%s left the apartment at %s" % (body_list[user_name]['name'], currently))
    logging.info("%s left the apartment at %s" % (body_list[user_name]['name'], currently))
    
def weather_station():
    #cron this procedure at a set time every day
    logging.info("Called the weather station.")
    import pyowm
    owm = pyowm.OWM()
    observation = owm.weather_at_place("New York, US")
    weather = observation.get_weather()
    temperature = weather.get_temperature('fahrenheit')
    forecast = owm.daily_forecast("New York, US", limit=1)
    f = forecast.get_forecast()
    rain = forecast.will_have_rain()
    snow = forecast.will_have_snow()
    avg_temp = temperature['temp']

    alert_color = 50000

    if anybody_home():
        notificationlight.on = True
        notificationlight.brightness = 100
        notificationlight.saturation=255
        if temperature < 30:
            notificationlight.hue = 47500 #electric blue
        elif temperature < 50:
            notificationlight.hue = 46000 #light_blue
        elif temperature < 70:
            notificationlight.hue = 45000 #light_light_blue
        elif temperature < 90:
            notificationlight.hue = 25000 # "green"
        else: notificationlight.hue = 5000 #red-orange
        if snow == True or rain == True:
            pass
            #rotate lights with alert_color


def main(args):
    #Function chooser
    '''
    Run functions from command line.
    $python3 hue_control.py welcome 00:61:71:CC:52:C8 
    Runs the welcome_back function with that device_id
    Will weather still work if no second argument included? might have to make a separate call for that
    '''
    func_arg = {"-welcome":welcome_back,
            "-goodbye":see_you_later,
            "-weather":weather_station
            }
    func_arg[args[1]]() if args[1] == '-weather' else func_arg[args[1]](args[2])

if __name__ == "__main__":
    import sys
    main(sys.argv)
    # func_arg[sys.argv[1]]() if sys.argv[1] == '-weather' else func_arg[sys.argv[1]](sys.argv[2])
    # alt method below
    # try:
    #     func_arg[sys.argv[1]](sys.argv[2])
    # except IndexError:
    #     try:
    #        func_arg[sys.argv[1]]()
    # except IndexError:
    #     print('no valid args passed. running main program.')
    #     pass
