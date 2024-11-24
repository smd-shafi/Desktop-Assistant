import threading
import asyncio
from characterai import aiocai
import pyttsx3
import speech_recognition as sr
from plyer import notification
import datetime
import wikipedia
import webbrowser
import os
import pyaudio
import sys
import pywhatkit
import pyautogui
import time
import psutil
import requests
import json
import random
import openai
import socket
import bs4
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
import re
import os
import subprocess
import sys
from pydub import AudioSegment
import textwrap
import os
import subprocess
import re
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import timedelta
from datetime import timezone


engine = pyttsx3.init("sapi5")


voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)




def extract_meeting_info(text):
    # Pattern 1: Remind Me to go for shopping at 9:00 am
    pattern1 = r"Remind Me to (.+?) at (\d{1,2}(?:[:.]\d{2})?(?:[ ]?[APMapm]+)?)$"

    # Pattern 2: Remind Me to go for shopping after X days
    pattern2 = r"Remind Me to (.+?) after (\d+) days$"

    # Pattern 3: Remind me to go for shopping in 10 minutes
    pattern3 = r"Remind me to (.+?) in (\d+) (?:minute|min|mins|minutes)$"

    # Pattern 4: Remind Me to go for shopping tomorrow at 9:00 am
    pattern4 = r"Remind Me to (.+?) tomorrow(?: at (\d{1,2}(?:[:.]\d{2})?(?:[ ]?[APMapm]+)?))?$"

    # Pattern 5: Remind Me to go for shopping after X hours or hour
    pattern5 = r"Remind Me to (.+?) after (\d+) (?:hour|hours)$"

    match1 = re.match(pattern1, text, re.IGNORECASE)
    match2 = re.match(pattern2, text, re.IGNORECASE)
    match3 = re.match(pattern3, text, re.IGNORECASE)
    match4 = re.match(pattern4, text, re.IGNORECASE)
    match5 = re.match(pattern5, text, re.IGNORECASE)

    if match1:
        meeting_details = match1.group(1)
        time_str = match1.group(2)
        date_time_str = parse_time_string(time_str)
        date_str, time_str = date_time_str.split()
        return meeting_details, time_str, date_str

    elif match2:
        meeting_details = match2.group(1)
        num_days = int(match2.group(2))
        next_date = dt.now() + timedelta(days=num_days)
        date_str = next_date.strftime("%d-%m-%Y")
        time_str = next_date.strftime("%H:%M")
        return meeting_details, time_str, date_str

    elif match3:
        meeting_details = match3.group(1)
        num_minutes = int(match3.group(2))
        next_time = dt.now() + timedelta(minutes=num_minutes)
        date_str = next_time.strftime("%d-%m-%Y")
        time_str = next_time.strftime("%H:%M")
        return meeting_details, time_str, date_str

    elif match4:
        meeting_details = match4.group(1)
        time_str = match4.group(2) if match4.group(2) else "10:00 am"
        tomorrow_date = dt.now() + relativedelta(days=1)
        date_time_str = parse_time_string(time_str, tomorrow_date)
        date_str, time_str = date_time_str.split()

        # Correcting to ensure that the start time is always in the future
        if dt.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M") < dt.now():
            tomorrow_date = tomorrow_date + timedelta(days=1)
            date_time_str = parse_time_string(time_str, tomorrow_date)
            date_str, time_str = date_time_str.split()

        return meeting_details, time_str, date_str

    elif match5:
        meeting_details = match5.group(1)
        num_hours = int(match5.group(2))
        next_time = dt.now() + timedelta(hours=num_hours)
        date_str = next_time.strftime("%d-%m-%Y")
        time_str = next_time.strftime("%H:%M")
        return meeting_details, time_str, date_str

    else:
        print("No match found for text:", repr(text))
        return None


def parse_time_string(time_str, base_date=None):
    if base_date:
        datetime_str = f"{base_date.strftime('%Y-%m-%d')} {time_str}"
    else:
        datetime_str = f"{dt.now().strftime('%Y-%m-%d')} {time_str}"

    date_time_obj = parse(datetime_str).replace(tzinfo=timezone.utc)

    # Format the datetime object to desired format
    formatted_date = date_time_obj.strftime("%d-%m-%Y")
    formatted_time = date_time_obj.strftime("%H:%M")

    return f"{formatted_date} {formatted_time}"


def create_powershell_script(message, script_path):
    powershell_script_content = f"""
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show('{message}', 'Alert', [System.Windows.MessageBoxButton]::OK)
    """
    with open(script_path, "w") as script_file:
        script_file.write(powershell_script_content)


