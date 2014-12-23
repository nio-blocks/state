from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from ..merge_state_block import MergeState


class StateSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.state = state


class OtherSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.other = state


class TestMergeState(NIOBlockTestCase):
    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def signals_notified(self, signals):
        self._signals = signals

    @patch.object(MergeState, '_backup')
    def test_merge_state(self, mock_backup):
        blk = MergeState()
        config = {
            "state_expr": "{{$state}}",
            "state_name": "mstate"
        }
        self.configure_block(blk, config)
        blk.start()

        signals_notified = 0

        # set state
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk._state, '1')
        self.assert_num_signals_notified(signals_notified, blk)

        # set state + other signal
        blk.process_signals([StateSignal('2'), OtherSignal('3')])
        signals_notified += 1
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(blk._state, '2')
        self.assertEqual(self._signals[0].mstate, '2')

        # Just sending other signals pass through and have mstates of '2'
        blk.process_signals([OtherSignal(n) for n in range(100)])
        signals_notified += 100
        self.assertEqual(blk._state, '2')
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(len(self._signals), 100)
        [self.assertEqual(n.mstate, '2') for n in self._signals]

        blk.stop()
