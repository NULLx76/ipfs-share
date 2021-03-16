from __future__ import annotations

import requests
from enum import Enum
from urllib.parse import urljoin
from abc import ABC
from typing import Union


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
    url: str

    def pin(self, cid: str) -> None:
        res = requests.post(urljoin(self.url, f"/api/v0/pin/add?arg={cid}"))
        if res.status_code != 200:
            raise Exception(f"Failed remote pin: {res.text}")

    def __init__(self, url: str):
        self.url = url


class ClusterAPI(RemotePinner):
    url: str

    def pin(self, cid: str) -> None:
        raise NotImplementedError

    def __init__(self, url: str):
        self.url = url
