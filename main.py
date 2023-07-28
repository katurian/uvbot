import re
import discord
import requests
from datetime import datetime
import json
from urllib.parse import quote

def get_uv_color(uv_value):
    if uv_value <= 2:
        return "rgba(0, 255, 0, 0.6)" # green
    elif uv_value <= 5:
        return "rgba(255, 255, 0, 0.6)" # yellow
    elif uv_value <= 7:
        return "rgba(255, 165, 0, 0.6)" # orange
    elif uv_value <= 10:
        return "rgba(255, 0, 0, 0.6)" # red
    else:
        return "rgba(238, 130, 238, 0.6)" # violet

with open('config.json', 'r') as f:
    data = json.load(f)

intents = discord.Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Beep Boop, I am uvbot!')
    print("------")
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if '?uv' in message.content:
        labels = []
        uv_values = []
        zipcode = re.search(r'\d{5}', message.content).group(0)
        response = requests.get(f'https://data.epa.gov/efservice/getEnvirofactsUVHourly/ZIP/{zipcode}/JSON')
        uv_json = response.json()
        for item in uv_json:  
            if int(item['UV_VALUE']) > 0:
                dt_obj = datetime.strptime(item['DATE_TIME'], '%b/%d/%Y %I %p')
                labels.append(dt_obj.strftime('%I %p'))
                uv_values.append(int(item['UV_VALUE']))
            else:
                continue
        uv_colors = [get_uv_color(value) for value in uv_values]
        chart_config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [ 
                    {
                        "label": "UV Index",
                        "data": uv_values,
                        "backgroundColor": uv_colors
                    }
                ],
            },
            "options": {"legend": {"display": False}, "title": {"display": True, "text": zipcode}}
        }
        chart_config = json.dumps(chart_config, indent=2)
        postdata = {
          'chart': chart_config,
          'width': 500,
          'height': 300,
          'backgroundColor': 'white',
        }
        response = requests.post('https://quickchart.io/chart/create', json=postdata)
        parsed = json.loads(response.text)
        await message.reply(parsed["url"])

client.run(data['token'])
