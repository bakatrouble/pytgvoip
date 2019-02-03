import os
import hashlib
import random
from time import sleep
import json
from datetime import datetime
import unicodedata
import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api import errors
from pyrogram.api.functions.messages import GetDhConfig
from pyrogram.api.functions.help import GetConfig
from pyrogram.api.functions.phone import RequestCall, AcceptCall, ConfirmCall, GetCallConfig, DiscardCall, SaveCallDebug
from pyrogram.api.types import PhoneCallProtocol, InputPhoneCall, UpdatePhoneCall, PhoneCallRequested, \
                               PhoneCallAccepted, PhoneCall, PhoneCallDiscarded, PhoneCallDiscardReasonDisconnect, \
                               DataJSON
from _tgvoip import VoIP


def get_rand_bytes(dhc, length=256):
    return bytes(x ^ y for x, y in zip(
        os.urandom(length), dhc.resp.random
    ))


def integer_to_bytes(integer):
    return int.to_bytes(
        integer,
        length=(integer.bit_length() + 8 - 1) // 8,  # 8 bits per byte,
        byteorder='big',
        signed=False
    )


EMOJIS = ['😉', '😍', '😛', '😭', '😱', '😡', '😎', '😴', '😵', '😈', '😬', '😇', '😏', '👮', '👷', '💂', '👶', '👨', '👩', '👴', '👵',
          '😻', '😽', '🙀', '👺', '🙈', '🙉', '🙊', '💀', '👽', '💩', '🔥', '💥', '💤', '👂', '👀', '👃', '👅', '👄', '👍', '👎', '👌', '👊', '✌',
          '✋', '👐', '👆', '👇', '👉', '👈', '🙏', '👏', '💪', '🚶', '🏃', '💃', '👫', '👪', '👬', '👭', '💅', '🎩', '👑', '👒', '👟', '👞', '👠', '👕',
          '👗', '👖', '👙', '👜', '👓', '🎀', '💄', '💛', '💙', '💜', '💚', '💍', '💎', '🐶', '🐺', '🐱', '🐭', '🐹', '🐰', '🐸', '🐯', '🐨', '🐻', '🐷', '🐮',
          '🐗', '🐴', '🐑', '🐘', '🐼', '🐧', '🐥', '🐔', '🐍', '🐢', '🐛', '🐝', '🐜', '🐞', '🐌', '🐙', '🐚', '🐟', '🐬', '🐋', '🐐', '🐊', '🐫', '🍀', '🌹', '🌻',
          '🍁', '🌾', '🍄', '🌵', '🌴', '🌳', '🌞', '🌚', '🌙', '🌎', '🌋', '⚡', '☔', '❄', '⛄', '🌀', '🌈', '🌊', '🎓', '🎆', '🎃', '👻', '🎅', '🎄',
          '🎁', '🎈', '🔮', '🎥', '📷', '💿', '💻', '☎', '📡', '📺', '📻', '🔉', '🔔', '⏳', '⏰', '⌚', '🔒', '🔑', '🔎', '💡', '🔦', '🔌', '🔋',
          '🚿', '🚽', '🔧', '🔨', '🚪', '🚬', '💣', '🔫', '🔪', '💊', '💉', '💰', '💵', '💳', '✉', '📫', '📦', '📅', '📁', '✂', '📌', '📎', '✒',
          '✏', '📐', '📚', '🔬', '🔭', '🎨', '🎬', '🎤', '🎧', '🎵', '🎹', '🎻', '🎺', '🎸', '👾', '🎮', '🃏', '🎲', '🎯', '🏈', '🏀', '⚽', '⚾',
          '🎾', '🎱', '🏉', '🎳', '🏁', '🏇', '🏆', '🏊', '🏄', '☕', '🍼', '🍺', '🍷', '🍴', '🍕', '🍔', '🍟', '🍗', '🍱', '🍚', '🍜', '🍡', '🍳', '🍞', '🍩',
          '🍦', '🎂', '🍰', '🍪', '🍫', '🍭', '🍯', '🍎', '🍏', '🍊', '🍋', '🍒', '🍇', '🍉', '🍓', '🍑', '🍌', '🍐', '🍍', '🍆', '🍅', '🌽', '🏡', '🏥', '🏦', '⛪',
          '🏰', '⛺', '🏭', '🗻', '🗽', '🎠', '🎡', '⛲', '🎢', '🚢', '🚤', '⚓', '🚀', '✈', '🚁', '🚂', '🚋', '🚎', '🚌', '🚙', '🚗', '🚕', '🚛', '🚨', '🚔',
          '🚒', '🚑', '🚲', '🚠', '🚜', '🚦', '⚠', '🚧', '⛽', '🎰', '🗿', '🎪', '🎭', '🇯🇵', '🇰🇷', '🇩🇪', '🇨🇳', '🇺🇸', '🇫🇷', '🇪🇸', '🇮🇹', '🇷🇺', '🇬🇧', '1⃣',
          '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '0⃣', '🔟', '❗', '❓', '♥', '♦', '💯', '🔗', '🔱', '🔴', '🔵', '🔶', '🔷']


class AuthKeyHandler:
    def __init__(self, client):
        self.client = client  # type: pyrogram.Client
        self.voips = {}

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
                voip.discard()

    def _calc_fingerprint(self, key):
        return int.from_bytes(
            bytes(hashlib.sha1(key).digest()[-8:]), 'little', signed=True
        )

    def request_call(self, user_id):
        PROTOCOL = PhoneCallProtocol(min_layer=65, max_layer=65, udp_p2p=True, udp_reflector=True)
        self._discard_ended_voips()
        peer = self.client.resolve_peer(user_id)
        dhc = self._get_dh_config()
        a = 0
        while not (1 < a < dhc.p - 1):
            a = int.from_bytes(get_rand_bytes(dhc), 'little')
        g_a = pow(dhc.g, a, dhc.p)  # check_g(g_a, dhc.p)
        g_a_hash = hashlib.sha256(integer_to_bytes(g_a)).digest()
        res = self.client.send(RequestCall(
            user_id=peer,
            random_id=random.randint(0, 0x7fffffff - 1),
            g_a_hash=g_a_hash,
            protocol=PROTOCOL,
        ))
        voip = self.voips[res.phone_call.id] = VoIP(True, peer.user_id,
                                                    InputPhoneCall(res.phone_call.id, res.phone_call.access_hash),
                                                    self, VoIP.CALL_STATE_REQUESTED, PROTOCOL)
        voip.storage = {'a': a, 'g_a': integer_to_bytes(g_a).ljust(256, b'\0')}
        return voip

    def accept_call(self, call):
        self._discard_ended_voips()
        if self.call_status(call.id) != VoIP.CALL_STATE_ACCEPTED:
            return False
        dhc = self._get_dh_config()
        b = random.randint(2, dhc.p-1)
        g_b = pow(dhc.g, b, dhc.p)  # check_g(g_b, dhc.p)
        try:
            res = self.client.send(AcceptCall(
                peer=call,
                g_b=integer_to_bytes(g_b),
                protocol=PhoneCallProtocol(min_layer=65, max_layer=65, udp_p2p=False, udp_reflector=True)  # call.p2p_allowed?
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
        # self.check_g(params['g_b'], dhc.p)
        key = pow(int.from_bytes(call.g_b, 'big'), voip.storage['a'], dhc.p)
        bytes_key = integer_to_bytes(key)
        key_fingerprint = self._calc_fingerprint(integer_to_bytes(key))
        res = self.client.send(ConfirmCall(
            key_fingerprint=key_fingerprint,
            peer=InputPhoneCall(call.id, call.access_hash),
            g_a=voip.storage['g_a'],
            protocol=PhoneCallProtocol(min_layer=65, max_layer=65, udp_reflector=True)
        )).phone_call
        visualization = []
        vis_src = hashlib.sha256(bytes_key + voip.storage['g_a']).digest()
        for i in range(0, len(vis_src), 8):
            number = vis_src[i:i+8]
            number = integer_to_bytes(number[0] & 0x7f) + number[1:]
            visualization.append(EMOJIS[int.from_bytes(number, 'big') % len(EMOJIS)])
        print(', '.join([unicodedata.name(emoji) for emoji in visualization]))
        config = self.client.send(GetConfig())
        voip.set_visualization(visualization)
        shared_config = json.loads(self.client.send(GetCallConfig()).data)
        for k in shared_config:
            shared_config[k] = str(shared_config[k]).lower() if isinstance(shared_config[k], bool) else str(shared_config[k])
        voip.configuration['shared_config'].update(shared_config)
        voip.configuration['endpoints'].extend([res.connection] + res.alternative_connections)
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

    def complete_call(self, call):
        self._discard_ended_voips()
        voip = self.get_voip(call.id)
        if self.call_status(call.id) != VoIP.CALL_STATE_ACCEPTED or not voip.storage.get('b'):
            return False
        dhc = self._get_dh_config()
        if hashlib.sha256(call.g_a_or_b).digest() != voip.storage['g_a_hash']:
            raise RuntimeError('Invalid g_a')
        # self.check_g(params['g_a_or_b'], dhc.p)
        key = pow(int.from_bytes(call.g_a_or_b, 'big'), voip.storage['b'], dhc.p)
        bytes_key = integer_to_bytes(key)
        key_fingerprint = self._calc_fingerprint(bytes_key)
        if key_fingerprint != call.key_fingerprint:
            raise RuntimeError('Invalid fingerprint')
        visualization = []
        vis_src = hashlib.sha256(bytes_key + call.g_a_or_b).digest()
        for i in range(0, len(vis_src), 8):
            number = vis_src[i:i+8]
            number = integer_to_bytes(number[0] & 0x7f) + number[1:]
            visualization.append(EMOJIS[int.from_bytes(number, 'big') % len(EMOJIS)])
        print(', '.join([unicodedata.name(emoji) for emoji in visualization]))
        config = self.client.send(GetConfig())
        voip.set_visualization(visualization)
        voip.configuration['shared_config'].update(json.loads(self.client.send(GetCallConfig()).data))
        voip.configuration['endpoints'].extend([call.connection] + call.alternative_connections)
        voip.configuration.update({
            'recv_timeout': config.call_receive_timeout_ms // 1000,
            'init_timeout': config.call_connect_timeout_ms // 1000,
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

    def call_status(self, call_id):
        self._discard_ended_voips()
        if call_id in self.voips:
            return self.get_voip(call_id).get_call_state()
        return VoIP.CALL_STATE_NONE

    def get_voip(self, call_id):
        self._discard_ended_voips()
        return self.voips.get(call_id)

    def discard_call(self, call, reason, rating, debug=True):
        voip = self.get_voip(call.id)
        if not voip:
            return
        try:
            self.client.send(DiscardCall(
                peer=call,
                duration=int(datetime.now().timestamp() - (voip.when_created() or 0)),
                connection_id=voip.get_preferred_relay_id(),
                reason=PhoneCallDiscardReasonDisconnect()
            ))
        except pyrogram.Error as e:
            if e.CODE not in ['CALL_ALREADY_DECLINED', 'CALL_ALREADY_ACCEPTED']:
                raise e
        if rating:
            pass
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


def process_raw_update(cl, update, users, chats):
    if isinstance(update, UpdatePhoneCall):
        pc = update.phone_call
        if isinstance(pc, PhoneCallRequested):
            if key_handler.get_voip(pc.id):
                raise pyrogram.StopPropagation
            voip = VoIP(False, pc.admin_id, InputPhoneCall(pc.id, pc.access_hash), key_handler,
                        VoIP.CALL_STATE_INCOMING, pc.protocol)
            voip.storage['g_a_hash'] = pc.g_a_hash
            key_handler.voips[pc.id] = voip
        elif isinstance(pc, PhoneCallAccepted):
            if not key_handler.confirm_call(pc):
                raise pyrogram.StopPropagation
        elif isinstance(pc, PhoneCall):
            if not key_handler.complete_call(pc):
                raise pyrogram.StopPropagation
        elif isinstance(pc, PhoneCallDiscarded):
            voip = key_handler.get_voip(pc.id)
            if not voip:
                raise pyrogram.StopPropagation
            return voip.discard(str(pc.reason), None, pc.need_debug)


def accept_call(cl, update, users, chats):
    if isinstance(update, UpdatePhoneCall):
        pc = update.phone_call
        voip = key_handler.get_voip(pc.id)
        if voip and voip.get_call_state() == VoIP.CALL_STATE_INCOMING:
            voip.accept()
            voip.play('input.raw')
            voip.set_output_file('output.raw')


client = pyrogram.Client('session', 'app_id', 'app_hash', ipv6=True)
client.add_handler(RawUpdateHandler(process_raw_update))
key_handler = AuthKeyHandler(client)


def receive_call_test():
    client.start()
    client.add_handler(RawUpdateHandler(accept_call), 1)
    client.idle()


def send_call_test():
    client.start()
    call = key_handler.request_call('@bakatrouble')
    call.play('input.raw')
    call.play_on_hold(['input.raw'])
    call.set_output_file('output.raw')

    while call.get_call_state() < VoIP.CALL_STATE_ENDED:
        sleep(1)

    client.stop()


if __name__ == '__main__':
    # Check documentation here: https://docs.madelineproto.xyz/docs/CALLS.html
    # Audio conversion:
    # ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw
    # ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3

    receive_call_test()
    # send_call_test()