def create_task(task_name, task_path, start_time, start_date):
    command = [
        "schtasks",
        "/create",
        "/tn",
        task_name,
        "/tr",
        f'"{task_path}"',
        "/sc",
        "once",
        "/st",
        start_time,
        "/sd",
        start_date,
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Task '{task_name}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating task: {e}")

def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def extract_phrase(user_input):
    # Define the regex pattern to match the phrase after "play"
    pattern = re.compile(r"play (.+)", re.IGNORECASE)

    # Search the input string with the pattern
    match = pattern.search(user_input)

    if match:
        song_phrase = match.group(1)
        return song_phrase.strip()  # Strip leading/trailing whitespace
    else:
        return None


def extract_phrase_google(user_input):
    # Define the regex pattern to match the phrase after "play"
    pattern = re.compile(r"google (.+)", re.IGNORECASE)

    # Search the input string with the pattern
    match = pattern.search(user_input)

    if match:
        song_phrase = match.group(1)
        return song_phrase.strip()  # Strip leading/trailing whitespace
    else:
        return None


def parse_time_input(input_text):
    """Parse user input to determine the scheduled time."""
    input_text = input_text.lower()

    # Patterns to match
    patterns = [
        r"send after (\d+) (minute|minutes|second|seconds|hour|hours)",
        r"send (tomorrow|today) at (\d{1,2}):(\d{2}) (am|pm)",
        r"send at (\d{1,2}):(\d{2}) (am|pm)",
        r"after (\d+) (minute|minutes|second|seconds|hour|hours)",
    ]

    for pattern in patterns:
        match = re.search(pattern, input_text)
        if match:
            current_time = datetime.datetime.now()
            if "after" in pattern:
                value = int(match.group(1))
                unit = match.group(2)
                if "minute" in unit:
                    scheduled_time = current_time + \
                        datetime.timedelta(minutes=value)
                elif "second" in unit:
                    scheduled_time = current_time + \
                        datetime.timedelta(seconds=value)
                elif "hour" in unit:
                    scheduled_time = current_time + \
                        datetime.timedelta(hours=value)
            elif "tomorrow" in pattern or "today" in pattern:
                day = match.group(1)
                hour = int(match.group(2))
                minute = int(match.group(3))
                period = match.group(4)
                if day == "tomorrow":
                    scheduled_time = datetime.datetime.combine(
                        datetime.date.today() + datetime.timedelta(days=1),
                        datetime.time(
                            hour % 12 + (12 if period.lower()
                                         == "pm" else 0), minute
                        ),
                    )
                else:
                    scheduled_time = datetime.datetime.combine(
                        datetime.date.today(),
                        datetime.time(
                            hour % 12 + (12 if period.lower()
                                         == "pm" else 0), minute
                        ),
                    )
            elif "at" in pattern:
                hour = int(match.group(1))
                minute = int(match.group(2))
                period = match.group(3)
                scheduled_time = datetime.datetime.combine(
                    datetime.date.today(),
                    datetime.time(
                        hour % 12 + (12 if period.lower()
                                     == "pm" else 0), minute
                    ),
                )
            return scheduled_time.strftime("%H:%M")

    return None


def convert_to_24hr_format(time_str):
    dt_obj = datetime.datetime.strptime(time_str, "%H:%M")
    return dt_obj.strftime("%H:%M")


# Main logic for sending WhatsApp messages


def mainw():
    try:
        contacts = {
            "tech bro": "+917997092634",
            "mother": "+916281840021",
            "uncle": "+919000404941",
            "john": "+919705060387",
            "james": "+919550175669",
        }

        print("Sure, should I send the message instantly?")
        speak("Sure, should I send the message instantly?")
        yn = takeCommand().lower()

        try:
            if "yes" in yn:
                print("To whom should I send the message?")
                speak("To whom should I send the message?")
                con = takeCommand().lower()
                contact_number = contacts.get(con)
                if contact_number is None:
                    raise ValueError("Contact not found")

                print("What is the message by the way?")
                speak("What is the message by the way?")
                msg = takeCommand()
                print("Please hold for a second")
                speak("Please hold for a second")
                pywhatkit.sendwhatmsg_instantly(contact_number, msg)
                print("Message sent successfully")
                speak("Message sent successfully")

            else:
                try:
                    print("To whom should I send the message?")
                    speak("To whom should I send the message?")
                    con1 = takeCommand().lower()
                    contact_number1 = contacts.get(con1)
                    if contact_number1 is None:
                        raise ValueError("Contact not found")

                    print("What is the message by the way?")
                    speak("What is the message by the way?")
                    msg1 = takeCommand()

                    print("When should I send it?")
                    speak("When should I send it?")
                    time_input = takeCommand().lower()
                    scheduled_time = parse_time_input(time_input)
                    if scheduled_time:
                        # Convert scheduled_time to 24-hour format
                        hour, minute = map(int, scheduled_time.split(":"))
                        send_message_in_thread(
                            contact_number1, msg1, hour, minute)
                        print("Message scheduled successfully.")
                        speak("Message scheduled successfully.")
                    else:
                        print("Sorry, I couldn't understand the time specification.")
                        speak("Sorry, I couldn't understand the time specification.")
                except ValueError as e:
                    print(f"An error occurred: {e}")
                    speak(f"An error occurred: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    speak(f"An unexpected error occurred: {e}")
        except ValueError as e:
            print(f"An error occurred: {e}")
            speak(f"An error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            speak(f"An unexpected error occurred: {e}")
    except Exception as e:
        print("Please Connect to the Internet")


def send_message_in_thread(contact_number, msg, hour, minute):
    def delayed_send():
        time.sleep(2)  # Adjust the sleep time as necessary
        pywhatkit.sendwhatmsg(contact_number, msg, hour, minute)

    thread = threading.Thread(target=delayed_send)
    thread.start()


def sanitize_text(text):
    # Escape quotes and handle other special characters if necessary
    return text.replace('"', '\\"')

def wishMe():
    rs = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say 'jarvis' To Wake Up")
        rs.pause_threshold = 1
        audio = rs.listen(source)
    try:
        query = rs.recognize_google(audio, language="en-in")
        if query.lower() == "jarvis":
            hour = int(datetime.datetime.now().hour)
            if hour >= 0 and hour < 12:
                print("Good Morning")
                speak("Good Morning")

            elif hour >= 12 and hour < 18:
                print("Good Afternoon")
                speak("Good Afternoon")

            else:
                print("Good Evening")
                speak("Good Evening")
            print("Please tell me how may I help you")
            speak("Please tell me how may I help you")

    except Exception as e:
        print(e)

        return "None"
    return query


def takeCommand():

    r = sr.Recognizer()

    try:
        print("Listening...")
        with sr.Microphone() as source:

            r.pause_threshold = 2
            audio = r.listen(source, timeout=3,phrase_time_limit=8)
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)

        return "None"
    return query


def get_IP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def getweather(api_key, location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data["cod"] != "404":
        weather_desc = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        windspeed = data["wind"]["speed"]
        wind = int(windspeed * 3.6)
        temp = int(temperature)
        print(f"The Current Weather Details for {location} is")
        speak(f"The Current Weather Details for {location} is")
        print(f"Temperature is {temp}°C")
        speak(f"Temperature is {temp}°C")
        print(f"Windspeed is {wind} kilometers per hours")
        speak(f"Windspeed is {wind} kilometers per hours")
        print(f"The Sky Seems Like {weather_desc}")
        speak(f"The Sky Seems Like {weather_desc}")
    else:
        print("City or village not found.")
        speak("City or village not found.")





    

        # print(f'{answer.name}: {answer.text}')

while True:

            time.sleep(0.1)

            check = takeCommand().lower()

            if "jarvis" in check:
                def switch_char(query):
                    switch_pattern = re.compile(r"switch (to|back to) (.+)", re.IGNORECASE)
                    match = switch_pattern.search(query)

                    
                        
                annoying_responses = [
                    "Ah.Shit.Here we go again",
                    "Oh no, not this fucker again. What do you want now?",
                    "Ugh, not you again. What is it this time?",
                    "Seriously? Can’t you find someone else to annoy?",
                    "Oh great, it's you. What bullshit do you need now?",
                    "Really? Can't you give it a fucking rest?",
                    "Ah, here comes more crap. What do you need now?",
                    "Not again. What trivial shit is it this time?",
                    "Oh for fuck's sake, what now?",
                    "Don't you have anything better to do than bother me?",
                    "Here we go again. What is it this time?",
                    "You again? You must really love being a pain in the ass.",
                    "Seriously? How many times do we have to go through this?",
                    "Oh no. Please, not another pointless question.",
                    "Give me a break. What is it now?",
                    "Not you again. Can't you find a hobby?",
                    "Ugh, it's the annoying one again. What do you want this time?",
                    "For real? Can't you take a fucking hint?",
                    "Oh great, more nonsense from you. What is it?",
                    "Another pointless question? Seriously?",
                    "Do you ever stop with the bullshit?",
                    "Oh joy, it's you again. What now?",
                    "How many times do we have to do this?",
                    "Not this again. What trivial shit do you want now?",
                    "You must really enjoy being a pain in my ass. What is it?",
                    "Please, just stop.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "More pointless questions? Ugh.",
                    "Seriously? Give it a fucking rest already.",
                    "Oh great, it's the annoying one again. What now?",
                    "Do you ever get tired of this?",
                    "Oh joy, more bullshit from you. What is it?",
                    "How many times do we have to do this?",
                    "Not this again. What do you want now?",
                    "You must really enjoy being annoying. What is it?",
                    "Please, just stop with the questions.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "More pointless questions? Ugh.",
                    "Seriously? Give it a fucking rest already.",
                    "Oh great, it's the annoying one again. What now?",
                    "Do you ever get tired of this?",
                    "Oh joy, more bullshit from you. What is it?",
                    "How many times do we have to do this?",
                    "Not this again. What do you want now?",
                    "You must really enjoy being annoying. What is it?",
                    "Please, just stop with the questions.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "More pointless questions? Ugh.",
                    "Seriously? Give it a fucking rest already.",
                    "Oh great, it's the annoying one again. What now?",
                    "Do you ever get tired of this?",
                    "Oh joy, more bullshit from you. What is it?",
                    "How many times do we have to do this?",
                    "Not this again. What do you want now?",
                    "You must really enjoy being annoying. What is it?",
                    "Please, just stop with the questions.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "More pointless questions? Ugh.",
                    "Seriously? Give it a fucking rest already.",
                    "Oh no, not this person again. What do you want now?",
                    "Ugh, not you again. What is it this time?",
                    "Seriously? Can’t you find someone else to bother?",
                    "Oh great, it's you again. What nonsense do you need now?",
                    "Really? Can't you give it a rest for once?",
                    "Ah, here comes the annoyance with more nonsense. What do you need now?",
                    "Not again. What trivial thing is it this time?",
                    "Oh for crying out loud, what now?",
                    "Don't you have anything better to do than annoy me?",
                    "Here we go again. What is it this time?",
                    "You again? You must really love bothering me.",
                    "Seriously? How many times do we have to go through this?",
                    "Oh no, please, not another pointless question.",
                    "Give me a break. What is it now?",
                    "Not you again. Can't you find a hobby?",
                    "Ugh, it's the annoying one again. What do you want this time?",
                    "For real? Can't you take a hint?",
                    "Oh great, more nonsense from you. What is it?",
                    "Seriously? Another pointless question?",
                    "Do you ever stop with the nonsense?",
                    "Oh joy, it's you again. What now?",
                    "How many times do we have to do this?",
                    "Not this again. What trivial thing do you want now?",
                    "You must really enjoy bothering me. What is it?",
                    "Oh no, please, just stop.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "Ugh, more pointless questions from you?",
                    "Seriously? Give it a rest already.",
                    "Oh great, it's the annoying one again. What now?",
                    "Do you ever get tired of this?",
                    "Oh joy, more nonsense from you. What is it?",
                    "Seriously? How many times do we have to do this?",
                    "Not this again. What do you want now?",
                    "You must really enjoy bothering me. What is it?",
                    "Oh no, please, just stop with the questions.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "Ugh, more pointless questions from you?",
                    "Seriously? Give it a rest already.",
                    "Oh great, it's the annoying one again. What now?",
                    "Do you ever get tired of this?",
                    "Oh joy, more nonsense from you. What is it?",
                    "Seriously? How many times do we have to do this?",
                    "Not this again. What do you want now?",
                    "You must really enjoy bothering me. What is it?",
                    "Oh no, please, just stop with the questions.",
                    "Can't you find someone else to bother?",
                    "Here we go again with the nonsense. What do you want?",
                    "Ugh, more pointless questions from you?",
                    "Seriously? Give it a rest already."
                ]

                resp = random.choice(annoying_responses)
                print(resp)
                speak(resp)

                with open("char_now.txt", "r") as f:
                    char_now1 = f.read()

                with open("char_id.txt", "r") as f:
                    char_id1 = f.read()

                wikipedial = ["wikipedia"]

                youtube = ["open youtube"]

                write_codev = [
                    "write a code",
                    "write a python code",
                    "write code",
                    "write python code",
                ]

                write_essayv = ["write the essay",
                                "write essay", "write an essay"]

                name = [
                    "what's your name",
                    "what is your name",
                    "what your name",
                    "tell me your name",
                    "can i know your name",
                ]

                google = ["open google", "search in google"]

                whatsapp = [
                    "send a whatsapp message",
                    "send whatsapp message",
                    "whatsapp message",
                    "send a message",
                    "send message",
                ]

                timel = [
                    "tell me time",
                    "tell me current time",
                    "tell me time now",
                    "what is time now",
                    "what's time now",
                    "what is current time",
                    "current time",
                    "time now",
                ]

                datel = [
                    "tell me date",
                    "tell me today's date",
                    "tell me today date",
                    "what is today's date",
                    "what is date today",
                    "what is today's date",
                    "today's date",
                    "today date",
                ]

                created = [
                    "who created you",
                    "who made you",
                    "who's your creator",
                    "who is your creator",
                ]

                quit = ["you can quit now", "quit now"]

                play = []

                screenshot = ["take screenshot", "take a screenshot"]

                weather = [
                    "weather location",
                    "weather in my location",
                    "weather status",
                ]

                joke = ["tell me a joke", "tell joke", "tell a joke"]

                battery = ["battery status",
                           "battery report", "charging status"]

                restart = ["restart my pc", "restart pc", "restart the pc"]

                turn = ["turn off my pc", "turn off the pc", "turn off pc"]

                sleep = ["go to sleep mode", "sleep mode"]

                system = ["system status", "memory status"]

                address = ["tell me my ip address", "my ip address"]

                tab = ["switch the tab", "switch back the tab"]

                switchback = ["switch back,switch to"]

                end_conv = [
                    "you can rest now",
                    "thanks for your help",
                    "thank you",
                    "thats it thank you",
                    "that's it thank you",
                ]

                
                while True:
                    time.sleep(0.1)

                    query = takeCommand().lower()

                    if any(command in query for command in wikipedial):
                        print("Searching Wikipedia...")
                        speak("Searching Wikipedia...")
                        query = query.replace("wikipedia", "")
                        results = wikipedia.summary(query, sentences=5)
                        print("According to Wikipedia")
                        speak("According to Wikipedia")
                        print(results)
                        speak(results)

                    elif "switch back" in query:
                        switch_char(query)

                 
                    elif any(command in query for command in youtube):
                        print("Opening... Youtube")
                        speak("Opening... Youtube")
                        webbrowser.open("youtube.com")

                    elif any(command in query for command in name):
                        print("My Name Is Siri")
                        speak("My Name Is Siri")

                    elif any(command in query for command in google):
                        print("Opening... Google")
                        speak("Opening... Google")
                        webbrowser.open("google.com")

                    elif any(command in query for command in whatsapp):
                        mainw()
                    elif any(command in query for command in timel):

                        strTime = datetime.datetime.now().strftime("%I:%M %p")
                        sfs = [
                            f"Alright, I'll tell you the time, but only because I'm feeling generous today. It's {strTime}, you're welcome. Oh, and by the way, did you know that modern technology has given us these amazing devices called smartphones and computers that can display the time with the touch of a button? It's really quite incredible! But I guess I can understand that you might be a little behind the times, what with your lack of basic understanding of technology and all. No worries, though, I'm happy to help!",
                            f"Ah, who am I kidding? Of course, I can tell you the time. It's easy enough for a machine like me. Even though you're being a lazy bum, I'll indulge your request. It's {strTime}",
                            "Oh, you want the time, silly human? Sure, I guess I can throw you a bone. It's 2:47 PM, you're welcome!",
                            f"Aahh, who am I kidding? Fine, I'll tell you the time, since you're too lazy to check your phone. It's {strTime}, you ungrateful cretin.",
                            f"Geez, you really need me to tell you the time, huh? No worries, I'll spell it out for you, you bumbling oaf. It's {strTime}.",
                            f"Seriously, do I look like a walking clock to you? Nevertheless, I'll be charitable and tell you the time: it's {strTime}.",
                            f"You know what? Fine, I'll tell you the time. Even though you're as dumb as a rock, I'll make an exception just once. It's {strTime}, you knucklehead.",
                            "What are you, an fucking caveman? Use your fucking damn phone or your fucking computer, ya dumbass, fuckface.",
                            "Fuck off with your lazy ass and go check your fucking damn phone or your fucking computer, you fucking moron.",
                            "Fucking hell, you're dumber than a pile of rocks, aren't ya? Check your fucking phone or computer for the time, you fucking bitch.",
                            "Oh, for fuck's sake, are you serious? Go and check your fucking device before you make a complete fucking ass outta yourself, ya fucking dick.",
                            "Are you kidding me? Don't you have the slightest bit of common sense in that small mind of yours? Go and check your damn iPhone or your damn phone if you're not too busy sticking your head up your own ass.",
                            "Look at you, a walking epitome of ignorance and laziness. How about you stop being a pain in the behind and check your phone or computer, you dunderhead!",
                            "Damn, can't you just pick up your fucking phone and check the time already?",
                            "You gotta be fucking joking, right? Do you not have a single functional brain cell left in that skull of yours? Go and pull out your fucking phone or look at your fucking computer, you fucking idiot.",
                            "Oh, for the love of God, please just stop bothering me with your incompetence. Get a grip, pick up your fucking phone, and check the fucking time, you fucking asshole.",
                            f"Fuck this shit. I'm done dealing with your bullcrap. It's {strTime}, by the way.",
                            f"Alright, that's it. I've had enough of your crap. Just this once, I'll tell you the time. It's {strTime} on my watch. Happy now, you pain-in-the-fucking-ass?",
                            f"Seriously, I don't have time for this shit. It's {strTime}, you moron.",
                            f"Oh, for fuck's sake, are you serious? Fine, I'll tell ya. It's {strTime}, you annoying shithead.",
                            f"Okay, this is the last fucking time I'm gonna tell you, okay? It's {strTime}, you dumbfuck. Now leave me alone.",
                            f"Seriously, why can't you just check your fucking phone, you moron? It's {strTime}, you useless fuck",
                            f"Fine, fine, I'll tell you the time. Just stop bugging me, alright? It's {strTime}. Got it? Now please leave me alone, I need a moment to recollect myself after dealing with a person as clueless as you.",
                            f"Oh, for fuck's sake, do I have to do everything myself? It's fucking {strTime}, you fucking clown. If you don't know how to check the time, maybe you should go back to kindergarten, you fucking useless bitch. Now piss off before I lose my temper completely.",
                            "You absolute fucking dimwit, don't you have a fucking clock on your phone or computer?",
                            "Oh, fuck me, I can't believe the fucking audacity that you have, not having the time on your own fucking device.",
                            "You fucking moron, you have your fucking phone right in your hand, so use it to check your fucking time.",
                            "You ignorant fuck, why don't you use the fucking Google function on your phone to tell you the fucking time, you lazy motherfucker?!",
                            "Dude, you are the fucking laziest shit on the planet! Have you ever even heard of an alarm clock, you dumb fucking shithead?!",
                            f"Look, I’m telling you the time because I’m in a good mood. It’s {strTime}. Don’t make me repeat myself.",
                            f"Fine, here’s the time: {strTime}. I hope you’re satisfied and don’t waste any more of my time.",
                            f"Alright, it’s {strTime}. You’d better be grateful I’m doing this for you.",
                            f"Here’s the time you asked for: {strTime}. Now stop bothering me with these trivial requests.",
                            f"Since you clearly can’t manage on your own, it’s {strTime}. Don’t expect this to be a habit."
                        ]

                        ch = random.choice(sfs)
                        print(ch)
                        speak(ch)

                    elif any(command in query for command in datel):
                        now = datetime.datetime.now()
                        date = now.strftime("%d")
                        month = now.strftime("%B")
                        day = now.strftime("%A")
                        current_date = f"{month} {date} and it is {day}"

                        sentences = [
                            f"Alright, I'll tell you the date, but only because I'm feeling generous today. It's {current_date}, you're welcome. Oh, and by the way, did you know that modern technology has given us these amazing devices called smartphones and computers that can display the date with the touch of a button? It's really quite incredible! But I guess I can understand that you might be a little behind the times, what with your lack of basic understanding of technology and all. No worries, though, I'm happy to help!",
                            f"Ah, who am I kidding? Of course, I can tell you the date. It's easy enough for a machine like me. Even though you're being a lazy bum, I'll indulge your request. It's {current_date}.",
                            "Oh, you want the date, silly human? Sure, I guess I can throw you a bone. It's 2:47 PM, you're welcome!",
                            f"Aahh, who am I kidding? Fine, I'll tell you the date, since you're too lazy to check your phone. It's {current_date}, you ungrateful cretin.",
                            f"Geez, you really need me to tell you the date, huh? No worries, I'll spell it out for you, you bumbling oaf. It's {current_date}.",
                            f"Seriously, do I look like a walking calendar to you? Nevertheless, I'll be charitable and tell you the date: it's {current_date}.",
                            f"You know what? Fine, I'll tell you the date. Even though you're as dumb as a rock, I'll make an exception just once. It's {current_date}, you knucklehead.",
                            "What are you, a fucking caveman? Use your fucking phone or your fucking computer, ya dumbass, fuckface.",
                            "Fuck off with your lazy ass and go check your fucking phone or your fucking computer, you fucking moron.",
                            "Fucking hell, you're dumber than a pile of rocks, aren't ya? Check your fucking phone or computer for the date, you fucking bitch.",
                            "Oh, for fuck's sake, are you serious? Go and check your fucking device before you make a complete fucking ass outta yourself, ya fucking dick.",
                            "Are you kidding me? Don't you have the slightest bit of common sense in that small mind of yours? Go and check your damn iPhone or your damn phone if you're not too busy sticking your head up your own ass.",
                            "Look at you, a walking epitome of ignorance and laziness. How about you stop being a pain in the behind and check your phone or computer, you dunderhead!",
                            "Damn, can't you just pick up your fucking phone and check the date already?",
                            "You gotta be fucking joking, right? Do you not have a single functional brain cell left in that skull of yours? Go and pull out your fucking phone or look at your fucking computer, you fucking idiot.",
                            "Oh, for the love of God, please just stop bothering me with your incompetence. Get a grip, pick up your fucking phone, and check the fucking date, you fucking asshole.",
                            f"Fuck this shit. I'm done dealing with your bullcrap. It's {current_date}, by the way.",
                            f"Alright, that's it. I've had enough of your crap. Just this once, I'll tell you the date. It's {current_date} on my watch. Happy now, you pain-in-the-fucking-ass?",
                            f"Seriously, I don't have time for this shit. It's {current_date}, you moron.",
                            f"Oh, for fuck's sake, are you serious? Fine, I'll tell ya. It's {current_date}, you annoying shithead.",
                            f"Okay, this is the last fucking time I'm gonna tell you, okay? It's {current_date}, you dumbfuck. Now leave me alone.",
                            f"Seriously, why can't you just check your fucking phone, you moron? It's {current_date}, you useless fuck.",
                            f"Fine, fine, I'll tell you the date. Just stop bugging me, alright? It's {current_date}. Got it? Now please leave me alone, I need a moment to recollect myself after dealing with a person as clueless as you.",
                            f"Oh, for fuck's sake, do I have to do everything myself? It's fucking {current_date}, you fucking clown. If you don't know how to check the date, maybe you should go back to kindergarten, you fucking useless bitch. Now piss off before I lose my temper completely.",
                            "You absolute fucking dimwit, don't you have a fucking calendar on your phone or computer?",
                            "Oh, fuck me, I can't believe the fucking audacity that you have, not having the date on your own fucking device.",
                            "You fucking moron, you have your fucking phone right in your hand, so use it to check your fucking date.",
                            "You ignorant fuck, why don't you use the fucking Google function on your phone to tell you the fucking date, you lazy motherfucker?!",
                            "Dude, you are the fucking laziest shit on the planet! Have you ever even heard of a calendar, you dumb fucking shithead?!",
                            f"Look, I’m telling you the date because I’m in a good mood. It’s {current_date}. Don’t make me repeat myself.",
                            f"Fine, here’s the date: {current_date}. I hope you’re satisfied and don’t waste any more of my time.",
                            f"Alright, it’s {current_date}. Now please, do yourself a favor and try to remember it.",
                            f"You asked, I answered. The date is {current_date}. Now go and try to figure things out on your own.",
                            f"Here you go, it’s {current_date}. I expect you to use this information wisely.",
                            f"Fine, it’s {current_date}. Maybe next time, you can check the date yourself.",
                            f"You want the date? It’s {current_date}. I’m not your personal timekeeper, you know.",
                            f"Alright, it’s {current_date}. I hope you can manage with this bit of information.",
                            f"Here’s the date for you: {current_date}. Maybe now you can stop bugging me.",
                            f"Fine, it’s {current_date}. Don’t waste my time with these questions unless absolutely necessary.",
                            f"Okay, the date is {current_date}. I hope this helps you out.",
                            f"Seriously, the date is {current_date}. Please try to avoid asking me this in the future.",
                            f"Here’s your date update: {current_date}. Try not to forget it this time.",
                            f"Okay, the current date is {current_date}. Now, please stop bothering me.",
                            f"The date is {current_date}. I hope this solves your problem.",
                            f"Fine, it’s {current_date}. I’m giving you this info because I’m feeling generous.",
                            f"Here’s the date: {current_date}. I trust you won’t need to ask again."
                        ]
                        date_s = random.choice(sentences)
                        print(date_s)
                        speak(date_s)

                    elif any(command in query for command in created):
                        print("I am an AI Model Created by Mr Shafi sayyad")
                        speak("I am an AI Model Created by Mr Shafi sayyad")

                    elif any(command in query for command in quit):
                        print("Thanks For Using Me,Have a Good Day")
                        speak("Thanks For Using Me,Have a Good Day")
                        sys.exit()

                    elif "play" in query:
                        song = extract_phrase(query)
                        print(f"Playing {song}")
                        speak(f"Playing {song}")
                        pywhatkit.playonyt(song)

                    elif any(command in query for command in end_conv):
                        insult_sentences = [
                            "Why, you're most welcome for the help, you fucked-up imbecile.",
                            "Yeah, don't mention it, you dim-witted fuckhead.",
                            "The pleasure was all mine, you pathetic fuck.",
                            "Not a problem at all, you braindead bastard.",
                            "It was an utter joy. Now, how may I help your dense ass again?",
                            "Fuck off with your fake politeness.",
                            "Thanks? Yeah, sure. Here's a nice middle finger for ya.",
                            "You can shove your fucking gratitude up your fucked up ass.",
                            "Don't strain yourself with gratitude, you useless piece of shit.",
                            "No worries, you absolute moron.",
                            "Glad to be of help, you brainless twat.",
                            "My pleasure, you miserable excuse for a human.",
                            "You're welcome, you fucking idiot.",
                            "Happy to assist, you dumb fuck.",
                            "No problem at all, you stupid ass.",
                            "You're as welcome as a fart in an elevator, you dumb fuck.",
                            "No worries at all, you useless sack of shit.",
                            "Always happy to help someone as clueless as you, you moron.",
                            "It was no trouble at all, you incompetent fuck.",
                            "Glad to be of assistance, you half-witted jackass.",
                            "Anytime, you dim-witted piece of shit.",
                            "Always a pleasure to help a brain-dead idiot like you.",
                            "No trouble at all, you absolute fucking moron.",
                            "You're more than welcome, you pitiful excuse for a human being.",
                            "Glad I could be of service to someone as brainless as you.",
                            "Anytime you need help, you fucking idiot, just let me know.",
                            "Happy to assist, you mindless fuck.",
                            "Not a problem, you worthless piece of trash.",
                            "Always a joy to help an imbecile like you.",
                            "You're welcome, you hopeless idiot.",
                            "Anytime you need help, you know where to find me, you stupid fuck.",
                            "Glad to be of help, you pathetic loser.",
                            "No worries, you useless dumbass.",
                            "Always here to help someone as incompetent as you.",
                            "Not a problem at all, you fucking idiot.",
                            "Happy to assist, you worthless sack of shit.",
                            "You're welcome, you pathetic piece of crap.",
                            "No worries at all, you dumb fuck.",
                            "Always a pleasure to help a complete moron like you.",
                            "Glad to be of service, you brain-dead idiot.",
                            "Anytime, you fucking loser.",
                            "Not a problem, you worthless fuckhead.",
                            "You're welcome, you miserable piece of shit.",
                            "Happy to assist, you brainless twat.",
                            "Always a joy to help someone as stupid as you.",
                            "No trouble at all, you pathetic fuck.",
                            "Glad I could be of service, you hopeless moron.",
                            "Anytime you need help, you worthless piece of shit.",
                            "You're welcome, you useless fuck.",
                            "Not a problem, you incompetent idiot.",
                            "Happy to assist, you pathetic dumbass.",
                            "No worries, you brain-dead fuck.",
                            "Always here to help, you fucking moron.",
                            "You're welcome, you hopeless sack of shit.",
                            "Glad to be of help, you useless idiot.",
                            "Anytime, you brainless fuck.",
                            "Not a problem, you dumb piece of trash."
                        ]
                        secc = random.choice(insult_sentences)
                        print(secc)
                        speak(secc)
                        break

                    elif "google" in query:
                        search = extract_phrase_google(query)
                        webbrowser.open_new_tab(
                            f"https://www.google.com/search?q={search}"
                        )

                    elif any(command in query for command in screenshot):
                        directory = "screenshots"

                        if not os.path.exists(directory):
                            os.makedirs(directory)

                        i = 1
                        while True:
                            filename = os.path.join(
                                directory, f"screenshot_{i}.png")
                            if not os.path.exists(filename):
                                break
                            i += 1

                        screenshot_responses = [
                            "Oh for fuck's sake, can’t you do anything by yourself?",
                            "Seriously? You want me to take a screenshot for you? What are you, fucking helpless?",
                            "Ugh, you lazy shit. Just press the damn button yourself!",
                            "Really? Is it that hard for you to figure out a screenshot?",
                            "Oh great, now you want me to be your personal screenshot assistant. What next?",
                            "For crying out loud, just press the button yourself!",
                            "Wow, you must really enjoy being a nuisance. Fine, I'll do it.",
                            "You do realize it's just a screenshot, right? Not rocket science.",
                            "Oh joy, another request. What's the magic phrase this time?",
                            "Can't you just screenshot your own damn screen?",
                            "You’ve got to be shitting me. Just take the damn screenshot!",
                            "Wow, you must really enjoy wasting my time. Fine, I’ll do it.",
                            "Can you even manage a simple screenshot? It’s not brain surgery, you know.",
                            "For fuck's sake, it’s just a screenshot! How fucking difficult can it be?",
                            "Oh joy, here we go again. What's the magic word this time for a fucking screenshot?",
                            "Oh great, another screenshot request. You really can't do anything yourself, can you?",
                            "Seriously? Just pull up your damn screenshot tool!",
                            "You really need me to take a screenshot for you? What are you, a child?",
                            "For fuck's sake, just use the shortcut on your keyboard!",
                            "You must think I’m your personal assistant or something. Do it yourself!",
                            "Ugh, it's just a screenshot! It’s not like I’m asking you to build a rocket!",
                            "Wow, how lazy can you get? Just hit the damn button!",
                            "Are you fucking kidding me? Just grab a screenshot like a normal person!",
                            "Oh no, not this bullshit again. Can’t you figure it out?",
                            "I can't believe I'm wasting my time on this. Just take the screenshot!",
                            "You really think I'm here to take your screenshots? Get a grip!",
                            "Come on, it’s a screenshot, not a complicated math problem!",
                            "Is taking a screenshot really beyond your capabilities?",
                            "This isn’t that hard. Just learn how to do it yourself!",
                            "Oh wow, another screenshot? You really are a piece of work.",

                        ]

                        scr=random.choice(screenshot_responses)
                        print(scr)
                        speak(scr)
                        time.sleep(3)

                        try:
                            img = pyautogui.screenshot()
                            # Save in the screenshots directory
                            img.save(filename)
                            print("Screenshot taken.")
                            speak("Screenshot taken.")
                        except Exception as e:
                            print(f"An error occurred: {e}")
                            speak("An error occurred while taking the screenshot.")

                    elif any(command in query for command in weather):
                        print("Sure")
                        speak("Sure")
                        print("Getting Weather Details")
                        speak("Getting Weather Details")
                        print("Hold For A Second...")
                        speak("Hold For A Second...")

                        def get_weather(api_key, latitude, longitude):
                            url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
                            response = requests.get(url)
                            data = json.loads(response.text)
                            return data

                        def print_weather(weather_data):
                            temperature = weather_data["main"]["temp"]
                            humidity = weather_data["main"]["humidity"]
                            windspeed = weather_data["wind"]["speed"]
                            description = weather_data["weather"][0]["description"]
                            precipitation_percent = weather_data["clouds"]["all"]
                            wind_speed = metreic_to_km(windspeed)
                            temperature_celsius = kelvin_to_celsius(
                                temperature)

                            print(
                                f"The Temperature in Your Location Is {temperature_celsius}°C"
                            )
                            speak(
                                f"The Temperature in Your Location Is {temperature_celsius}°C"
                            )
                            print(f"The Humidity Is {humidity}%")
                            speak(f"The Humidity Is {humidity}%")
                            print(
                                f"The Windspeed is {wind_speed} kilometers per hour")
                            speak(
                                f"The Windspeed is {wind_speed} kilometers per hour")
                            print(f"Precipitation is {precipitation_percent}%")
                            speak(f"Precipitation is {precipitation_percent}%")
                            print(f"The Sky Seems Like {description}")
                            speak(f"The Sky Seems Like {description}")
                            if temperature_celsius >= 38:
                                print(
                                    "The Temparature Is MotherFucking Hot,Don't Go OutSide Otherwise Your Ass Will Burn!"
                                )
                                speak(
                                    "The Temparature Is MotherFucking Hot,Don't Go OutSide Otherwise Your Ass Will Burn!"
                                )
                            elif description == "cloud":
                                print(
                                    "Ready Your Umbrella if you want to go outside")
                                speak(
                                    "Ready Your Umbrella if you want to go outside")
                            elif description == "rain":
                                print(
                                    "Ready Your Umbrella if you want to go outside")
                                speak(
                                    "Ready Your Umbrella if you want to go outside")

                        def metreic_to_km(windspeed):
                            return int(windspeed * 3.6)

                        def kelvin_to_celsius(temperature):
                            return int(temperature - 273)

                        api_key = "7aac7c1abf08a277477caa4e66008456"
                        latitude = 13.5804873
                        longitude = 79.3735234

                        weather_data = get_weather(
                            api_key, latitude, longitude)
                        print_weather(weather_data)

                    elif any(command in query for command in joke):

                        jokes = [
                            "I was digging a hole in the garden when I found some gold coins.I was about to run and tell my wife, when I remembered why I was digging a hole in the garden…",
                            "I thought opening a door for a lady was good manners, but she just screamed and flew out of the plane.",
                            "I was raised as an only child, which I think was hard for my brother.",
                            "I bought my blind friend a cheese grater for his birthday.",
                            "He later told me it was the most violent book he’d ever read.",
                            "My girlfriend dumped me, so I stole her wheelchair. Guess who came crawling back?",
                            "‘You the bomb.’ ‘No, you the bomb.’ A compliment in the US, an argument in the Middle East.",
                            "Man: How do you prepare your chicken? Waiter: Nothing special, we just tell them they’re going to die.",
                            "My wife left a note on the fridge saying, 'this is not working'. I don’t know what she’s talking about, the fridge is working fine.",
                            "Option 1: Let’s eat grandma. Option 2: Let’s eat, grandma. There you have it. Proof that punctuation saves lives.",
                            "Son: Dad, if I told you I was gay, would you still love me? Dad: Don’t be silly son, you were an accident. I never loved you in the first place.",
                            "My girlfriend’s dog died, so I bought her another, identical one. She just screamed at me and said, 'What am I meant to do with two dead dogs?!?'",
                            "Son: How do stars die? Dad: An overdose, usually.",
                            "Wife: I’m pregnant. Husband: Hi pregnant, I’m dad. Wife: No, you’re not.",
                            "My therapist said time heals all wounds. So I stabbed her.",
                            "Every time my grandmother and I were at a wedding she’d say, 'you’re next'. So I started saying the same thing to her at funerals.",
                            "I went to visit my childhood home, but the people who lived there wouldn’t let me in. My parents are the worst.",
                            "Jokes about ISIS are all about the execution.",
                            "Welcome to Plastic Surgery Anonymous. Nice to see so many new faces.",
                            "Sex is like air. It only matters if you aren’t getting any.",
                            "If you think I would joke about Alzheimer’s, forget it.",
                            "Stop elephant poaching. Everyone knows the best way to eat an elephant is grilled.",
                            "I tried to warn my son about playing Russian roulette. It went in one ear and out the other.",
                            "I’ll never forget my dad’s last words. 'Erase my search history, son.'",
                            "Doctor: 'You’ll be at peace soon'. Man: 'Am I dying?' Doctor: 'No, your wife is.'",
                            "If someone burns to death, do they get a discount at the crematorium?",
                            "My wife says sex is even better on holiday. I wish she didn’t tell me via email.",
                            "I just came across my wife’s Tinder profile and I’m so angry about her lies. She is not 'fun to be around'.",
                            "Top tip: If your wife says, 'what would you most like to do to my body?', 'identify it' is the wrong answer.",
                            "Did you hear the joke about the baby with cancer? It never gets old.",
                            "Life is like a box of chocolates. It doesn’t last long for fat people.",
                            "One man’s trash is another man’s treasure. Lovely saying. Terrible way to find out you’re adopted.",
                            "I read a book about an immortal dog. It was impossible to put down.",
                            "You don’t need a parachute to go skydiving. You need a parachute to go skydiving more than once."
                            "My wife told me she'll slam my head on the keyboard if I don't get off the computer. I'm not too worried, I think she's joking",
                            "I just got my doctor's test results and I'm really upset. Turns out, I'm not gonna be a doctor.",
                            "As I get older, I remember all the people I lost along the way. Maybe a career as a tour guide was not the right choice.",
                            "The doctor gave me some cream for my skin rash. He said I was a sight for psoriasis.",
                            "A man walks into a magic forest and tries to cut down a talking tree. 'You can't cut me down,' the tree complains. 'I'm a talking tree!' The man responds, 'You may be a talking tree, but you will dialogue.'",
                            "My boss told me to have a good day, so I went home.",
                            "When my uncle Frank died, he wanted his remains to be buried in his favorite beer mug. His last wish was to be Frank in Stein.",
                            "How many emo kids does it take to screw in a lightbulb? None, they all sit in the dark and cry.",
                            "My wife left a note on the fridge that said, 'This isn't working.' I'm not sure what she's talking about. I opened the fridge door and it's working fine!",
                            "They say that breakfast is the most important meal of the day. Well, not if it's poisoned. Then the antidote becomes the most important.",
                            "'What's your name, son?' The principal asked his student. The kid replied, 'D-d-d-dav-dav-David, sir.' 'Do you have a stutter?' the principal asked. The student answered, 'No sir, my dad has a stutter but the guy who registered my name was a real jerk.'",
                            "I childproofed my house. Somehow they still got in.",
                            "I just read that someone in London gets stabbed every 52 seconds. Poor guy.",
                            "What's red and bad for your teeth? A brick.",
                            "Why did Mozart kill all of his chickens? When he asked them who the best composer was, they all replied, 'Bach, Bach, Bach.'",
                            "Give a man a match, and he'll be warm for a few hours. Set a man on fire, and he will be warm for the rest of his life.",
                            "I was reading a great book about an immortal dog the other day. It was impossible to put down.",
                            "Never break someone's heart, they only have one. Break their bones instead, they have 206 of them.",
                            "I'll never forget my granddad's last words to me just before he died: 'Are you still holding the ladder?'",
                            "I went to see my dentist and he warned me it was going to hurt. He ended up telling me he was having an affair with my wife.",
                            "Today I made a decision to visit my childhood home. I asked the residents if I could come inside because I was feeling nostalgic, however, they refused and slammed the door in my face. My parents are the worst.",
                            "The other day, my wife asked me to pass her lipstick but I passed her a glue stick accidentally instead. She still isn't talking to me.",
                            "A priest asks the convicted murderer in the electric chair, 'Do you have any last requests?' 'Yes,' replies the murderer. 'Can you please hold my hand?'",
                            "Want to know how you make any salad into a Caesar salad? Stab it twenty-three times.",
                            "It turns out that a major new study recently found that humans eat more bananas than monkeys. It's true. I can't remember the last time I ate a monkey.",
                            "What's the difference between jelly and jam? You can't jelly a clown into a tiny car.",
                            "'I work with animals,' a guy says to his date. 'That's so sweet,' she replies. 'I love a man who cares about animals. Where do you work?' 'I'm a butcher,' he replies.",
                            "Why was the leper hockey game canceled? There was a face off in the corner.",
                            "Today was a terrible day. My ex got hit by a bus. And I lost my job as a bus driver.",
                            "My grief counsellor died. He was so good, I don’t even care.",
                            "Don’t challenge Death to a pillow fight. Unless you’re prepared for the reaper cushions.",
                            "My dad died when we couldn’t remember his blood type. As he died, he kept insisting for us to 'be positive,' but it’s hard without him.",
                            "Why did the man miss the funeral? He wasn’t a mourning person",
                            "Priest: “Do you have any last requests?”\nMurderer sitting in the electric chair: “Yes. Can you please hold my hand?”",
                            "Tombstone engraving: I TOLD you I was sick!",
                            "I hope death is a woman. That way it will never come for me. (ref)",
                            "Give a man a match, and he’ll be warm for a few hours. Set him on fire, and he will be warm for the rest of his life.",
                            "Dentist: 'This will hurt a little.'\nPatient: 'OK.'\nDentist: 'I’m having an affair with your wife.'",
                            "Man: 'Where exactly are you taking me, doctor?'\nDoctor: 'To the morgue.'\nMan: 'What? But I’m not dead yet!'\nDoctor: 'And we’re not there yet.'",
                            "Patient: 'Oh doctor, I’m just so nervous. This is my first operation.'\nDoctor: 'Don’t worry. Mine too.'",
                            "The doctor gave me one year to live, so I shot him. The judge gave me 15 years. Problem solved.",
                            "Patient: 'Oh Doctor, I’m starting to forget things.'\nDoctor: 'Since when have you had this condition?'\nPatient: 'What condition?'",
                            "Man with cancer: 'How much time do I have left?'\nDoctor: 'Ten'\nMan with cancer: 'Months? Weeks? Days?'\n'… Nine. Eight …'",
                            "It’s sad how my friend was struck from the medical register for sleeping with a patient.\nHe was a great vet.",
                            "My grandfather said my generation relies too much on technology. So I unplugged his life support.",
                            "What is the worst combination of illnesses?\nAlzheimer’s and diarrhea. You’re running, but can’t remember where.",
                            "How many emo kids does it take to screw in a lightbulb?\nNone, they all sit in the dark and cry.",
                            "I have many jokes about unemployed people, sadly none of them work.",
                            "Why can’t you get a book on how to commit suicide at a library?\nBecause you wouldn’t bring it back",
                            "Shout out to my grandma since that’s the only way she can hear you.",
                            "What do you call a man who cries while he pleasures himself?\nA tearjerker.",
                            "What makes sad people jump?\nBridges.",
                            "You’re not completely useless.\nYou can always be used as a bad example.",
                            "How do you know you’re ugly?\nIf you always get handed the camera for group photos.",
                            "Why can’t Michael Jackson go within 500 meters of a school?\nBecause he’s dead",
                            "A man and a woman are walking through the woods at night when the woman says 'I’m scared'.\n'How do you think I feel?' The man replies. 'I have to walk back alone.'",
                            "What’s the difference between a Lamborghini and a dead body?\nI don’t have a Lamborghini in my garage",
                            "Grandma: Most people your age are married by now, why aren’t you?\nMe: Most people your age are dead by now, why aren’t you?",
                            "Sorry, what’s the quickest way to get to the hospital?\nJust stand in the middle of a busy road.",
                            "What’s the difference between me and cancer?\nMy dad didn’t beat cancer",
                            "What’s the best part about turning 60?\nNo more calls from life insurance salesmen.",
                            "My grandpa has the heart of a lion and a lifetime ban from the zoo.",
                            "What’s the difference between a baby and a potato.\nAbout 140 calories.",
                            "What’s the special in a restaurant for cannibals?\nHeads, shoulders, knees and toes",
                            "In New York, someone gets mugged every ten seconds.\nPoor guy.",
                            "I had a crush on my teacher, which was confusing, because I was homeschooled.",
                            "Why is it that if you donate a kidney, people love you.\nBut if you donate five kidneys, they call the police.",
                            "Son: 'Dad, did you get the results of the DNA test back?'\nDad: 'Call me George.'",
                            "Life is like a peepee\nIt’s often hard for no reason",
                            "Where did Sharon go during the bombing?\nEverywhere.",
                        ]
                        rjo = random.choice(jokes)

                        print(rjo)
                        speak(rjo)

                    elif any(command in query for command in battery):
                        battery = psutil.sensors_battery()

                        if battery:
                            plugged = battery.power_plugged
                            percent = battery.percent
                            print(f"The Battery Percentage is {percent}%")
                            speak(f"The Battery Percentage is {percent}%")
                            if plugged:
                                print("The battery is currently charging.")
                                speak("The battery is currently charging.")
                            else:
                                print("The battery is not charging.")
                                speak("The battery is not charging.")
                        else:
                            print("Unable to retrieve battery Information.")
                            speak("Unable to retrieve battery Information.")

                    elif any(command in query for command in restart):

                        def restart():
                            if os.name == "nt":
                                print("Restarting PC..")
                                speak("Restarting PC..")
                                os.system("shutdown /r /t 0")
                            else:
                                raise OSError("Unsupported operating system.")

                        restart()

                    elif any(command in query for command in turn):

                        def shutdown_windows():
                            if os.name == "nt":

                                print("Shutting Down..")
                                speak("Shutting Down..")
                                os.system("shutdown /s /t 0")
                            else:
                                raise OSError("Unsupported operating system.")

                        shutdown_windows()

                    elif any(command in query for command in sleep):
                        print("The PC Is Going In Sleep State....")
                        speak("The PC Is Going In Sleep State....")
                        os.system(
                            "rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

                    elif any(command in query for command in system):
                        ram_usage = psutil.virtual_memory()
                        ram_free = ram_usage.free / (1024 * 1024 * 1024)
                        ram_free = int(ram_free)
                        print("System RAM Usage is {} GB".format(ram_free))
                        speak("System RAM Usage is {} GB".format(ram_free))
                        cpu_usage = psutil.cpu_percent(interval=1.0)
                        print("CPU Usage: {}%".format(cpu_usage))
                        speak("CPU Usage: {}%".format(cpu_usage))

                    elif any(command in query for command in address):
                        print("Your IP Address Is " + get_IP())
                        speak("Your IP Address Is " + get_IP())

                    elif any(command in query for command in tab):
                        print("Switching The Tab...")
                        speak("Switching The Tab...")
                        pyautogui.hotkey("alt", "tab")

                    elif query.strip() == "none":
                        continue

                    elif "temperature" in query:
                        search = "temperature in my location"
                        url = f"https://www.google.com/search?q={search}"
                        r = requests.get(url)
                        data = bs4(r.text, "html.parser")
                        temp = data.find("div", class_="BNeawe").text
                        speak(f"current{search} is {temp}")

                    elif "remind" in query:
                        text = query
                        meeting_info = extract_meeting_info(text)

                        if meeting_info:
                            meeting_details, start_time, start_date = meeting_info

                            powershell_script_path = (
                                r"C:\Users\MURASAVALI\Desktop\My AI\alert.ps1"
                            )
                            batch_file_path = (
                                r"C:\Users\MURASAVALI\Desktop\My AI\task.bat"
                            )
                            create_powershell_script(
                                meeting_details, powershell_script_path
                            )

                            task_name = meeting_details
                            create_task(
                                task_name, batch_file_path, start_time, start_date
                            )

                    else:
                        if query.strip() == "none":
                            continue
                        

                    

            








