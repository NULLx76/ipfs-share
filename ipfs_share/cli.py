import os
import sys
import argparse
from urllib.parse import urlparse

from .pinner import RemotePinner, RemotePinnerType
from .ipfs_share import ShareOptions, ipfs_share

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
    gateways = [url_t(x) for x in env_gateways.split()] if (env_gateways := os.environ.get("IPFS_GATEWAYS")) is not None else None
    remote_pinner_url = url_t(env_remote_pinner) if (env_remote_pinner := os.environ.get("IPFS_REMOTE_PINNER")) is not None else None
    pinner_type = RemotePinnerType(env_pinner_type) if (env_pinner_type := os.environ.get("IPFS_REMOTE_PINNER_TYPE")) is not None else RemotePinnerType.Node

    parser = argparse.ArgumentParser(description="Share a file using IPFS")
    parser.add_argument("path", type=path_t, help="the file or folder to share")
    parser.add_argument("--no-clipboard", action="store_true", help="disable clipboard support")
    parser.add_argument("--nocopy", action="store_true", help="Use the experimental ipfs 'no copy' feature")

    parser.add_argument("-p", "--pin", action="store_true", help="Pin file/folder to a remote pinner")

    parser.add_argument("-g", "--gateway", metavar="URL", action="append", type=url_t, default=gateways,
                        help="gateway(s) to use for url generation (repetition allowed). You can also use the 'IPFS_GATEWAYS' environment variable")

    parser.add_argument("-r", "--remote-pinner-url", metavar="URL", type=url_t, default=remote_pinner_url,
                        required="-p" in sys.argv and remote_pinner_url is None,
                        help="Url of a remote pinner. You can also use the 'IPFS_REMOTE_PINNER' environment variable. Required when using '--pin'")

    parser.add_argument("-t", "--pinner-type", type=RemotePinnerType, default=pinner_type, choices=list(RemotePinnerType),
                        help="Remote pinner type to use. You can also use the 'IPFS_REMOTE_PINNER_TYPE' environment variable. Defaults to node")

    args = parser.parse_args()

    pinner = RemotePinner.from_type(args.pinner_type, args.remote_pinner_url)
    ipfs_share(ShareOptions(args.path, not args.no_clipboard, args.gateway or GATEWAYS, args.pin, pinner, args.nocopy))


if __name__ == "__main__":
    main()
