from time import sleep

import pyrogram

from pyrogram_wrapper import PyrogramWrapper
from _tgvoip import VoIP


client = pyrogram.Client('session', 'app_id', 'app_hash', ipv6=True)
calls = PyrogramWrapper(client)

client.start()
voip = calls.request_call('@bakatrouble')
voip.play('input.raw')
voip.then('input.raw')
voip.play_on_hold(['input.raw'])
voip.set_output_file('output.raw')

while voip.get_call_state() < VoIP.CALL_STATE_ENDED:
    sleep(1)

client.stop()
