from copy import copy
from collections import defaultdict
from .mixins.group_by.group_by_block import GroupBy
from nio.common.signal.base import Signal
from nio.common.block.base import Block
from nio.common.command import command
from nio.common.command.params.string import StringParameter
from nio.metadata.properties import ExpressionProperty, TimeDeltaProperty, \
    BoolProperty
from nio.metadata.properties.version import VersionProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock


@command('current_state', StringParameter("group", default='null'))
class StateBase(GroupBy, Block):

    """ A base block mixin for keeping track of state """

    state_expr = ExpressionProperty(
        title='State Expression', default='{{ $state }}')
    use_persistence = BoolProperty(title="Use Persistence", default=True)
    initial_state = ExpressionProperty(
        title='Initial State', default='{{ None }}')

    # Hidden properties
    version = VersionProperty(default='1.0.1', min_version='1.0.0')
    backup_interval = TimeDeltaProperty(
        title='Backup Interval', default={'seconds': 600}, visible=False)

    def __init__(self):
        super().__init__()
        self._initial_state = None
        self._backup_job = None
        self._state_locks = defaultdict(Lock)
        self._safe_lock = Lock()
        self._states = {}

    def configure(self, context):
        super().configure(context)

        # Store a cached copy of what a new state should look like
        self._initial_state = self.initial_state(Signal())

        # We want to check if the persistence has the key, not check the loaded
        # value. This allows us to persist False-y states
        if self.use_persistence and self.persistence.has_key('states'):
            self._states = self.persistence.load('states')

    def start(self):
        super().start()
        self._backup_job = Job(self._backup, self.backup_interval, True)

    def stop(self):
        self._backup_job.cancel()
        self._backup()
        super().stop()

    def get_state(self, group):
        """ Return the current state for a group.

        If the state has not been set yet, this function will return the
        initial state configured for the block. It will also set that as the
        state.
        """
        if group not in self._states:
            self._states[group] = copy(self._initial_state)

        return self._states[group]

    def process_signals(self, signals, input_id='default'):
        """ Process incoming signals.

        This block is a helper, it will just call _process_group and
        notify any signals that get appeneded to the to_notify list.

        Most likely, _process_group will be overridden in subclasses instead
        of this method.
        """
        self._logger.debug(
            "Ready to process {} incoming signals".format(len(signals)))
        signals_to_notify = []
        with self._safe_lock:
            if input_id == 'default' or input_id == 'getter':
                self.for_each_group(
                    self._process_group,
                    signals,
                    kwargs={"to_notify": signals_to_notify})
            elif input_id == 'setter':
                self.for_each_group(
                    self._process_setter_group,
                    signals,
                    kwargs={"to_notify": signals_to_notify})
        if signals_to_notify:
            self.notify_signals(signals_to_notify)

    def _process_group(self, signals, group, to_notify):
        """ Implement this method in subclasses to process signals in a group.

        Add any signals that you wish to notify to the to_notify list.

        No return value is necessary

        This method is for signals that come in the 'default' input.
        """
        pass

    def _process_setter_group(self, signals, group, to_notify):
        """ Implement this method in subclasses to process signals in a group.

        Add any signals that you wish to notify to the to_notify list.

        No return value is necessary

        This method is for signals that come in the 'setter' input.
        """
        pass

    def _process_state(self, signal, group):
        """ Changes state based on a signal and a group.

        If the signal cannot be processed, the state remains unchanged.

        Returns:
            Tuple: (prev_sate, new_state) if the state was changed
            None - if the state did not change
        """
        with self._state_locks[group]:
            prev_state = self.get_state(group)
            try:
                new_state = self.state_expr(signal)
            except:
                # expression failed so don't set a state.
                self._logger.exception(
                    "State Change failed for group {}".format(group))
                return

            if new_state != prev_state:
                # notify signal if there was a prev_state and
                # the state has changed.
                self._logger.debug(
                    "Changing state from {} to {} for group {}".format(
                        prev_state, new_state, group))
                self._states[group] = new_state

                return (prev_state, new_state)

    def _backup(self):
        """ Persist the current state using the persistence module. """
        self._logger.debug("Attempting to persist the current states")
        self.persistence.store("states", self._states)
        self.persistence.save()

    def current_state(self, group):
        """ Command that returns the current state of a group """
        with self._state_locks[group]:
            if group in self._states:
                return {"state": self._states[group]}
            else:
                return {}
