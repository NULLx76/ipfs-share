# ipfs-share
A utility to make sharing files over IPFS more convenient by generating gateway urls, pinning the CID to a remote node 
and copying the url to your clipboard.

### Usage
```shell
usage: ipfs_share.py [-h] [-nc] [-p] [-g URL] [-r URL] [-t {node,cluster}] path

Share a file using IPFS

positional arguments:
  path                  the file or folder to share

optional arguments:
  -h, --help            show this help message and exit
  -nc, --no-clipboard   disable clipboard support
  -p, --pin             Pin file/folder to a remote pinner
  -g URL, --gateway URL
                        gateway(s) to use for url generation (repetition allowed). You can also use the 'IPFS_GATEWAYS' environment variable
  -r URL, --remote-pinner-url URL
                        Url of a remote pinner. You can also use the 'IPFS_REMOTE_PINNER' environment variable. Required when using '--pin'
  -t {node,cluster}, --pinner-type {node,cluster}
                        Remote pinner type to use. You can also use the 'IPFS_REMOTE_PINNER_TYPE' environment variable. Defaults to node
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
* `ipfs` binary in your path
* `python-requests` for sending http requests
* (optional) `tk` for clipboard support