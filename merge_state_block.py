from .state_base_block import StateBase
from nio.block.terminals import input
from nio.util.discovery import discoverable
from nio.properties import Property
from nio.properties import Property, StringProperty, \
    VersionProperty


@input('setter')
@input('getter')
@discoverable
class MergeState(StateBase):

    """ Merge the *setter* state into *getter* signals.

    Maintains a *state* and merges that state (with name **state_name**) with
    signals that are input through the *getter* input.
    """

    state_name = StringProperty(default='state', title="State Name")
    version = VersionProperty('0.1.0')

    def _process_group(self, signals, group, to_notify):
        """ Process the signals from the default/getter input for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            existing_state = self.get_state(group)
            self.logger.debug(
                "Assigning state {} to signal".format(existing_state))
            setattr(signal, self.state_name(), existing_state)
            to_notify['default'].append(signal)

    def _process_setter_group(self, signals, group, to_notify):
        """ Process the signals from the setter input for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            self.logger.debug("Attempting to set state")
            self._process_state(signal, group)
