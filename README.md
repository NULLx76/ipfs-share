# ipfs-share
A utility to make sharing files over IPFS more convenient by generating gateway urls, pinning the CID to a remote node 
and copying the url to your clipboard.

### Usage
```shell
usage: ipfs-share [-h] [-p] [--no-clipboard] path

Share a file using IPFS

positional arguments:
  path            The file or folder to share

optional arguments:
  -h, --help      show this help message and exit
  -p, --pin       Pin target to a remote node or cluster
  --no-clipboard  Disable clipboard support

Environment:
  IPFS_GATEWAYS              A list of IPFS Gateway URLs to be used for generating urls
  IPFS_REMOTE_PINNER_TYPE    Either 'node' or 'cluster' depending on what remote pinner you want to use
  IPFS_REMOTE_PINNER_URL     The URL for a remote pinner
```

### Example
```shell
> ipfs_share index.html

CID: QmTeLU7tgi82xU9Hmmp4GwTV11XDPF6Ts5qvCciPNKhs3r
https://cloudflare-ipfs.com/ipfs/QmTeLU7tgi82xU9Hmmp4GwTV11XDPF6Ts5qvCciPNKhs3r/index.html
https://ipfs.xirion.net/ipfs/QmTeLU7tgi82xU9Hmmp4GwTV11XDPF6Ts5qvCciPNKhs3r/index.html
```


### Requirements
* `python` version 3.9 (untested on older versions)
* `python-requests` for sending http requests
* (optional) `tk` for clipboard support
