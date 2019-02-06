from typing import Union

import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api import types

from .call import PyrogramVoIPCall


class VoIPService:
    def __init__(self, client: pyrogram.Client, receive_calls=True):
        self.client = client
        self.incoming_call_handlers = []
        if receive_calls:
            client.add_handler(RawUpdateHandler(self.update_handler), -1)
        client.on_message()

    def on_incoming_call(self):
        def decorator(func: callable) -> callable:
            self.incoming_call_handlers.append(func)
            return func
        return decorator

    def start_call(self, user_id: Union[str, int]):
        call = PyrogramVoIPCall(self.client)
        call.start_outgoing_call(user_id)
        return call

    def update_handler(self, _, update, users, chats):
        if isinstance(update, types.UpdatePhoneCall):
            call = update.phone_call
            if isinstance(call, types.PhoneCallRequested):
                voip_call = PyrogramVoIPCall.build_incoming_call(self.client, call)
                for handler in self.incoming_call_handlers:
                    handler(voip_call)
        raise pyrogram.ContinuePropagation
