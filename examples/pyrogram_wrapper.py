import hashlib
import json
import random
from datetime import datetime

import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api import errors
from pyrogram.api.functions.help import GetConfig
from pyrogram.api.functions.messages import GetDhConfig
from pyrogram.api.functions.phone import SaveCallDebug, SetCallRating, DiscardCall, GetCallConfig, RequestCall, \
    AcceptCall, ConfirmCall
from pyrogram.api.types import UpdatePhoneCall, DataJSON, PhoneCallDiscardReasonDisconnect, PhoneCallProtocol, \
    InputPhoneCall, PhoneCallRequested, PhoneCallAccepted, PhoneCallDiscarded, PhoneCall

from utils import integer_to_bytes, calc_fingerprint, check_g, generate_visualization
from _tgvoip import VoIP


class PyrogramWrapper:
    min_layer = 65

    def __init__(self, client: pyrogram.Client, shared_config_callback=None):
        self.client = client
        client.add_handler(RawUpdateHandler(self._process_raw_update))
        self.shared_config_callback = shared_config_callback
        self.voips = {}
        voip = VoIP()
        self.max_layer = voip.get_connection_max_layer()
        if shared_config_callback:
            voip.set_shared_config(json.dumps(shared_config_callback({})))

    def _process_raw_update(self, cl, update, users, chats):
        if isinstance(update, UpdatePhoneCall):
            pc = update.phone_call
            if isinstance(pc, PhoneCallRequested):
                if self.get_voip(pc.id):
                    raise pyrogram.StopPropagation
                voip = VoIP(False, pc.admin_id, InputPhoneCall(pc.id, pc.access_hash),
                            self, VoIP.CALL_STATE_INCOMING, pc.protocol)
                voip.storage['g_a_hash'] = pc.g_a_hash
                self.voips[pc.id] = voip
            elif isinstance(pc, PhoneCallAccepted):
                if not self.confirm_call(pc):
                    raise pyrogram.StopPropagation
            elif isinstance(pc, PhoneCall):
                if not self.complete_call(pc):
                    raise pyrogram.StopPropagation
            elif isinstance(pc, PhoneCallDiscarded):
                voip = self.get_voip(pc.id)
                if not voip:
                    raise pyrogram.StopPropagation
                voip.discard(pc.reason, None, pc.need_debug)
            raise pyrogram.ContinuePropagation

    def _get_protocol(self):
        return PhoneCallProtocol(self.min_layer, self.max_layer, True, True)

    def _get_dh_config(self):
        class DH:
            def __init__(self, dhc):
                self.p = int.from_bytes(dhc.p, 'big')
                self.g = dhc.g
                self.resp = dhc

        return DH(self.client.send(GetDhConfig(0, 256)))

    def _discard_ended_voips(self):
        for voip in self.voips.values():
            if voip.get_call_state() == VoIP.CALL_STATE_ENDED:
                voip.discard(PhoneCallDiscardReasonDisconnect(), None, True)

    def _configure_voip(self, voip, call, bytes_key, key_fingerprint, visualization_part2):
        visualization = generate_visualization(bytes_key, visualization_part2)
        config = self.client.send(GetConfig())
        voip.set_visualization(visualization)
        call_config = self.client.send(GetCallConfig()).data
        if callable(self.shared_config_callback):
            voip.configuration['shared_config'] = json.dumps(self.shared_config_callback(json.loads(call_config)))
        else:
            voip.configuration['shared_config'] = call_config
        voip.configuration['endpoints'].extend([call.connection] + call.alternative_connections)
        voip.configuration.update({
            'recv_timeout': config.call_receive_timeout_ms / 1000,
            'init_timeout': config.call_connect_timeout_ms / 1000,
            'data_saving': VoIP.DATA_SAVING_NEVER,
            'enable_NS': True,
            'enable_AEC': True,
            'enable_AGC': True,
            'auth_key': bytes_key,
            'auth_key_id': key_fingerprint,
            'call_id': hashlib.sha256(bytes_key).digest()[-16:],
            'network_type': VoIP.NET_TYPE_ETHERNET,
        })
        voip.parse_config()
        return voip.start_the_magic()

    def request_call(self, user_id):
        self._discard_ended_voips()
        peer = self.client.resolve_peer(user_id)
        dhc = self._get_dh_config()
        a = random.randint(2, dhc.p-1)
        g_a = pow(dhc.g, a, dhc.p)
        check_g(g_a, dhc.p)
        g_a_hash = hashlib.sha256(integer_to_bytes(g_a)).digest()
        protocol = self._get_protocol()
        call = self.client.send(RequestCall(
            user_id=peer,
            random_id=random.randint(0, 0x7fffffff - 1),
            g_a_hash=g_a_hash,
            protocol=protocol,
        ))
        voip = self.voips[call.phone_call.id] = VoIP(True, peer.user_id,
                                                     InputPhoneCall(call.phone_call.id, call.phone_call.access_hash),
                                                     self, VoIP.CALL_STATE_REQUESTED, protocol)
        voip.storage = {'a': a, 'g_a': integer_to_bytes(g_a).ljust(256, b'\0')}
        return voip

    def accept_call(self, call):
        self._discard_ended_voips()
        if self.call_status(call.id) != VoIP.CALL_STATE_ACCEPTED:
            return False
        dhc = self._get_dh_config()
        b = random.randint(2, dhc.p-1)
        g_b = pow(dhc.g, b, dhc.p)
        check_g(g_b, dhc.p)
        try:
            res = self.client.send(AcceptCall(
                peer=call,
                g_b=integer_to_bytes(g_b),
                protocol=self._get_protocol()
            ))
        except errors.Error as e:
            if e.CODE == 'CALL_ALREADY_ACCEPTED':
                return True
            elif e.CODE == 'CALL_ALREADY_DECLINED':
                return False
            raise e
        self.get_voip(res.phone_call.id).storage['b'] = b
        return True

    def confirm_call(self, call):
        self._discard_ended_voips()
        if self.call_status(call.id) != VoIP.CALL_STATE_REQUESTED:
            return False
        voip = self.get_voip(call.id)
        dhc = self._get_dh_config()
        g_b = int.from_bytes(call.g_b, 'big')
        check_g(g_b, dhc.p)
        key = pow(g_b, voip.storage['a'], dhc.p)
        bytes_key = integer_to_bytes(key)
        key_fingerprint = calc_fingerprint(integer_to_bytes(key))
        call = self.client.send(ConfirmCall(
            key_fingerprint=key_fingerprint,
            peer=InputPhoneCall(call.id, call.access_hash),
            g_a=voip.storage['g_a'],
            protocol=self._get_protocol()
        )).phone_call
        return self._configure_voip(voip, call, bytes_key, key_fingerprint, voip.storage['g_a'])

    def complete_call(self, call):
        self._discard_ended_voips()
        voip = self.get_voip(call.id)
        if self.call_status(call.id) != VoIP.CALL_STATE_ACCEPTED or not voip.storage.get('b'):
            return False
        dhc = self._get_dh_config()
        if hashlib.sha256(call.g_a_or_b).digest() != voip.storage['g_a_hash']:
            raise RuntimeError('Invalid g_a')
        g_a_or_b = int.from_bytes(call.g_a_or_b, 'big')
        check_g(g_a_or_b, dhc.p)
        key = pow(g_a_or_b, voip.storage['b'], dhc.p)
        bytes_key = integer_to_bytes(key)
        key_fingerprint = calc_fingerprint(bytes_key)
        if key_fingerprint != call.key_fingerprint:
            raise RuntimeError('Invalid fingerprint')
        return self._configure_voip(voip, call, bytes_key, key_fingerprint, call.g_a_or_b)

    def call_status(self, call_id):
        self._discard_ended_voips()
        if call_id in self.voips:
            return self.get_voip(call_id).get_call_state()
        return VoIP.CALL_STATE_NONE

    def get_voip(self, call_id):
        self._discard_ended_voips()
        return self.voips.get(call_id)

    def discard_call(self, call, reason=None, rating=None, debug=True):
        if not reason:
            reason = PhoneCallDiscardReasonDisconnect()
        voip = self.get_voip(call.id)
        if not voip:
            return
        try:
            self.client.send(DiscardCall(
                peer=call,
                duration=int(datetime.now().timestamp() - (voip.when_created() or 0)),
                connection_id=voip.get_preferred_relay_id(),
                reason=reason
            ))
        except pyrogram.Error as e:
            if e.CODE not in ['CALL_ALREADY_DECLINED', 'CALL_ALREADY_ACCEPTED']:
                raise e
        if rating:
            self.client.send(SetCallRating(
                peer=call,
                rating=rating.rating,
                comment=rating.comment
            ))
        if debug:
            self.client.send(SaveCallDebug(
                peer=call,
                debug=DataJSON(json.dumps(voip.get_debug_log()))
            ))
        print(voip.get_debug_log())
        update = UpdatePhoneCall(phone_call=call)
        self.client.updates_queue.put(update)
        del self.voips[call.id]
        self._discard_ended_voips()
