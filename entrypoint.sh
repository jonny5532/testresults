#!/bin/sh

# workaround alpine DNS issues...
echo "nameserver 8.8.8.8" > /etc/resolv.conf

python3 /main.py "$@"
