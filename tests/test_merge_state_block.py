from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from .test_state_base_block import StateSignal
from ..merge_state_block import MergeState


class OtherSignal(Signal):

    def __init__(self, state):
        super().__init__()
        self.other = state


@patch.object(MergeState, '_backup')
class TestMergeState(NIOBlockTestCase):

    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def signals_notified(self, signals, output_id='default'):
        self._signals = signals

    def test_merge_state(self, mock_backup):
        blk = MergeState()
        self.configure_block(blk, {
            'state_sig': '{{hasattr($, "state")}}',
            'initial_state': '{{False}}',
            "state_expr": "{{$state}}",
            'group_by': 'null',
            "state_name": "mstate"
        })
        blk.start()

        signals_notified = 0

        # set state
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk.get_state('null'), '1')
        self.assert_num_signals_notified(signals_notified, blk)

        # set state + other signal
        blk.process_signals([StateSignal('2'), OtherSignal('3')])
        signals_notified += 1
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(blk.get_state('null'), '2')
        self.assertEqual(self._signals[0].mstate, '2')

        # Just sending other signals pass through and have mstates of '2'
        blk.process_signals([OtherSignal(n) for n in range(100)])
        signals_notified += 100
        self.assertEqual(blk.get_state('null'), '2')
        self.assert_num_signals_notified(signals_notified, blk)
        self.assertEqual(len(self._signals), 100)
        [self.assertEqual(n.mstate, '2') for n in self._signals]

        blk.stop()

    def test_bad_state_sig(self, mock_backup):
        """ Make sure that a bad state_sig is not a state setter """
        blk = MergeState()
        self.configure_block(blk, {
            'state_sig': '{{$state + 1}}',
            'state_expr': '{{$state}}',
            'group_by': 'null'
        })
        blk.start()

        # set state - no signal notified
        blk.process_signals([StateSignal(1)])
        self.assert_num_signals_notified(0, blk)

        # set state again but error in state_sig
        # this should NOT set the state, it should add the existing state
        # to the signal instead
        blk.process_signals([StateSignal('hello')])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self._signals[0].state, 1)
