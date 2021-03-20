from __future__ import annotations

import requests
from enum import Enum
from urllib.parse import urljoin
from abc import ABC
from typing import Union
from ipfs_share import ipfshttpclient as ipfs


class RemotePinnerType(Enum):
    Node = "node"
    Cluster = "cluster"

    def __str__(self):
        return self.value


class RemotePinner(ABC):
    def pin(self, cid: str) -> None:
        pass

    @staticmethod
    def from_type(kind: RemotePinnerType, host: str) -> Union[NodeAPI, ClusterAPI]:
        if kind is RemotePinnerType.Node:
            return NodeAPI(host)
        elif kind is RemotePinnerType.Cluster:
            return ClusterAPI(host)
        else:
            raise ValueError(f"Invalid RemotePinnerType: {kind}")


class NodeAPI(RemotePinner):
    def __init__(self, addr: str):
        self._client = ipfs.connect(addr=addr)

    def pin(self, cid: str) -> None:
        self._client.pin.add(cid)


class ClusterAPI(RemotePinner):
    def __init__(self, addr: str):
        self._addr = addr

    def pin(self, cid: str) -> None:
        raise NotImplementedError
