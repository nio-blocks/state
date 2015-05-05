from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from .test_state_base_block import StateSignal
from nio.common.signal.base import Signal
from ..relay_block import Relay


class OtherSignal(Signal):

    def __init__(self, state):
        super().__init__()
        self.other = state


@patch.object(Relay, '_backup')
class TestRelay(NIOBlockTestCase):

    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def signals_notified(self, signals, output_id='default'):
        self._signals = signals

    def test_relay(self, mock_backup):
        blk = Relay()
        self.configure_block(blk, {
            # Signals to 'getter' input act as setter if state_sig is True
            'state_sig': '{{ hasattr($, "state") }}',
            'state_expr': '{{ $state }}',
            'initial_state': '{{ False }}',
            'group_by': 'null'
        })
        blk.start()

        self.assertFalse(blk.get_state('null'))

        # set state to True
        blk.process_signals([StateSignal('1')])
        self.assertEqual(blk.get_state('null'), '1')
        self.assertTrue(bool(blk.get_state('null')))
        self.assert_num_signals_notified(0, blk)

        # send a true state + other signal
        blk.process_signals([StateSignal('2'), OtherSignal('3')])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(blk.get_state('null'), '2')
        self.assertTrue(bool(blk.get_state('null')))
        self.assertEqual(self._signals[0].other, '3')

        # no signals pass through when State is false
        blk.process_signals([StateSignal(False), OtherSignal('4')])
        self.assertFalse(bool(blk.get_state('null')))
        self.assert_num_signals_notified(1, blk)

        # no signals still pass through
        blk.process_signals([OtherSignal(n) for n in range(100)])
        self.assertEqual(blk.get_state('null'), False)
        self.assert_num_signals_notified(1, blk)

        # set state to 1 and get notification signal.
        blk.process_signals([StateSignal('1'), OtherSignal('5')])
        self.assert_num_signals_notified(2, blk)
        self.assertEqual(blk.get_state('null'), '1')
        self.assertTrue(bool(blk.get_state('null')))
        self.assertEqual(self._signals[0].other, '5')
        blk.stop()

    def test_getter_input(self, mock_backup):
        blk = Relay()
        self.configure_block(blk, {
            # No signals in 'getter' input are state setter signals
            'state_sig': '{{ False }}',
            'state_expr': '{{ $state }}',
            'initial_state': '{{ False }}',
            'group_by': 'null'
        })
        blk.start()
        # initial state is False so signals do not pass through
        blk.process_signals([OtherSignal('3')], input_id='getter')
        self.assert_num_signals_notified(0, blk)
        # set state to True
        blk.process_signals([StateSignal('1')], input_id='setter')
        # pass signals through
        blk.process_signals([OtherSignal('3')], input_id='getter')
        self.assert_num_signals_notified(1, blk)
        # set state back to False
        blk.process_signals([StateSignal('')], input_id='setter')
        # signals do not pass through
        blk.process_signals([OtherSignal('3')], input_id='getter')
        self.assert_num_signals_notified(1, blk)

    def test_setter_input(self, mock_backup):
        blk = Relay()
        self.configure_block(blk, {
            # No signals in 'getter' input are state setter signals
            'state_sig': '{{ False }}',
            'state_expr': '{{ $state }}',
            'initial_state': '{{ False }}',
            'group_by': 'null'
        })
        blk.start()
        self.assertFalse(blk.get_state('null'))
        # set state to True
        blk.process_signals([StateSignal('1')], input_id='setter')
        self.assertEqual(blk.get_state('null'), '1')
        self.assertTrue(bool(blk.get_state('null')))
        # set state back to False
        blk.process_signals([StateSignal('')], input_id='setter')
        self.assertEqual(blk.get_state('null'), '')
        self.assertFalse(bool(blk.get_state('null')))
        # no signals were notified
        self.assert_num_signals_notified(0, blk)

    def test_bad_state_sig(self, mock_backup):
        """ Make sure that a bad state_sig is not a state setter """
        blk = Relay()
        self.configure_block(blk, {
            'state_sig': '{{ $state + 1 }}',
            'state_expr': '{{ $state }}',
            'group_by': 'null'
        })
        blk.start()

        # set state - no signal notified
        blk.process_signals([StateSignal(1)])
        self.assert_num_signals_notified(0, blk)

        # set state again but error in state_sig
        # this should NOT set the state, instead the signal
        # should be let through since the relay should be open
        blk.process_signals([StateSignal('hello')])
        self.assert_num_signals_notified(1, blk)
        self.assertTrue(bool(blk.get_state('null')))

        # error in state_sig doesn't matter if the signals is passed into the
        # 'setter' input. And the empty strings sets state to False.
        blk.process_signals([StateSignal('')], 'setter')
        self.assert_num_signals_notified(1, blk)
        self.assertFalse(bool(blk.get_state('null')))
