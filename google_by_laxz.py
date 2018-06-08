#!/usr/bin/env python



# Copyright (C) 2017 Google Inc.

#

# Licensed under the Apache License, Version 2.0 (the "License");

# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at

#

#     http://www.apache.org/licenses/LICENSE-2.0

#

# Unless required by applicable law or agreed to in writing, software

# distributed under the License is distributed on an "AS IS" BASIS,

# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# See the License for the specific language governing permissions and

# limitations under the License.





# This Google SDK hotword.py was modified by Min Latt with 

# no distribution n only for my testings

# I combined Google hotword.py with OLED Display

# Using SPI Interface between OLED device and Raspberry Pi

# And I used Google Assistant's voice feedback ON_RENDER_RESPONSE

# to text and

# display in OLED just that.



# From Google (importing __future__ must be very first)

from __future__ import print_function





# To convert modified str to dict

from yaml import load

#################################

import datetime

# For OLED ######################

import os

from random import randrange

from PIL import Image,ImageFont

from luma.core.virtual import terminal

from luma.core.render import canvas

#################################

dateString = '%d,%m,%Y(%b,%a) %I:%M:%S -%p-'

# Connection with device #######

def get_device():

    DC = 24

    RST = 25

    from luma.oled.device import sh1106

    from luma.core.interface.serial import spi

    serial = spi(device=0, port=0, bus_speed_hz=8000000, transfer_size=4096, gpio_DC=DC, gpio_RST=RST)

    return(sh1106(serial, rotate=2))

###############################

device = get_device()

# Font Init ###################

def make_font(name, size):

    font_path = os.path.abspath(os.path.join(

        os.path.dirname(__file__), 'fonts', name))

    return ImageFont.truetype(font_path, size)

###############################



# Main Funtion ################

def print_terminal(event):

    for fontname, size in [("ProggyTiny.ttf", 16)]:

        font = make_font(fontname, size) if fontname else None

        term = terminal(device, font)

        term.println(event)

        time.sleep(1)

        term.clear()

        term.println(datetime.datetime.now().strftime(dateString))

###############################



# Logo ########################

def logo(a,b):

    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),

        'image','pi_logo.png'))

    logo = Image.open(img_path).convert("RGBA")

    fff = Image.new(logo.mode, logo.size, (255,) * 4 )



    background = Image.new("RGBA", device.size, "white")

    posn = ((device.width - logo.width) //2 , 0)

    while True:

        for angle in range(0, 360, 2):

            rot = logo.rotate(angle, resample=Image.BILINEAR)

            img = Image.composite(rot, fff, rot)

            background.paste(img, posn)

            device.display(background.convert(device.mode))

        if a==b:

            break

###############################



# Google Assistant ############

import argparse,os.path,json



import google.auth.transport.requests

import google.oauth2.credentials



import RPi.GPIO as GPIO

import time



from google.assistant.library import Assistant

from google.assistant.library.event import EventType

from google.assistant.library.file_helpers import existing_file





DEVICE_API_URL = 'https://embeddedassistant.googleapis.com/v1alpha2'





def process_device_actions(event, device_id):

    if 'inputs' in event.args:

        for i in event.args['inputs']:

            if i['intent'] == 'action.devices.EXECUTE':

                for c in i['payload']['commands']:

                    for device in c['devices']:

                        if device['id'] == device_id:

                            if 'execution' in c:

                                for e in c['execution']:

                                    if 'params' in e:

                                        yield e['command'], e['params']

                                    else:

                                        yield e['command'], None





def process_event(event, device_id):

    """Pretty prints events.

    Prints all events that occur with two spaces between each new

    conversation and a single space between turns of a conversation.

    Args:

        event(event.Event): The current event to process.

        device_id(str): The device ID of the new instance.

    """





    #if event.type != EventType.ON_CONVERSATION_TURN_STARTED:

    #    logo(event.type,EventType.ON_CONVERSATION_TURN_STARTED)



    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:

        print()

        print('Listening on, Sir.')

        GPIO.output(16,1)





    if event.type == EventType.ON_RENDER_RESPONSE:

        a = str(event).replace("ON_RENDER_RESPONSE:"," ")

        a = load(a.replace('\n',' ').replace("    ",""))

        a = a["text"]

        #print(a)

        try:

            device = get_device()

            print_terminal(a)

        except KeyboardInterrupt:

            pass

#    print(event)

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and

            event.args and not event.args['with_follow_on_turn']):

        GPIO.output(16,0)

        #GPIO.output(25,0) #to turn of oled (RST to ground) 

    if event.type == EventType.ON_DEVICE_ACTION:

        for command, params in process_device_actions(event, device_id):

            print('Do command', command, 'with params', str(params))

            if command == "com.example.commands.BlinkLight":

                number = int( params['number'] )

                for i in range(int(number)):

                    print('Device is blinking')

                    GPIO.output(26,1)

                    time.sleep(1)

                    GPIO.output(26,0)

                    time.sleep(1)

            """if command == "action.devices.commands.OnOff":

                if params['on']:

                    print('Turning the LED on.')

                    GPIO.output(26,1)

                else:

                    print('Turning the LED off.')

                    GPIO.output(26,0)"""

            """if command == "action.devices.commands.BrightAbsolute":

                if params['brightness']:

                    pwm_led = GPIO.PWM(25,20)

                    #pwm_led.start(int(params['brightness']))

                    if params['brightness'] > 50:

                        print('brightness > 50')

                    else:

                        print('brightness <= 50')"""

