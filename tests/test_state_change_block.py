from unittest.mock import patch
from ..state_change_block import StateChange
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal


class StateSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.state = state


class TestStateChange(NIOBlockTestCase):
    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def signals_notified(self, signals, output_id='default'):
        self._signals = signals

    @patch.object(StateChange, '_backup')
    def test_state_change(self, mock_backup):
        blk = StateChange()
        config = {
            "state_expr": "{{$state}}",
        }
        self.configure_block(blk, config)
        blk.start()
        # init state to 1. initializing so no notification.
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk._state, '1')
        self.assert_num_signals_notified(0, blk)
        # set state to 2 and get notification signal.
        blk.process_signals([StateSignal('2')])
        self.assertEqual(blk._state, '2')
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self._signals[0].prev_state, '1')
        self.assertEqual(self._signals[0].state, '2')
        # no notification when state does not change.
        blk.process_signals([StateSignal('2')])
        self.assertEqual(blk._state, '2')
        self.assert_num_signals_notified(1, blk)
        # set state to 1 and get notification signal.
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk._state, '1')
        self.assert_num_signals_notified(2, blk)
        self.assertEqual(self._signals[0].prev_state, '2')
        self.assertEqual(self._signals[0].state, '1')
        blk.stop()
