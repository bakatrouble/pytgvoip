import logging

from tgvoip import PyrogramVoIPCall, VoIPServerConfig, VoIPService
import pyrogram


logging.basicConfig(level=logging.INFO)


VoIPServerConfig.set_config({
    'audio_init_bitrate': 80000,
    'audio_max_bitrate': 100000,
    'audio_min_bitrate': 60000,
    'audio_bitrate_step_decr': 5000,
    'audio_bitrate_step_incr': 5000
})


client = pyrogram.Client('session')
client.start()
voip_service = VoIPService(client, receive_calls=False)

f = open('output.raw', 'wb')
f2 = open('ochinchin.raw', 'rb')
def write(frame):
    f.write(frame)
def read(length):
    return f2.read(length)
call = voip_service.start_call('@bakatrouble')
call.ctrl.set_recv_audio_frame_callback(write)
call.ctrl.set_send_audio_frame_callback(read)
client.idle()
