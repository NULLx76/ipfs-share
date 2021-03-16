#!/usr/bin/env python3
import subprocess
import os
import argparse
import requests
import sys
from shutil import which
from typing import List, Tuple
from urllib.parse import urlparse, urljoin
from enum import Enum

# Try importing Tk for clipboard support
try:
    from tkinter import Tk
except ImportError:
    Tk = None

# Default gateways to generate links for
GATEWAYS = ["https://cloudflare-ipfs.com", "https://ipfs.xirion.net"]


# Types of supported remote pinning APIs
class RemotePinner(Enum):
    Node = "node"
    Cluster = "cluster"

    def __str__(self):
        return self.value


# Checker for argparse to verify that the path exists
def path_t(path: str) -> str:
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"{path} is not a valid path to a file or dir")


# Checker for argparse to validate urls
def url_t(url: str) -> str:
    parsed = urlparse(url)
    if all([parsed.scheme, parsed.netloc]):
        return parsed.geturl()
    else:
        raise argparse.ArgumentTypeError(f"{url} is not a valid url")


# Upload file to ipfs
def upload_file(file: str, ipfs: str) -> Tuple[str, str]:
    # ipfs subcommand
    # -w: Wrap, wraps the file in a folder, allows linking to the filename
    # -q: Quiet, gives better parsable output
    result = subprocess.run([ipfs, "add", "-wq", file],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    file_name = os.path.basename(file)

    return folder_hash, f"{folder_hash}/{file_name}"


# Upload folder to ipfs, returns (folder_cid, file_cid)
def upload_folder(path: str, ipfs: str) -> str:
    # ipfs subcommand
    # -r: Recursive, required for folders
    # -q: Quiet, gives better parsable output
    result = subprocess.run([ipfs, "add", "-rq", path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    return folder_hash


# Upload folder or file to ipfs, returns (folder_cid, file_cid)
def upload(path: str, ipfs: str = "ipfs") -> Tuple[str, str]:
    if os.path.isdir(path):
        cid = upload_folder(path, ipfs)
        return cid, cid
    elif os.path.isfile(path):
        return upload_file(path, ipfs)
    else:
        raise ValueError(f"{path} is an invalid path to file or dir")


def remote_pin(pinner: RemotePinner, host: str, cid: str):
    if pinner is RemotePinner.Node:
        # curl -X POST "http://ipfs-node:5001/api/v0/pin/add?arg={cid}"
        res = requests.post(urljoin(host, f"/api/v0/pin/add?arg={cid}"))
        if res.status_code != 200:
            raise Exception(f"Failed remote pin: {res.text}")

    elif pinner is RemotePinner.Cluster:
        raise Exception("Pinning to a IPFS Cluster is not yet supported")
    else:
        raise ValueError(f"Unknown remote pinner {pinner}")


def copy_to_clipboard(string: str):
    if Tk is not None:
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(string)
        r.update()
        r.destroy()


def ipfs_share(target: str, clipboard: bool, gw: List[str], pin: bool, pinner: RemotePinner, pinner_url: str):
    if (ipfs := which("ipfs")) is None:
        raise Exception("ipfs binary could not be found")

    folder_cid, file_cid = upload(target, ipfs)

    if pin: 
        remote_pin(pinner, pinner_url, folder_cid)

    urls = [urljoin(g, f"ipfs/{file_cid}") for g in gw]

    if clipboard:
        copy_to_clipboard(urls[-1])

    print(f"CID: {folder_cid}")
    for el in urls:
        print(el)


if __name__ == "__main__":
    gateways = [url_t(x) for x in env_gateways.split()] if (env_gateways := os.environ.get("IPFS_GATEWAYS")) is not None else None
    remote_pinner_url = url_t(env_remote_pinner) if (env_remote_pinner := os.environ.get("IPFS_REMOTE_PINNER")) is not None else None
    pinner_type = RemotePinner(env_pinner_type) if (env_pinner_type := os.environ.get("IPFS_REMOTE_PINNER_TYPE")) is not None else RemotePinner.Node

    parser = argparse.ArgumentParser(description="Share a file using IPFS")
    parser.add_argument("path", type=path_t, help="the file or folder to share")
    parser.add_argument("-nc", "--no-clipboard", action="store_true", help="disable clipboard support")
    parser.add_argument("-p", "--pin", action="store_true", help="Pin file/folder to a remote pinner")

    parser.add_argument("-g", "--gateway", metavar="URL", action="append", type=url_t, default=gateways,
                        help="gateway(s) to use for url generation (repetition allowed). You can also use the 'IPFS_GATEWAYS' environment variable")
    
    parser.add_argument("-r", "--remote-pinner-url", metavar="URL", type=url_t, default=remote_pinner_url, required="-p" in sys.argv and remote_pinner_url is None,
                        help="Url of a remote pinner. You can also use the 'IPFS_REMOTE_PINNER' environment variable. Required when using '--pin'")
    
    parser.add_argument("-t", "--pinner-type", type=RemotePinner, default=pinner_type, choices=list(RemotePinner),
                        help="Remote pinner type to use. You can also use the 'IPFS_REMOTE_PINNER_TYPE' environment variable. Defaults to node")

    args = parser.parse_args()

    ipfs_share(args.path, not args.no_clipboard, args.gateway or GATEWAYS, args.pin, args.pinner_type, args.remote_pinner_url)
