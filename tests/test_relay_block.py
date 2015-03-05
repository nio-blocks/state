from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from .test_state_base_block import StateSignal
from nio.common.signal.base import Signal
from ..relay_block import Relay


class OtherSignal(Signal):

    def __init__(self, state):
        super().__init__()
        self.other = state


class TestRelay(NIOBlockTestCase):

    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def signals_notified(self, signals, output_id='default'):
        self._signals = signals

    @patch.object(Relay, '_backup')
    def test_relay(self, mock_backup):
        blk = Relay()
        self.configure_block(blk, {
            'state_sig': '{{hasattr($, "state")}}',
            'state_expr': '{{$state}}',
            'initial_state': '{{False}}',
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
