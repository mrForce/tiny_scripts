"""
This is for checking the correctness of the unisex bathroom program output.
"""
from enum import Enum
import re
class Sex(Enum):
    MALE = 1
    FEMALE = 2

class Action(Enum):
    ENTER = 1
    LEAVE = 2
    WAIT = 3





class StateTracker:

    def __init__(self):
        self.regex = re.compile('(?P<sex>male|female)\s+#(?P<number>\d+)\s+(?P<action>enters|exits|waits)')
        self.waiting = set()
        self.bathroom = set()
        self.exited = []
    def next(self, line):
        #returns a tuple of the form (Action, Sex)
        parsed = self.regex.match(line)
        sex = parsed.group('sex')
        action = parsed.group('action')
        num = int(parsed.group('number'))
        sex_enum = None
        action_enum = None
        if sex == 'male':
            sex_enum = Sex.MALE
        elif sex == 'female':
            sex_enum = Sex.FEMALE
        person = (sex_enum, num)
        if action == 'waits':
            action_enum = Action.WAIT
            self.waiting.add(person)
        elif action == 'exits':
            action_enum = Action.LEAVE
            self.bathroom.remove(person)
            self.exited.append(person)
        elif action == 'enters':
            action_enum = Action.ENTER
            if person in self.waiting:
                self.waiting.remove(person)
            self.bathroom.add(person)
        assert(sex_enum)
        assert(action_enum)
        
        return (action_enum, person)
    
def unisex_constraint(waiting, bathroom):
    return len(set([x[0] for x in bathroom])) < 2

def stall_constraint(waiting, bathroom, s):
    return len(bathroom) <= s

def priority_constraint(waiting, bathroom, next_return):
    action = next_return[0]
    sex = next_return[1][0]
    if action == Action.ENTER:
        if sex == Sex.MALE and Sex.FEMALE in [x[0] for x in waiting]:
            return False
    return True

def end_exit_constraint(exited, num_males, num_females):
    return len(list(filter(lambda x: x == Sex.MALE, [x[0] for x in exited]))) == num_males and len(list(filter(lambda x: x == Sex.FEMALE, [x[0] for x in exited]))) == num_females

