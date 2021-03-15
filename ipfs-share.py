#!/usr/bin/env python3
import subprocess
import os
import argparse
from typing import List

gateways = ["https://ipfs.xirion.net", "https://cloudflare-ipfs.com"]

# Checker for argparse to verify that the path exists
def path(path: str) -> str:
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path to a file or dir")

# Upload file to ipfs
def upload_file(path: str) -> str:
    # ipfs subcommand
    # -w: Wrap, wraps the file in a folder, allows linking to the filename
    # -q: Quiet, gives better parsable output
    result = subprocess.run(["ipfs", "add", "-wq", path], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    file_name = os.path.basename(path)

    return f"{folder_hash}/{file_name}"

# Upload folder to ipfs
def upload_folder(path: str) -> str:
    # ipfs subcommand
    # -r: Recursive, required for folders
    # -q: Quiet, gives better parsable output
    result = subprocess.run(["ipfs", "add", "-rq", path], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"ipfs command failed:\n\n{result.stderr}")

    folder_hash = result.stdout.splitlines()[-1]
    return folder_hash

# Upload folder or file to ipfs
def upload(path: str) -> str:
    if os.path.isdir(path):
        return upload_folder(path)
    elif os.path.isfile(path):
        return upload_file(path)
    else:
        raise ValueError(f"{path} is an invalid path to file or dir")

def format_urls(cid: str, gateways: List[str]) -> List[str]:
    return [f"{g}/ipfs/{cid}" for g in gateways]

def main(path: str):
    cid = upload(path)
    urls = format_urls(cid, gateways)
    print("Uploaded file succesfully, urls:")
    # TODO: Copy to clipboard
    for url in urls:
        print(url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Share a file using IPFS')
    parser.add_argument('path', type=path, help='The file or folder to share')
    # TODO: Custom gateway
    # TODO: Remote pinning
    args = parser.parse_args()

    main(args.path)
