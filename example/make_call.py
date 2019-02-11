from tgvoip import VoIPServerConfig, VoIPFileStreamService
import pyrogram


VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
client.start()

voip_service = VoIPFileStreamService(client, receive_calls=False)
call = voip_service.start_call('@bakatrouble')
call.play('input.raw')
call.play_on_hold(['input.raw'])
call.set_output_file('output.raw')


@call.on_call_state_changed
def state_changed(call, state):
    print('State changed:', call, state)


client.idle()
