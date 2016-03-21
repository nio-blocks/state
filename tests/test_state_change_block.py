from unittest.mock import patch
from ..state_base_block import StateBase
from ..state_change_block import StateChange
from .test_state_base_block import StateSignal
from nio.testing.block_test_case import NIOBlockTestCase


@patch.object(StateBase, '_backup')
class TestStateChange(NIOBlockTestCase):

    #def get_test_modules(self):
    #    return self.ServiceDefaultModules + ['persistence']

    def test_state_change(self, mock_backup):
        """ Test that signals get notified only when state changes """
        blk = StateChange()
        self.configure_block(blk, {
            'state_expr': '{{$state}}',
            'initial_state': '{{None}}',
            'group_by': '{{$group}}'
        })
        blk.start()
        # init state to 1
        blk.process_signals([StateSignal('1', 'A')])
        self.assertEqual(blk.get_state('A'), '1')
        self.assert_num_signals_notified(1, blk)
        # set state to 2 and get notification signal.
        blk.process_signals([StateSignal('2', 'A')])
        self.assertEqual(blk.get_state('A'), '2')
        self.assert_num_signals_notified(2, blk)
        self.assertEqual(self.last_notified['default'][1].prev_state, '1')
        self.assertEqual(self.last_notified['default'][1].state, '2')
        self.assertEqual(self.last_notified['default'][1].group, 'A')
        # no notification when state does not change.
        blk.process_signals([StateSignal('2', 'A')])
        self.assertEqual(blk.get_state('A'), '2')
        self.assert_num_signals_notified(2, blk)
        # set state to 1 and get notification signal.
        blk.process_signals([StateSignal('1', 'A')])
        self.assertEqual(blk.get_state('A'), '1')
        self.assert_num_signals_notified(3, blk)
        self.assertEqual(self.last_notified['default'][2].prev_state, '2')
        self.assertEqual(self.last_notified['default'][2].state, '1')
        blk.stop()

    def test_no_exclude(self, mock_backup):
        """ Tests that state changing signals are passed without exclude """
        blk = StateChange()
        self.configure_block(blk, {
            'state_expr': '{{$state}}',
            'initial_state': '{{None}}',
            'group_by': '{{$group}}',
            'exclude': False
        })
        blk.start()
        # init state to 1
        blk.process_signals([StateSignal('1', 'A')])
        # set state to 2 and get notification signal.
        blk.process_signals([StateSignal('2', 'A')])
        self.assertEqual(blk.get_state('A'), '2')
        self.assert_num_signals_notified(2, blk)
        self.assertEqual(self.last_notified['default'][1].prev_state, '1')
        self.assertEqual(self.last_notified['default'][1].state, '2')
        # Make sure that attributes on the original signal also came through
        self.assertEqual(self.last_notified['default'][1].group, 'A')
        # no notification when state does not change.
        blk.process_signals([StateSignal('2', 'A')])
        self.assertEqual(blk.get_state('A'), '2')
        self.assert_num_signals_notified(2, blk)

    def test_state_name_property(self, mock_backup):
        """ Tests that state attribute can be customized"""
        blk = StateChange()
        self.configure_block(blk, {
            'state_name': 'attr'
        })
        blk.start()
        # init state to 1
        blk.process_signals([StateSignal(1, 'A')])
        self.assertDictEqual(self.last_notified['default'][0].to_dict(),
                             {'prev_attr': None, 'attr': 1, 'group': 'null'})
