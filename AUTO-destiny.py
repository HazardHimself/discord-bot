import requests
from dotenv import dotenv_values
import bot_backbone
import json
import time

from bot_backbone import client, bot_setup

bot_backbone._bot_setup(function_server_file='servers_destiny.json')

BUNGIE_API_HEADERS = {"X-API-Key": bot_setup['BUNGIE_API_KEY']}

# Step 1: Find the vendors file.
api_call_bungie_manifest = dict()

def bungie_api_handshake():
    global api_call_bungie_manifest
    print("Initiating Bungie API handshake. Please be patient. This will take a while.")
    api_call_bungie_manifest = requests.get('https://www.bungie.net/Platform/Destiny2/Manifest/')
    api_call_bungie_manifest = api_call_bungie_manifest.json()
    if api_call_bungie_manifest['ErrorCode'] != 1:
        print("Couldn't access bungie api, trying again in a few seconds.")
        time.sleep(3)
        bungie_api_handshake()
    else:
        print("Bungie API handshake successful.")

bungie_api_handshake()

english_world_content_paths = api_call_bungie_manifest['Response']['jsonWorldComponentContentPaths']['en']

# Xur will be in the Vendor Definition File, so we want to find that.

vendor_definition_url = f"https://www.bungie.net{english_world_content_paths['DestinyVendorDefinition']}"

# Once we have that, we want to download that file.
# It's 2 million-ish lines. So this may take a while. And asking Python to sort through all of that without it *having* it could take a while.
with requests.get(vendor_definition_url, stream=True) as r:
    r.raise_for_status()
    with open('local_vendor_definition_file.json', 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192, decode_unicode=False):
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            # if chunk:
            f.write(chunk)

# Xur has weapons and armor. We want that shit. Get the item manifest file too.

item_definition_url = f"https://www.bungie.net{english_world_content_paths['DestinyInventoryItemDefinition']}"

with requests.get(item_definition_url, stream=True) as r:
    r.raise_for_status()
    with open('local_item_definition_file.json', 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192, decode_unicode=False):
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            # if chunk:
            f.write(chunk)

# Step 2: Isolate Xur.
# This file is 2 million lines long, once we find Xur, he's all we want to deal with.
local_vendor_definition_file = dict()
with open('local_vendor_definition_file.json', encoding='utf-8') as local_vendor_file:
    for i in local_vendor_file:
        local_vendor_definition_file = json.loads(i)

local_item_definition_file = dict()
with open('local_item_definition_file.json', encoding='utf-8') as local_item_file:
    for i in local_item_file:
        local_item_definition_file = json.loads(i)


# Get limited time vendors
api_call_vendors = requests.get("https://www.bungie.net/platform/Destiny2/Vendors/?components=400,402", headers=BUNGIE_API_HEADERS)
api_response_vendors = api_call_vendors.json()['Response']

# Find temp vendors
temp_vendor_list = []
for i in api_response_vendors['vendorGroups']['data']['groups']:
    if i['vendorGroupHash'] == 3227191227:
        temp_vendor_list = i['vendorHashes']

# Save the vendors to a list containing their hash and name for easier reference.
safe_vendor_lists = []
for i in temp_vendor_list:
    temp_dict = {
        'vendor_hash' : str(i),
        'vendor_name' : local_vendor_definition_file[str(i)]['displayProperties']['name']
    }
    safe_vendor_lists.append(temp_dict)

# Once we have the list of vendors, match their hashes to the overall vendor list.
for i in safe_vendor_lists:
    vendor_inventory = api_response_vendors['sales']['data'][i['vendor_hash']]['saleItems']
    vendor_inventory_readable = []
    # Loop through vendor inventory to pull item hash and name.
    for j in vendor_inventory:
        temp_dict = {
            'item_hash' : vendor_inventory[j]['itemHash'],
            'item_name' : local_item_definition_file[str(vendor_inventory[j]['itemHash'])]['displayProperties']['name']
        }
        temp_dict['item_cost'] = []
        # For each item, pull the cost and match the item hash of the required currency to the item file.
        for cost in vendor_inventory[j]['costs']:
            currency_amount = cost['quantity']
            currency_name = local_item_definition_file[str(cost['itemHash'])]['displayProperties']['name']
            temp_dict['item_cost'].append({
                'currency_name' : currency_name,
                'currency_amount' : currency_amount
            })
        vendor_inventory_readable.append(temp_dict)

    i['vendor_inventory'] = vendor_inventory_readable

# Finally, put it all together.
for i in safe_vendor_lists:
    vendor_message = f"# {i['vendor_name']} is selling:"
    for j in i['vendor_inventory']:
        if len(j['item_cost']) > 0:
            temp_entry = f"\n> {j['item_name']}"
            for k in j['item_cost']:
                currency_name = k['currency_name']
                if k['currency_amount'] != 1 and k['currency_name'][-1].lower() != 's': currency_name = f"{currency_name}s"
                temp_entry = f"{temp_entry}, {k['currency_amount']} {currency_name}"
            vendor_message = f"{vendor_message}{temp_entry}"
    i['vendor_message'] = vendor_message

@client.event
async def on_ready():
    if (bot_backbone.servers_object != {}):
        for value in bot_backbone.servers_object.values():
            for i in safe_vendor_lists:
                await client.get_channel(value).send(i['vendor_message'])
    quit()

client.run(bot_setup['DISCORD_BOT_CLIENT_ID'])