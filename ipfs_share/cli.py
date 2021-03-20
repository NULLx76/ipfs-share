import os
import argparse
from urllib.parse import urlparse

from ipfs_share.ipfs_share import ipfs_share
from ipfs_share.pinner import RemotePinner, RemotePinnerType

GATEWAYS = ["https://cloudflare-ipfs.com", "https://ipfs.xirion.net"]


def path_t(path: str) -> str:
    """Checker for argparse to verify that the path exists"""
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path to a file or dir")


def url_t(url: str) -> str:
    """Checker for argparse to validate urls"""
    parsed = urlparse(url)
    if all([parsed.scheme, parsed.netloc]):
        return parsed.geturl()
    else:
        raise argparse.ArgumentTypeError(f"{url} is not a valid url")


def main():
    env_help = """
Environment:
  IPFS_GATEWAYS              A list of IPFS Gateway URLs to be used for generating urls
  IPFS_REMOTE_PINNER_TYPE    Either 'node' or 'cluster' depending on what remote pinner you want to use
  IPFS_REMOTE_PINNER_URL     The URL for a remote pinner
"""

    gateways = [url_t(x) for x in eg.split()] if (eg := os.environ.get("IPFS_GATEWAYS")) else GATEWAYS
    pinner_type = RemotePinnerType(ept) if (ept := os.environ.get("IPFS_REMOTE_PINNER_TYPE")) else RemotePinnerType.Node
    remote_pinner_url = url_t(erp) if (erp := os.environ.get("IPFS_REMOTE_PINNER_URL")) else None

    parser = argparse.ArgumentParser(description="Share a file using IPFS", epilog=env_help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=path_t, help="The file or folder to share")
    parser.add_argument("-p", "--pin", action="store_true", help="Pin target to a remote node or cluster")
    parser.add_argument("--no-clipboard", action="store_true", help="Disable clipboard support")

    args = parser.parse_args()

    if args.pin and remote_pinner_url is None:
        raise ValueError("Can't pin without IPFS_REMOTE_PINNER_URL")

    pinner = RemotePinner.from_type(pinner_type, remote_pinner_url) if remote_pinner_url is not None else None
    ipfs_share(args.path, not args.no_clipboard, gateways, pinner)


if __name__ == "__main__":
    main()
