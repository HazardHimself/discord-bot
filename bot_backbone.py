import discord
import os
import json
import io
from dotenv import dotenv_values, find_dotenv

global client
global servers_object
global file_locale
global file_location
global server_file
global bot_setup

bot_setup = dotenv_values(find_dotenv())

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def _bot_setup(function_server_file: str = 'servers_default.json', function_file_location: str = '/files/'):
    global client
    global servers_object
    global file_locale
    global file_location
    global server_file

    file_location = function_file_location
    server_file = function_server_file
    file_locale = os.path.dirname(os.path.abspath(__file__))

    if os.path.isfile(file_locale+'/'+server_file) & os.access(file_locale+'/'+server_file, os.R_OK) & os.access(file_locale+'/'+server_file, os.W_OK):
        print('File check successful.')
    else:
        print('File cannot be read or does not exist, creating...')
        with io.open(file_locale+'/'+server_file, 'w') as f:
            f.write(json.dumps({}))
            f.close()

    with io.open(file_locale+'/'+server_file, 'r') as f:
        global servers_object
        servers_object = json.load(f)
        f.close()


def _bot_default_setup():
    _bot_setup()


def command_check(message, command):
    return message.content.lower().startswith(command)


def set_server_file_value(key, value):
    servers_object[key] = value
    with io.open(file_locale+'/'+server_file, 'w') as f:
        f.write(json.dumps(servers_object))
        f.close()


async def send_timed_message_FILE(filename):
    if (servers_object != {}) & (os.path.isfile(file_locale+file_location+filename)):
        for value in servers_object.values():
            await client.get_channel(value).send(file=discord.File(r''+file_locale+file_location+filename))


async def send_timed_message_GIF(location):
    if (servers_object != {}):
        for value in servers_object.values():
            await client.get_channel(value).send(location)


def get_available_modes():
    available_modes = []
    root_directory = os.listdir(file_locale)
    for file in root_directory:
        if (os.path.isfile(file)):
            file_name = file
            file_path = os.path.realpath(file)
            file_extension = os.path.splitext(file_path)[1]
            if file_extension == '.json' and 'servers_' in file_name:
                mode_keyword = file_name.replace(
                    'servers_', '').replace('.json', '')
                available_modes.append(mode_keyword)
    return available_modes

def setmode_handler(full_message_text: str):
    command_arguments = full_message_text.split()
    command_arguments.pop(0)
    available_modes = get_available_modes()
    mode_list = '\n> '.join(available_modes)
    if len(available_modes) > 0: response_suffix = f"\nAvailable modes are:\n> {mode_list}"
    if len(command_arguments) > 0:
        server_file_mode = command_arguments[0]
        if server_file_mode in available_modes:
            server_file_name = f'servers_{server_file_mode}.json'
            _bot_setup(function_server_file=server_file_name)
            response_message = f"Done and dusted! We should be in {server_file_mode} mode!"
        else:
            response_message = f"Sorry, that doesn't appear to be a mode.{response_suffix}"
    else:
        response_message = f"Sorry, I don't think you told me which mode to use.{response_suffix}"
    return response_message

_bot_default_setup()
