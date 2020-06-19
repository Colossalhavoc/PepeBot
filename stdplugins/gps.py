"""Syntax : .gps <location name>
  help from @sunda005
  credits :@mrconfused
  don't edit credits"""

from geopy.geocoders import Nominatim
from uniborg.util import admin_cmd
from telethon.tl import types


@borg.on(admin_cmd(pattern="gps ?(.*)"))
async def gps(event):
    if event.fwd_from:
        return
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    input_str = event.pattern_match.group(1)
 
    if not input_str:
        return await event.edit("what should i find give me location.")

    await event.edit("finding")
         
    geolocator = Nominatim(user_agent="catuserbot")
    geoloc = geolocator.geocode(input_str) 
    if geoloc:
        lon = geoloc.longitude
        lat = geoloc.latitude
        await event.reply(
            input_str,
            file=types.InputMediaGeoPoint(
                types.InputGeoPoint(
                    lat, lon
                )
            ),
            reply_to=reply_to_id
        )
        await event.delete()
    else:
        await event.edit("i coudn't find it")