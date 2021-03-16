#!/usr/bin/env python3
import subprocess
import os

from .pinner import RemotePinner

from dataclasses import dataclass
from shutil import which
from typing import Tuple, List
from urllib.parse import urljoin

# Try importing Tk for clipboard support
try:
    from tkinter import Tk
except ImportError:
    Tk = None


@dataclass
class ShareOptions:
    target: str
    enable_clipboard: bool
    gateways: List[str]
    pin: bool
    pinner: RemotePinner
    no_copy: bool


# Upload file to ipfs
def upload_file(file: str, ipfs: str, no_copy: bool) -> Tuple[str, str]:
    # ipfs subcommand
    # -w: Wrap, wraps the file in a folder, allows linking to the filename
    # -q: Quiet, gives better parsable output
    cmd = [ipfs, "add", "-wq", file]
    if no_copy:
        cmd.insert(3, "--nocopy")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    file_name = os.path.basename(file)

    return str(folder_hash), f"{folder_hash}/{file_name}"


# Upload folder to ipfs, returns (folder_cid, file_cid)
def upload_folder(path: str, ipfs: str, no_copy: bool) -> str:
    # ipfs subcommand
    # -r: Recursive, required for folders
    # -q: Quiet, gives better parsable output
    cmd = [ipfs, "add", "-rq", path]
    if no_copy:
        cmd.insert(3, "--nocopy")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    return str(folder_hash)


# Upload folder or file to ipfs, returns (folder_cid, file_cid)
def upload(path: str, ipfs: str = "ipfs", no_copy: bool = False) -> Tuple[str, str]:
    if os.path.isdir(path):
        cid = upload_folder(path, ipfs, no_copy)
        return cid, cid
    elif os.path.isfile(path):
        return upload_file(path, ipfs, no_copy)
    else:
        raise ValueError(f"{path} is an invalid path to file or dir")


def copy_to_clipboard(string: str):
    if Tk is not None:
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(string)
        r.update()
        r.destroy()


def ipfs_share(options: ShareOptions):
    if (ipfs := which("ipfs")) is None:
        raise Exception("ipfs binary could not be found")

    folder_cid, file_cid = upload(options.target, ipfs)

    if options.pin:
        options.pinner.pin(folder_cid)

    urls = [urljoin(g, f"ipfs/{file_cid}") for g in options.gateways]

    if options.enable_clipboard:
        copy_to_clipboard(urls[-1])

    print(f"CID: {folder_cid}")
    for el in urls:
        print(el)
