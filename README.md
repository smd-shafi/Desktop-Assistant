# Desktop Assistant

This is a Python-based desktop assistant that helps automate various tasks using voice commands. It leverages multiple libraries to provide functionalities like web searches, system operations, and more.

## Features

- **Voice Recognition**: Understands and processes voice commands.
- **Text-to-Speech**: Converts text responses to spoken words.
- **Web Search**: Searches Wikipedia and the web for information.
- **Open Websites**: Opens specified websites in the default web browser.
- **System Operations**: Can perform various system operations like opening applications, checking system status, etc.
- **WhatsApp Messaging**: Sends messages via WhatsApp.
- **Automated Tasks**: Automates repetitive tasks like taking screenshots, checking battery status, etc.
- **Weather Updates**: Fetches current weather information.
- **Custom Commands**: Supports adding custom commands for personalized automation.

## Requirements

Ensure you have the following libraries installed:

```sh
pip install pyttsx3 speech_recognition wikipedia webbrowser pywhatkit pyautogui psutil requests python-dateutil
```

## Setup

Clone or Download the Project:

You can either clone the repository or download the Python files to your local machine.
To clone via Git:
```sh
git clone https://github.com/your-repository-url.git
```
## Install Dependencies

Ensure you have the required dependencies installed using the following command:
```sh
pip install -r requirements.txt
```
This will install all the necessary Python libraries like pyttsx3, speech_recognition, wikipedia, etc.

## Setup Voice Recognition

Make sure your microphone is set up and working.
If you're using a virtual environment, activate it before running the assistant.

## Usage
### Run the Assistant

Once everything is set up, you can start the assistant by running the assistant.py script:
```sh
python assistant.py
```

Once running, use voice commands to interact with the assistant. Here are some example commands:

- **Search Wikipedia for Python programming**: Searches Wikipedia for information related to Python programming.
- **Open YouTube**: Opens YouTube in the default web browser.
- **Send a WhatsApp message to John**: Sends a message to John via WhatsApp.
- **What is the weather in Bangalore?**: Fetches the current weather information for Bangalore.
- **Tell me a joke**: Tells a random joke.
