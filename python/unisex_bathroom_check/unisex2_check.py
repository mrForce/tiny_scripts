from unisex_check import *
import sys
s = 3
m = 15
f = 10
def dump(state):
    print(state.waiting)
    print(state.bathroom)
    print(state.exited)
state = StateTracker()
for line in sys.stdin:
    action, person = state.next(line)
    if not unisex_constraint(state.waiting, state.bathroom):
        print('unisex constraint violated')
        print(line)
        dump(state)
        
        sys.exit()
    if not stall_constraint(state.waiting, state.bathroom, s):
        print('stall constraint violated')
        print(line)
        dump(state)
        
        sys.exit()
    if not priority_constraint(state.waiting, state.bathroom, (action, person)):
        print('priority constraint violated')
        print(line)
        dump(state)
        
        sys.exit()
""""
if len(state.waiting) > 0:
    print('people still waiting')
    dump(state)
    sys.exit()
if len(state.bathroom) > 0:
    print('people still in bathroom')
    dump(state)
    sys.exit()
if not end_exit_constraint(state.exited, m, f):
    print('end constraint violated')
    dump(state)
    sys.exit()
"""
