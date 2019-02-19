libtgvoip wrapper
=================

.. module:: tgvoip.tgvoip


VoIPController
--------------

.. autoclass:: tgvoip.VoIPController
    :members:


VoIPServerConfig
----------------

.. autoclass:: tgvoip.VoIPServerConfig
    :members:


Enums
-----

.. autoclass:: tgvoip.NetType
    :members:

.. autoclass:: tgvoip.DataSaving
    :members:

.. autoclass:: tgvoip.CallState
    :members:

.. autoclass:: tgvoip.CallError
    :members:


Data structures
---------------


.. py:class:: tgvoip.Stats

    Object storing call stats

    .. attribute:: bytes_sent_wifi

       Amount of data sent over WiFi
       :type: ``int``

    .. attribute:: bytes_sent_mobile

       Amount of data sent over mobile network
       :type: ``int``

    .. attribute:: bytes_recvd_wifi

       Amount of data received over WiFi
       :type: ``int``

    .. attribute:: bytes_recvd_mobile

       Amount of data received over mobile network
       :type: ``int``


.. py:class:: tgvoip.Endpoint

    Object storing endpoint info

    :param _id: Endpoint ID
    :type _id: ``int``
    :param ip: Endpoint IPv4 address
    :type ip: ``str``
    :param ipv6: Endpoint IPv6 address
    :type ipv6: ``str``
    :param port: Endpoint port
    :type port: ``int``
    :param peer_tag: Endpoint peer tag
    :type peer_tag: ``bytes``
