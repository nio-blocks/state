from ..state_mixin import StateMixin, NoState
from nio.common.block.base import Block
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from unittest.mock import MagicMock


class StateBlock(StateMixin, Block):
    def __init__(self):
        super().__init__()
        StateMixin.__init__(self)


class StateSignal(Signal):
    def __init__(self, state):
        super().__init__()
        self.state = state


class TestStateMixin(NIOBlockTestCase):

    def test_state_change(self):
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

    def test_bad_expr(self):
        blk = StateBlock()
        blk.state_expr = '{{$state + 1}}'
        self.assertEqual(NoState, blk._state)
        blk._process_state(StateSignal('hello'))
        self.assertEqual(NoState, blk._state)


