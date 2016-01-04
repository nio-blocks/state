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
            'initial_state': '{{False}}',
            "state_expr": "{{$state}}",
            'group_by': 'null',
            "state_name": "mstate"
        })
        blk.start()

        signals_notified = 0

        # set state
        blk.process_signals([StateSignal('1')], input_id='setter')
        self.assertEqual(blk.get_state('null'), '1')
        self.assert_num_signals_notified(signals_notified, blk)

        # set state + other signal
        blk.process_signals([StateSignal('2')], input_id='setter')
        blk.process_signals([OtherSignal('3')])
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

    def test_getter_input(self, mock_backup):
        blk = MergeState()
        self.configure_block(blk, {
            # No signals in 'getter' input are state setter signals
            'state_expr': '{{ $state }}',
            'initial_state': '{{ False }}',
            'group_by': 'null',
            'state_name': 'mstate'
        })
        blk.start()
        # getter should get initial statue of False
        blk.process_signals([OtherSignal('3')], input_id='getter')
        self.assertEqual(self._signals[0].mstate, False)
        self.assert_num_signals_notified(1, blk)
        # set state to '1'
        blk.process_signals([StateSignal('1')], input_id='setter')
        # getter should get state of '1'
        blk.process_signals([OtherSignal('3')], input_id='getter')
        self.assertEqual(self._signals[0].mstate, '1')
        self.assert_num_signals_notified(2, blk)

    def test_setter_input(self, mock_backup):
        blk = MergeState()
        self.configure_block(blk, {
            # No signals in default input are state setter signals
            'initial_state': '{{ False }}',
            "state_expr": "{{ $state }}",
            'group_by': 'null',
            'state_name': "mstate"
        })
        blk.start()
        # set state
        blk.process_signals([StateSignal('1')], input_id='setter')
        self.assertEqual(blk.get_state('null'), '1')
        # set state again
        blk.process_signals([StateSignal('2')], input_id='setter')
        self.assertEqual(blk.get_state('null'), '2')
        # no signals were notified
        self.assert_num_signals_notified(0, blk)
