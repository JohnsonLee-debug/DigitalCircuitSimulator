import sys

INVERT_DELAY = 2
AND_GATE_DELAY = 3
OR_GATE_DELAY = 5
XOR_GATE_DELAY = 8


class Agenda(object):
    """
    structure of segment: (time, [procedures...])
    """
    segments: list
    current_time: int

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Agenda, "_instance"):
            Agenda._instance = object.__new__(cls)
            Agenda.current_time = 0
            Agenda.segments = []
        return Agenda._instance

    def empty(self):
        return len(self.segments) == 0

    def add_to_agenda(self, time, action):
        segments = self.segments
        lo, hi = 0, len(segments)
        while lo < hi:
            mid = (lo + hi) // 2
            if segments[mid].time < time:
                lo = mid + 1
            else:
                hi = mid
        if lo < len(segments) and segments[lo].time == time:
            segments[lo].actions.append(action)
        else:
            segments.insert(lo, Agenda.Segment(action, time))

    @property
    def first_agenda_item(self):
        if self.empty():
            return lambda: print('The agenda is empty', file=sys.stderr)
        # update time
        self.current_time = self.segments[0].time
        return self.segments[0].actions[0]

    def remove_first_agenda_item(self):
        first_segment = self.segments[0]
        first_segment.actions = first_segment.actions[1:]
        if len(first_segment.actions) == 0:
            self.segments = self.segments[1:]

    class Segment(object):
        def __init__(self, action, time=0):
            self.time = time
            self.actions = [action]


class Wire(object):
    """Wire is the basic element in circuit simulation.
    Each Wire carries a signal(0 or 1).
    """

    def __init__(self, name=''):
        self._signal = 0
        self._action_procedures = []
        self.name = name

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, new_value):
        self._signal = new_value
        for proc in self._action_procedures:
            proc()

    def add_action_procedure(self, proc):
        self._action_procedures.append(proc)
        proc()

    def __str__(self):
        return 'Wire {0}: {1}'.format(self.name, self.signal)

    def __add__(self, other):
        _output = Wire('output')
        OrGate(self, other, _output)
        return _output

    def __radd__(self, other):
        _output = Wire('output')
        OrGate(self, other, _output)
        return _output

    def __mul__(self, other):
        _output = Wire()
        AndGate(self, other, _output)
        return _output

    def __rmul__(self, other):
        _output = Wire()
        AndGate(self, other, _output)
        return _output

    # python 3.5+
    def __neg__(self):
        _output = Wire()
        InvertGate(self, _output)
        return _output

    def __or__(self, other):
        _output = Wire()
        OrGate(self, other, _output)
        return _output

    def __xor__(self, other):
        _output = Wire()
        XorGate(self, other, _output)
        return _output

    def __and__(self, other):
        _output = Wire()
        AndGate(self, other, _output)
        return _output


class AndGate(object):
    def __init__(self, input_a: Wire, input_b: Wire, output: Wire):
        def and_action():
            def set_output():
                def logical_and(a, b):
                    assert a in [0, 1] and b in [0, 1]
                    if a == 1 and b == 1:
                        return 1
                    return 0

                new_value = logical_and(input_a.signal, input_b.signal)
                output.signal = new_value

            after_delay(AND_GATE_DELAY, set_output)

        input_a.add_action_procedure(and_action)
        input_b.add_action_procedure(and_action)


class OrGate(object):
    def __init__(self, input_a: Wire, input_b: Wire, output: Wire):
        def or_action():
            def set_output():
                def logical_or(a, b):
                    assert a in [0, 1] and b in [0, 1]
                    if a == 0 and b == 0:
                        return 0
                    return 1

                new_value = logical_or(input_a.signal, input_b.signal)
                output.signal = new_value

            after_delay(OR_GATE_DELAY, set_output)

        input_a.add_action_procedure(or_action)
        input_b.add_action_procedure(or_action)


class InvertGate(object):
    def __init__(self, input_a: Wire, output: Wire):
        def invert_action():
            def set_output():
                def logical_not(s):
                    assert s in [0, 1]
                    if s == 0:
                        return 1
                    elif s == 1:
                        return 0

                new_value = logical_not(input_a.signal)
                output.signal = new_value

            after_delay(INVERT_DELAY, set_output)

        input_a.add_action_procedure(invert_action)


class XorGate(object):
    def __init__(self, input_a: Wire, input_b: Wire, output: Wire):
        def xor_action():
            def set_output():
                def logical_xor(a, b):
                    assert a in [0, 1] and b in [0, 1]
                    if a != b:
                        return 1
                    return 0

                new_value = logical_xor(input_a.signal, input_b.signal)
                output.signal = new_value

            after_delay(XOR_GATE_DELAY, set_output)

        input_a.add_action_procedure(xor_action)
        input_b.add_action_procedure(xor_action)


class Monitor(object):
    def __init__(self):
        pass

    VERBOSITY = 1

    def __new__(cls, *args, **kwargs):
        if not hasattr(Monitor, '_instance'):
            Monitor._instance = object.__new__(cls)
            Monitor.watching = []
        return Monitor._instance

    def add(self, wire: Wire):
        def print_log():
            if Monitor.VERBOSITY >= 2:
                print('{0}: {1} New-value = {2}'.format(Agenda().current_time, wire.name, wire.signal))

        self.watching.append(wire)
        wire.add_action_procedure(print_log)


class HalfAdder(object):
    def __init__(self, a, b, s, c):
        AndGate(a, b, c)
        XorGate(a, b, s)


class FullAdder(object):
    def __init__(self, a, b, c_in, sum_tmp, c_out):
        s = Wire()
        c1 = Wire()
        c2 = Wire()
        HalfAdder(b, c_in, s, c1)
        HalfAdder(a, s, sum_tmp, c2)
        OrGate(c1, c2, c_out)


def after_delay(delay, proc):
    agenda = Agenda()
    agenda.add_to_agenda(agenda.current_time + delay, proc)


def propagate():
    agenda = Agenda()
    while not agenda.empty():
        first_item = agenda.first_agenda_item
        first_item()
        agenda.remove_first_agenda_item()
    print('Propagate Done. Result:')
    monitor = Monitor()
    for w in monitor.watching:
        print(w)
    print('-'*30)


def probe(wire: Wire):
    monitor = Monitor()
    monitor.add(wire)


if __name__ == '__main__':
    I0 = Wire()
    I1 = Wire()
    I2 = Wire()
    I3 = Wire()
    I4 = Wire()
    I5 = Wire()
    I6 = Wire()
    I7 = Wire()

    Y0 = I1 + I3 + I5 + I7
    Y1 = I2 + I3 + I6 + I7
    Y2 = I4 + I5 + I6 + I7

    Y0.name = 'Y0'
    Y1.name = 'Y1'
    Y2.name = 'Y2'

    probe(Y0)
    probe(Y1)
    probe(Y2)

    I0.signal = 1
    propagate()
