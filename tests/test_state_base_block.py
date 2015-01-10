from unittest.mock import patch
from ..state_change_base_block import StateChangeBase, NoState
from nio.common.block.base import Block
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from unittest.mock import MagicMock


class StateBlock(StateChangeBase):
    pass

class StateSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.state = state


class TestStateChangeBase(NIOBlockTestCase):
    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    @patch.object(StateChangeBase, '_backup')
    def test_state_change(self, mock_backup):
        blk = StateBlock()
        blk.state_expr = '{{$state}}'
        self.assertEqual(NoState, blk._state)
        blk._process_state(StateSignal('1'))
        self.assertEqual('1', blk._state)
        blk._process_state(StateSignal('2'))
        self.assertEqual('2', blk._state)
        blk._process_state(StateSignal(1))
        self.assertEqual(1, blk._state)
        # test when attr doesn't exist.
        blk._process_state(Signal())
        self.assertEqual('', blk._state)

    @patch.object(StateChangeBase, '_backup')
    def test_bad_expr(self, mock_backup):
        blk = StateBlock()
        blk.state_expr = '{{$state + 1}}'
        self.assertEqual(NoState, blk._state)
        blk._process_state(StateSignal('hello'))
        self.assertEqual(NoState, blk._state)
