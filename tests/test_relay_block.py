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

    def test_relay(self, mock_backup):
        blk = Relay()
        self.configure_block(blk, {
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
        self.assert_num_signals_notified(0, blk)

        # send a true state + other signal
        blk.process_signals([StateSignal('2')], input_id='setter')
        blk.process_signals([OtherSignal('3')])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(blk.get_state('null'), '2')
        self.assertTrue(bool(blk.get_state('null')))
        self.assertEqual(self.last_notified['default'][0].other, '3')

        # no signals pass through when State is false
        blk.process_signals([StateSignal(False)], input_id='setter')
        blk.process_signals([OtherSignal('4')])
        self.assertFalse(bool(blk.get_state('null')))
        self.assert_num_signals_notified(1, blk)

        # no signals still pass through
        blk.process_signals([OtherSignal(n) for n in range(100)])
        self.assertEqual(blk.get_state('null'), False)
        self.assert_num_signals_notified(1, blk)

        # set state to 1 and get notification signal.
        blk.process_signals([StateSignal('1')], input_id='setter')
        blk.process_signals([OtherSignal('5')])
        self.assert_num_signals_notified(2, blk)
        self.assertEqual(blk.get_state('null'), '1')
        self.assertTrue(bool(blk.get_state('null')))
        self.assertEqual(self.last_notified['default'][1].other, '5')
        blk.stop()

    def test_getter_input(self, mock_backup):
        blk = Relay()
        self.configure_block(blk, {
            # No signals in 'getter' input are state setter signals
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
