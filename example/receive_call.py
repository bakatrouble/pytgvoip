import pyrogram

from tgvoip import VoIPServerConfig, VoIPFileStreamService, VoIPIncomingFileStreamCall

VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
client.start()
service = VoIPFileStreamService(client)


@service.on_incoming_call
def process_call(call: VoIPIncomingFileStreamCall):
    call.accept()
    call.play('input.raw')
    call.play_on_hold(['input.raw'])
    call.set_output_file('output.raw')


client.idle()