def register_device(project_id, credentials, device_model_id, device_id):

    """Register the device if needed.



    Registers a new assistant device if an instance with the given id

    does not already exists for this model.



    Args:

       project_id(str): The project ID used to register device instance.

       credentials(google.oauth2.credentials.Credentials): The Google

                OAuth2 credentials of the user to associate the device

                instance with.

       device_model_id(str): The registered device model ID.

       device_id(str): The device ID of the new instance.

    """

    base_url = '/'.join([DEVICE_API_URL, 'projects', project_id, 'devices'])

    device_url = '/'.join([base_url, device_id])

    session = google.auth.transport.requests.AuthorizedSession(credentials)

    r = session.get(device_url)

    print(device_url, r.status_code)

    if r.status_code == 404:

        print('Registering....')

        r = session.post(base_url, data=json.dumps({

            'id': device_id,

            'model_id': device_model_id,

            'client_type': 'SDK_LIBRARY'

        }))

        if r.status_code != 200:

            raise Exception('failed to register device: ' + r.text)

        print('\rDevice registered.')





def main():

    parser = argparse.ArgumentParser(

        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--credentials', type=existing_file,

                        metavar='OAUTH2_CREDENTIALS_FILE',

                        default=os.path.join(

                            os.path.expanduser('~/.config'),

                            'google-oauthlib-tool',

                            'credentials.json'

                        ),

                        help='Path to store and read OAuth2 credentials')

    parser.add_argument('--device_model_id', type=str,

                        metavar='DEVICE_MODEL_ID', required=True,

                        help='The device model ID registered with Google')

    parser.add_argument(

        '--project_id',

        type=str,

        metavar='PROJECT_ID',

        required=False,

        help='The project ID used to register device instances.')

    parser.add_argument(

        '-v',

        '--version',

        action='version',

        version='%(prog)s ' +

        Assistant.__version_str__())



    args = parser.parse_args()

    with open(args.credentials, 'r') as f:

        credentials = google.oauth2.credentials.Credentials(token=None,

                                                            **json.load(f))



    with Assistant(credentials, args.device_model_id) as assistant:

        events = assistant.start()



        print('device_model_id:', args.device_model_id + '\n' +

              'device_id:', assistant.device_id + '\n')



        GPIO.setmode(GPIO.BCM)

        GPIO.setup(16,GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(26,GPIO.OUT, initial=GPIO.LOW) #GPIO25 #physical37



        if args.project_id:

            register_device(args.project_id, credentials,

                            args.device_model_id, assistant.device_id)



        for event in events:

            process_event(event, assistant.device_id)

            #if(EventType.ON_RENDER_RESPONSE == event.type):

                #print(event.type)



if __name__ == '__main__':

    main()