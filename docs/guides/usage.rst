Usage
=====


Common
------
* You should have a protocol object: ``phoneCallProtocol(min_layer=65, max_layer=VoIPController.CONNECTION_MAX_LAYER, udp_p2p=True, udp_reflector=True)``
* All VoIP-related updates have type of ``updatePhoneCall`` with ``phone_call`` field of types ``phoneCallEmpty``, ``phoneCallWaiting``, ``phoneCallRequested``, ``phoneCallAccepted``, ``phoneCall`` or ``phoneCallDiscarded``
* Use :meth:`tgvoip.utils.generate_visualization` with ``auth_key`` and ``g_a`` for outgoing or ``g_a_or_b`` for incoming calls to get emojis if you need them


Starting conversation
---------------------
* Create a :class:`VoIPController` instance
* Call :meth:`tgvoip.VoIPController.set_send_audio_frame_callback` (see docs for arguments) if needed, otherwise silence will be sent
* Call :meth:`tgvoip.VoIPController.set_recv_audio_frame_callback` (see docs for arguments) if needed, otherwise nothing will be done to incoming audio stream
* Add state change handlers to :attr:`tgvoip.VoIPController.call_state_changed_handlers` (see docs for handler format) list if needed
* Add signal bars change handlers to :attr:`tgvoip.VoIPController.signal_bars_changed_handlers` (see docs for handler format) list if needed
* Invoke ``help.getConfig()`` (result is later referred as ``config``)
* Call :meth:`tgvoip.VoIPController.set_config` (arguments are: ``config.call_packet_timeout_ms / 1000., config.call_connect_timeout_ms / 1000., DataSaving.NEVER, call.id``)
* Call :meth:`tgvoip.VoIPController.set_encryption_key` (arguments are: ``i2b(auth_key), is_outgoing`` where ``is_outgoing`` is a corresponding boolean value)
* Build a ``list`` of :class:`tgvoip.Endpoint` objects from ``call.connection`` (single) and ``call.alternative_connections`` (another list)
* Call :meth:`tgvoip.VoIPController.set_remote_endpoints` (arguments are: ``endpoints, call.p2p_allowed, False, call.protocol.max_layer``)
* Call :meth:`tgvoip.VoIPController.start`
* Call :meth:`tgvoip.VoIPController.connect`


Discarding call
---------------
* Build ``peer``: ``inputPhoneCall(id=call.id, access_hash=call.access_hash)``
* Get call duration using :attr:`tgvoip.VoIPController.call_duration`
* Get connection ID using :meth:`tgvoip.VoIPController.get_preferred_relay_id`
* Build a suitable ``reason`` object (types are: ``phoneCallDiscardReasonBusy``, ``phoneCallDiscardReasonDisconnect``, ``phoneCallDiscardReasonHangup``, ``phoneCallDiscardReasonMissed``)
* Invoke ``phone.discardCall(peer, duration, connection_id, reason)``. You might get ``CALL_ALREADY_DECLINED`` error, this is fine
* Destroy the :class:`tgvoip.VoIPController` object


Ending conversation
-------------------
* Send call rating and debug log if call ended normally (not failed): `TBD`
* Destroy the :class:`tgvoip.VoIPController` object, everything will be done automatically


Making outgoing calls
---------------------
* Get a ``user_id`` object for user you want to call (of type ``inputPeerUser``)
* Request a Diffie-Hellman config using ``messages.getDhConfig(version=0, random_length=256)``
* Check received config using :meth:`tgvoip.utils.check_dhc`. If check is not passed, do not make the call. You might want to cache received config because check is expensive
* Choose a random value ``a``, ``1 < a < dhc.p-1``
* Calculate ``g_a``: ``pow(dhc.g, a, dhc.p)``
* Calculate ``g_a_hash``: ``sha256(g_a)``
* Choose a random value ``random_id``, ``0 <= random_id <= 0x7fffffff-1``
* Invoke ``phone.requestCall(user_id, random_id, g_a_hash, protocol)``
* Wait for an update with ``phoneCallAccepted`` object, it means that other party has accepted the call. You also might get a ``phoneCallDiscarded`` object, it means that other party has declined the call
* If you have got a ``phoneCallDiscarded`` object, stop the :class:`tgvoip.VoIPController`. Otherwise, continue
* Check a ``g_b`` value from received ``phoneCallAccepted`` (later referred as ``call``) object using :meth:`tgvoip.utils.check_g`. If check is not passed, stop the call
* Calculate ``auth_key``: ``pow(call.g_b, a, dhc.p)``
* Calculate ``key_fingerprint`` using :meth:`tgvoip.utils.calc_fingerprint`
* Build ``peer``: ``inputPhoneCall(id=call.id, access_hash=call.access_hash)``
* Invoke ``phone.confirmCall(key_fingerprint, peer, g_a, protocol)``
* Start the conversation


Receiving calls
---------------
* You will receive an update containing ``phoneCallRequested`` object (later referred as ``call``). You might discard it right away (use ``0`` for duration and connection_id)
* Request a Diffie-Hellman config using ``messages.getDhConfig(version=0, random_length=256)``
* Check received config using :meth:`tgvoip.utils.check_dhc`. If check is not passed, do not make the call. You might want to cache received config because check is expensive
* Choose a random value ``b``, ``1 < b < dhc.p-1``
* Calculate ``g_b``: ``pow(dhc.g, b, dhc.p)``
* Save ``call.g_a_hash``
* Build ``peer``: ``inputPhoneCall(id=call.id, access_hash=call.access_hash)``
* Invoke ``phone.acceptCall(peer, g_b, protocol)``. You might get ``CALL_ALREADY_DISCARDED`` or ``CALL_ALREADY_ACCEPTED`` errors, then you should stop current conversation. Also, if response contains ``phoneCallDiscarded`` object you should stop the call
* Wait for an update with ``phoneCall`` object (later referred as ``call``)
* Check that ``call.g_a_or_b`` is not empty and ``sha256(call.g_a_or_b)`` equals to ``g_a_hash`` you saved before. If it doesn't match, stop the call
* Check a ``call.g_a_or_b`` value object using :meth:`tgvoip.utils.check_g` (second argument is ``dhc.p``). If check is not passed, stop the call
* Calculate ``auth_key``: ``pow(call.g_a_or_b, b, dhc.p)``
* Calculate ``key_fingerprint`` using :meth:`tgvoip.utils.calc_fingerprint`
* Check that ``key_fingerprint`` you have just calculated matches ``call.key_fingerprint``. If it doesn't match, stop the call
* Start the conversation

