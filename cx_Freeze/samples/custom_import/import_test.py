# Code to test imports that rely on custom finder/loader to load the module into python
#  - package q1 loads a customer finder/loader (from customerFinder.py) which will redirect imports of
#    q1.q2.q and q1.q4.q to the file at q1/q3/q.py
#  - package r


print("import_test: Doing imports")
import q1.q4.q
q1.q4.q.doStuff_q()

import r1.r2.r3a.r
r1.r2.r3a.r.doStuff_r()
