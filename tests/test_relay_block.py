from ..relay_block import Relay
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal

class StateSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.state = state

class OtherSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.other = state

class TestRelay(NIOBlockTestCase):
    def signals_notified(self, signals):
        self._signals = signals

    def test_state_change(self):
        blk = Relay()
        config = {
            "state_expr": "{{$state}}"  # This should work but there is a bug with state_expressions
            # "state_expr": "{{$state if hasattr($, 'state') else 1/0}}",
        }
        self.configure_block(blk, config)
        blk.start()

        signals_notified = 0

        # send a true state, expect to receive it
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk._state, '1')
        self.assertEqual(self._signals[0].state, '1')
        signals_notified += 1
        self.assert_num_signals_notified(signals_notified, blk)
        # send a true state + other signal and get both of them

        # Ok, couple of problems. If these two are switched, _state is set to ''
        # This points to the self.state_expr returning a value even if there is
        # not the proper attribute in the signal!
        blk.process_signals([StateSignal('2'), OtherSignal('3')])
        signals_notified += 2
        self.assertEqual(blk._state, '2')

        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(self._signals[0].state, '2')
        self.assertEqual(self._signals[1].other, '3')

        # no signals pass through when State is false
        blk.process_signals([StateSignal(False), OtherSignal('4')])
        self.assertEqual(blk._state, False)
        self.assert_num_signals_notified(signals_notified, blk)

        # set state to 1 and get notification signal.
        # this is where it is currently failing because there is no signal!
        blk.process_signals([StateSignal('1'), OtherSignal('5')])
        signals_notified += 2
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(blk._state, '1')
        self.assertEqual(self._signals[0].state, '1')
        self.assertEqual(self._signals[1].other, '5')
        blk.stop()
