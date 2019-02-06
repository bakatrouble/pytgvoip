import hashlib
import random
from typing import Union

import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api import functions, types
from pyrogram.api.types.messages import DhConfig
from tgvoip import *
from tgvoip._utils import i2b, twoe1984, calc_fingerprint, b2i


class DH:
    def __init__(self, dhc: DhConfig):
        self.p: int = int.from_bytes(dhc.p, 'big')
        self.g: int = dhc.g
        self.resp: DhConfig = dhc


class PyrogramVoIPCall:
    min_layer = 65

    def __init__(self, client: pyrogram.Client):
        self.client = client
        self.ctrl = VoIPController()
        self.ctrl_started = False
        self.call = None
        self.is_outgoing = None
        self.peer = None
        self.state = None
        self.dhc = self._get_dhc()
        self.a = None
        self.g_a = None
        self.g_a_hash = None
        self.b = None
        self.g_b = None
        self.g_b_hash = None
        self.auth_key = None
        self.auth_key_bytes = None
        self.key_fingerprint = None
        self.max_layer = VoIPController.CONNECTION_MAX_LAYER
        self._update_handler = RawUpdateHandler(self._process_update)
        self.client.add_handler(self._update_handler, -1)

    def _get_protocol(self):
        return types.PhoneCallProtocol(self.min_layer, self.max_layer, True, True)

    def _get_dhc(self) -> DH:
        return DH(self.client.send(functions.messages.GetDhConfig(0, 256)))

    def _check_g(self, g_x: int, p: int) -> None:
        if not (1 < g_x < p - 1):
            self._stop()
            raise RuntimeError('g_x is invalid (1 < g_x < p - 1 is false)')
        if not (twoe1984 < g_x < p - twoe1984):
            self._stop()
            raise RuntimeError('g_x is invalid (2^1984 < g_x < p - 2^1984 is false)')

    def _update_state(self, val: CallState):
        self.state = val
        self.ctrl.handle_state_change(val)

    def _stop(self):
        self.client.remove_handler(self._update_handler, -1)
        del self.ctrl
        self.ctrl = None

    def _call_ended(self):
        self._update_state(CallState.ENDED)
        self._stop()

    def _process_update(self, _, update, users, chats):
        if isinstance(update, types.UpdatePhoneCall):
            call = update.phone_call
            if not self.call or not call or call.id != self.call.id:
                raise pyrogram.ContinuePropagation
            if not hasattr(call, 'access_hash') or not call.access_hash:
                call.access_hash = self.call.access_hash
            self.call = call
            if isinstance(call, types.PhoneCallAccepted) and not self.auth_key:
                self._process_accepted_call()
            elif isinstance(call, types.PhoneCallDiscarded):
                self._call_discarded()
            elif isinstance(call, types.PhoneCall) and not self.auth_key:
                # TODO: complete_call
                if not call.g_a_or_b:
                    print('g_a is null')
                    return self._call_failed()
                if self.g_a_hash != hashlib.sha256(call.g_a_or_b).digest():
                    print('g_a_hash doesn\'t match')
                    return self._call_failed()
                self.g_a = call.g_a_or_b
        raise pyrogram.ContinuePropagation

    def _call_failed(self, error: CallError = None):
        if error is None:
            error = self.ctrl.get_last_error() if self.ctrl and self.ctrl_started else CallError.UNKNOWN
        print('Call', self.call_id, 'failed with error', error)
        self._update_state(CallState.FAILED)
        self._stop()

    def _initiate_encrypted_call(self):
        config = self.client.send(functions.help.GetConfig())  # type: types.Config
        self.ctrl.set_config(config.call_packet_timeout_ms / 1000., config.call_connect_timeout_ms / 1000.,
                             DataSaving.NEVER, self.call.id)
        self.ctrl.set_encryption_key(self.auth_key_bytes, self.is_outgoing)
        endpoints = [self.call.connection] + self.call.alternative_connections
        endpoints = [Endpoint(e.id, e.ip, e.ipv6, e.port, e.peer_tag) for e in endpoints]
        self.ctrl.set_remote_endpoints(endpoints, self.call.p2p_allowed, False, self.call.protocol.max_layer)
        # TODO: set proxy
        self.ctrl.start()
        self.ctrl.connect()
        self.ctrl_started = True

    @property
    def call_id(self):
        return self.call.id if self.call else 0

    # outgoing calls
    def start_outgoing_call(self, user_id: Union[int, str]):
        self._update_state(CallState.REQUESTING)
        self.is_outgoing = True
        self.peer = self.client.resolve_peer(user_id)
        self.a = random.randint(2, self.dhc.p-1)
        self.g_a = pow(self.dhc.g, self.a, self.dhc.p)
        self._check_g(self.g_a, self.dhc.p)
        self.g_a_hash = hashlib.sha256(i2b(self.g_a)).digest()
        self.call = self.client.send(functions.phone.RequestCall(
            user_id=self.peer,
            random_id=random.randint(0, 0x7fffffff - 1),
            g_a_hash=self.g_a_hash,
            protocol=self._get_protocol(),
        )).phone_call
        self._update_state(CallState.WAITING)
        return self.call

    def _process_accepted_call(self):
        self._update_state(CallState.EXCHANGING_KEYS)
        self.g_b = b2i(self.call.g_b)
        self._check_g(self.g_b, self.dhc.p)
        self.auth_key = pow(self.g_b, self.a, self.dhc.p)
        self.auth_key_bytes = i2b(self.auth_key)
        self.key_fingerprint = calc_fingerprint(self.auth_key_bytes)
        self.call = self.client.send(functions.phone.ConfirmCall(
            key_fingerprint=self.key_fingerprint,
            peer=types.InputPhoneCall(self.call.id, self.call.access_hash),
            g_a=i2b(self.g_a),
            protocol=self._get_protocol(),
        )).phone_call
        self._initiate_encrypted_call()
        return self.call

    def _call_discarded(self):
        # TODO: call.need_debug
        need_rate = self.ctrl and VoIPServerConfig.config.get('bad_call_rating') and self.ctrl.need_rate()
        if isinstance(self.call.reason, types.PhoneCallDiscardReasonBusy):
            self._update_state(CallState.BUSY)
            self._stop()
        else:
            self._call_ended()
        if self.call.need_rating or need_rate:
            pass  # TODO: rate
