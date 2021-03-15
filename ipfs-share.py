#!/usr/bin/env python3
import subprocess
import os
import argparse
from shutil import which
from typing import List
from urllib.parse import ParseResult, urlparse, urljoin

try:
    from tkinter import Tk
except:
    Tk = None

# TODO: Custom gateway
GATEWAYS = ["https://cloudflare-ipfs.com", "https://ipfs.xirion.net"]


# Checker for argparse to verify that the path exists
def path(path: str) -> str:
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"{path} is not a valid path to a file or dir")


def url(url: str):
    parsed = urlparse(url)
    if all([parsed.scheme, parsed.netloc]):
        return parsed.geturl()
    else:
        raise argparse.ArgumentTypeError(f"{url} is not a valid url")


# Upload file to ipfs
def upload_file(path: str, ipfs: str) -> str:
    # ipfs subcommand
    # -w: Wrap, wraps the file in a folder, allows linking to the filename
    # -q: Quiet, gives better parsable output
    result = subprocess.run([ipfs, "add", "-wq", path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    file_name = os.path.basename(path)

    return f"{folder_hash}/{file_name}"


# Upload folder to ipfs
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


# Upload folder or file to ipfs
def upload(path: str, ipfs: str = "ipfs") -> str:
    if os.path.isdir(path):
        return upload_folder(path, ipfs)
    elif os.path.isfile(path):
        return upload_file(path, ipfs)
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


def main(path: str, clipboard: bool, gateways: List[str]):
    if (ipfs := which("ipfs")) is None:
        raise Exception("ipfs binary could not be found")

    # TODO: Remote pinning
    cid = upload(path, ipfs)
    urls = [urljoin(g, f"ipfs/{cid}") for g in gateways]

    if clipboard:
        copy_to_clipboard(urls[-1])

    print(f"CID: {cid}")
    for url in urls:
        print(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Share a file using IPFS')
    parser.add_argument('path', type=path, help='the file or folder to share')
    parser.add_argument('-g', '--gateway', action="append",
                        type=url, help="gateway(s) to use for url generation (repitition allowed)")
    parser.add_argument('-nc', '--no-clipboard',
                        action="store_true", help='disable clipboard support')

    args = parser.parse_args()

    main(args.path, not args.no_clipboard, args.gateway or GATEWAYS)
