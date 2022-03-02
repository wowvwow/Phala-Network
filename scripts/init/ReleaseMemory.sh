#!/bin/bash

sync
sync
sync

# to free reclaimable slab objects (includes dentries and inodes)
echo 2 > /proc/sys/vm/drop_caches
# to free slab objects and pagecache
echo 3 > /proc/sys/vm/drop_caches
# to free pagecache
echo 1 > /proc/sys/vm/drop_caches
