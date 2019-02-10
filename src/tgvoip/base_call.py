import pyrogram
from pyrogram.api import types, functions, errors

from tgvoip import VoIPController, CallState, CallError, Endpoint, DataSaving, VoIPServerConfig
from tgvoip._utils import i2b, b2i, twoe1984, get_real_elapsed_time


class DH:
    def __init__(self, dhc: types.messages.DhConfig):
        self.p = b2i(dhc.p)
        self.g = dhc.g
        self.resp = dhc


class VoIPCallBase:
    min_layer = 65
    max_layer = VoIPController.CONNECTION_MAX_LAYER
    is_outgoing = False

    def __init__(self, client: pyrogram.Client, use_proxy_if_available: bool = True):
        if not client.is_started:
            raise RuntimeError('Client must be started first')
        self.client = client
        self.ctrl = VoIPController()
        self.ctrl_started = False
        self.call = None
        self.peer = None
        self.state = None
        self.dhc = self.get_dhc()
        self.a = None
        self.g_a = None
        self.g_a_hash = None
        self.b = None
        self.g_b = None
        self.g_b_hash = None
        self.auth_key = None
        self.key_fingerprint = None

        if use_proxy_if_available and client.proxy:
            proxy = self.client.proxy
            self.ctrl.set_proxy(proxy['hostname'], proxy['port'], proxy['username'], proxy['password'])

        self._update_handler = pyrogram.RawUpdateHandler(self.process_update)
        self.client.add_handler(self._update_handler, -1)

    def process_update(self, _, update, users, chats):
        if not isinstance(update, types.UpdatePhoneCall):
            raise pyrogram.ContinuePropagation

        call = update.phone_call
        if not self.call or not call or call.id != self.call.id:
            raise pyrogram.ContinuePropagation
        if not hasattr(call, 'access_hash') or not call.access_hash:
            call.access_hash = self.call.access_hash
        self.call = call

        if isinstance(call, types.PhoneCallDiscarded):
            self.call_discarded()
            raise pyrogram.StopPropagation

    @property
    def auth_key_bytes(self) -> bytes:
        return i2b(self.auth_key) if self.auth_key is not None else b''

    @property
    def call_id(self) -> int:
        return self.call.id if self.call else 0

    def get_protocol(self) -> types.PhoneCallProtocol:
        return types.PhoneCallProtocol(self.min_layer, self.max_layer, True, True)

    def get_dhc(self) -> DH:
        return DH(self.client.send(functions.messages.GetDhConfig(0, 256)))

    def check_g(self, g_x: int, p: int) -> None:
        if not (1 < g_x < p - 1):
            self.stop()
            raise RuntimeError('g_x is invalid (1 < g_x < p - 1 is false)')
        if not (twoe1984 < g_x < p - twoe1984):
            self.stop()
            raise RuntimeError('g_x is invalid (2^1984 < g_x < p - 2^1984 is false)')

    def stop(self) -> None:
        try:
            self.client.remove_handler(self._update_handler, -1)
        except ValueError:
            pass
        del self.ctrl
        self.ctrl = None

    def update_state(self, val: CallState) -> None:
        self.state = val
        self.ctrl.handle_state_change(val)

    def call_ended(self) -> None:
        self.update_state(CallState.ENDED)
        self.stop()

    def call_failed(self, error: CallError = None) -> None:
        if error is None:
            error = self.ctrl.get_last_error() if self.ctrl and self.ctrl_started else CallError.UNKNOWN
        print('Call', self.call_id, 'failed with error', error)
        self.update_state(CallState.FAILED)
        self.stop()

    def call_discarded(self):
        # TODO: call.need_debug
        need_rate = self.ctrl and VoIPServerConfig.config.get('bad_call_rating') and self.ctrl.need_rate()
        if isinstance(self.call.reason, types.PhoneCallDiscardReasonBusy):
            self.update_state(CallState.BUSY)
            self.stop()
        else:
            self.call_ended()
        if self.call.need_rating or need_rate:
            pass  # TODO: rate

    def discard_call(self, reason=None):
        # TODO: rating
        if not reason:
            reason = types.PhoneCallDiscardReasonDisconnect()
        try:
            self.client.send(functions.phone.DiscardCall(
                peer=types.InputPhoneCall(self.call_id, self.call.access_hash),
                duration=int(get_real_elapsed_time() - (self.ctrl.start_time or 0)),
                connection_id=self.ctrl.get_preferred_relay_id(),
                reason=reason
            ))
        except (errors.CallAlreadyDeclined, errors.CallAlreadyAccepted):
            pass
        self.call_ended()

    def _initiate_encrypted_call(self) -> None:
        config = self.client.send(functions.help.GetConfig())  # type: types.Config
        self.ctrl.set_config(config.call_packet_timeout_ms / 1000., config.call_connect_timeout_ms / 1000.,
                             DataSaving.NEVER, self.call.id)
        self.ctrl.set_encryption_key(self.auth_key_bytes, self.is_outgoing)
        endpoints = [self.call.connection] + self.call.alternative_connections
        endpoints = [Endpoint(e.id, e.ip, e.ipv6, e.port, e.peer_tag) for e in endpoints]
        self.ctrl.set_remote_endpoints(endpoints, self.call.p2p_allowed, False, self.call.protocol.max_layer)
        self.ctrl.start()
        self.ctrl.connect()
        self.ctrl_started = True
        self.update_state(CallState.ESTABLISHED)
