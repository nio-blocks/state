from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.string import StringProperty
from .state_mixin import StateMixin, NoState


@Discoverable(DiscoverableType.block)
class MergeState(StateMixin, Block):
    '''
    When the state obtained from State Expression is true, signals are allowed through.
    Else signals are blocked
    '''
    state_name = StringProperty(default='', title="State Name")

    def process_signals(self, signals):
        signal_list = []
        for signal in signals:
            try:
                self._process_state(signal)
            except:
                pass
            if self._state is not NoState:
                setattr(signal, self.state_name, self._state)
                signal_list.append(signal)
        self.notify_signals(signal_list)
