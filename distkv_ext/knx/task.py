"""
KNX task for DistKV
"""

import anyio
import xknx
from xknx.io import ConnectionConfig, ConnectionType
import socket

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from distkv.util import combine_dict, NotGiven, attrdict
from distkv.exceptions import ClientConnectionError
from distkv_ext.knx.model import KNXroot, KNXserver

import logging
logger = logging.getLogger(__name__)

async def task(client, cfg, server: KNXserver, evt=None, local_ip=None):
    cfg = combine_dict(server.value_or({}, Mapping), cfg['server_default'])
    add = {}
    if local_ip is not None:
        add['local_ip'] = local_ip

    try:
        ccfg=ConnectionConfig(connection_type=ConnectionType.TUNNELING,
            gateway_ip=cfg['host'],
            gateway_port=cfg.get('port', 3671),
            **add
        )
        async with xknx.XKNX().run(connection_config=ccfg) as srv:
            await server.set_server(srv)
            if evt is not None:
                await evt.set()

            while True:
                await anyio.sleep(99999)
    except TimeoutError:
        raise
    except socket.error as e:  # this would eat TimeoutError
        raise ClientConnectionError(cfg['host'], cfg['port']) from e

