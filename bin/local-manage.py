import os
import sys

possible_topdir = os.path.normpath(os.path.join(
    os.path.abspath(sys.argv[0]), os.pardir, os.pardir)
)

if os.path.exists(os.path.join(possible_topdir, 'cruton', 'data_store', 'main.py')):
    sys.path.insert(0, possible_topdir)

import cruton.data_store.main as dm
dm.main()
