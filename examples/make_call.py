from time import sleep

import pyrogram

from pyrogram_wrapper import PyrogramWrapper
from _tgvoip import VoIP


def configure_voip(cnf):
    cnf['audio_init_bitrate'] = 80000
    cnf['audio_max_bitrate'] = 100000
    cnf['audio_min_bitrate'] = 60000
    cnf['audio_bitrate_step_decr'] = 5000
    cnf['audio_bitrate_step_incr'] = 5000
    return cnf


client = pyrogram.Client('session', 'app_id', 'app_hash', ipv6=True)
calls = PyrogramWrapper(client, configure_voip)

client.start()
voip = calls.request_call('@username')
voip.play('input.raw')
voip.play_on_hold(['input.raw'])
voip.set_output_file('output.raw')

while voip.get_call_state() < VoIP.CALL_STATE_ENDED:
    sleep(1)

client.stop()
