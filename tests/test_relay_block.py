from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from ..relay_block import Relay


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

    def test_relay(self):
        print("Testing Relay")
        blk = Relay()
        config = {
            "state_expr": "{{$state}}"
        }
        self.configure_block(blk, config)
        blk.start()

        signals_notified = 0

        # state is initally False
        print(blk._state)
        self.assertFalse(bool(blk._state))

        # set state to True
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk._state, '1')
        self.assertTrue(bool(blk._state))
        self.assert_num_signals_notified(signals_notified, blk)

        # send a true state + other signal
        blk.process_signals([StateSignal('2'), OtherSignal('3')])
        signals_notified += 1
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(blk._state, '2')
        self.assertTrue(bool(blk._state))
        self.assertEqual(self._signals[0].other, '3')

        # no signals pass through when State is false
        blk.process_signals([StateSignal(False), OtherSignal('4')])
        self.assertFalse(bool(blk._state))
        self.assert_num_signals_notified(signals_notified, blk)

        # no signals still pass through
        blk.process_signals([OtherSignal(n) for n in range(100)])
        self.assertEqual(blk._state, False)
        self.assert_num_signals_notified(signals_notified, blk)

        # set state to 1 and get notification signal.
        blk.process_signals([StateSignal('1'), OtherSignal('5')])
        signals_notified += 1
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(blk._state, '1')
        self.assertTrue(bool(blk._state))
        self.assertEqual(self._signals[0].other, '5')
        blk.stop()
