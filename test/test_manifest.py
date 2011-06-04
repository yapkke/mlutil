#!/usr/bin/env python
import yapc.core as core
import yapc.log.output as output
import mlutil.cache as mc
import mlutil.googlestorage as gs
import simplejson

output.set_mode("DBG")
server = core.core()
config = mc.config()
m = gs.manifest(server,config)

m.add_file("glasnot/testing 1234.tgz")
m.add_file("glasnot/testing 5678.tgz")
m.add_file("glasnot/bak/testing 1234.tgz")
m.add_file("glasnot/bak2/testing 1234.tgz")
m.add_file("glasnot/testing 1234.tgz")

for f in m.get_all_files():
    output.dbg(str(f))
output.dbg(str(m.files))
output.dbg(str(m.get_files()))
for name, d in m.get_dirs().items():
    output.dbg(str(m.get_files(d)))
    output.dbg(str(m.get_dir_names(d)))
    output.dbg(str(m.get_dirs(d)))
