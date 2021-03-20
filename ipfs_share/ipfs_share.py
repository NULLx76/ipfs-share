from __future__ import annotations

import os
from urllib.parse import urljoin
from typing import Optional

from ipfs_share import ipfshttpclient as ipfs
from ipfs_share.clipboard import copy_to_clipboard
from ipfs_share.pinner import RemotePinner

BASE_FOLDER = "/ipfs-share"


class IpfsShare:
    def __init__(self, addr: str = ipfs.DEFAULT_ADDR, base_folder: Optional[str] = None):
        self._client = ipfs.connect(addr=addr)
        self._base_folder = base_folder if base_folder else BASE_FOLDER

    def __enter__(self) -> IpfsShare:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._client.close()

    def root_cid(self):
        self._client.files.mkdir(self._base_folder, parents=True)
        return self._client.files.stat(self._base_folder)['Hash']

    def add(self, path: str) -> str:
        if os.path.isfile(path):
            return self.add_file(path)
        elif os.path.isdir(path):
            return self.add_folder(path)
        else:
            raise ValueError("Path must be a file or folder")

    def add_file(self, path: str) -> str:
        if not os.path.isfile(path):
            raise ValueError("Path must be a file")

        filename = os.path.basename(path)
        mfs_path = os.path.join(BASE_FOLDER, filename)
        self._client.files.mkdir(os.path.split(mfs_path)[0], parents=True)

        with open(os.path.abspath(path), "rb") as f:
            self._client.files.write(mfs_path, f, create=True)

        return f"{self.root_cid()}/{filename}"

    def add_folder(self, path: str) -> str:
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")

        abs_path = os.path.abspath(path)
        prefix = os.sep.join(abs_path.split(os.sep)[:-1])

        for dirpath, _, filenames in os.walk(abs_path):
            for file in filenames:
                path = os.path.join(dirpath, file)
                mfs_path = BASE_FOLDER + path.removeprefix(prefix)
                self._client.files.mkdir(os.path.dirname(mfs_path), parents=True)
                with open(path, "rb") as f:
                    self._client.files.write(mfs_path, f, create=True)

        return f"{self.root_cid()}/{abs_path.split(os.sep)[-1]}"


def ipfs_share(path: str, clipboard: bool, gateways: [str], remote_pinner: Optional[RemotePinner] = None):
    with IpfsShare() as share:
        cid = share.add(path)

    if remote_pinner is not None:
        remote_pinner.pin(cid)

    urls = [urljoin(g, f"ipfs/{cid}") for g in gateways]
    if clipboard:
        copy_to_clipboard(urls[-1])

    print(f"CID: {cid}")
    for url in urls:
        print(url)
