#!/usr/bin/env python
import yapc.core as core
import yapc.log.output as output
import yapc.util.memcacheutil as mcutil

import mlutil.cache as mc
import mlutil.base as base

import simplejson

output.set_mode("DBG")
mcutil.memcache_mode = mcutil.MEMCACHE_MODE["LOCAL"]
m = base.manifest("testing1")

m.add_file("testing 1234.tgz", "glasnot/")
m.add_file("glasnot/testing 5678.tgz")
m.add_file("glasnot/bak/testing 1234.tgz")
m.add_file("glasnot/bak2/testing 1234.tgz")
m.add_file("glasnot/testing 1234.tgz") #Duplicate
m.add_file("ndt/testing 1234.tgz") #Different dir

output.dbg(str(m.get_dirs()))
output.dbg(str(m.get_files()))
output.dbg(str(m.get_dirs("glasnot/")))
output.dbg(str(m.get_files("glasnot/")))
output.dbg("")
for f in m.get_all_files():
    output.dbg(str(f))
output.dbg(str(m))
m.save_file("testing.manifest")

n = base.manifest("testing2")
n.load_file("testing.manifest")
output.dbg(str(n))
for f in n.get_all_files():
    output.dbg(str(f))

output.dbg(n.delete_file("glasnot/bak/testing 12345.tgz"))
output.dbg(n.delete_file("glasnot/bak/testing 1234.tgz"))
output.dbg(str(n))

n.delete_dir("glasnot/")
output.dbg(str(n))

n.clear()
output.dbg(str(n))
