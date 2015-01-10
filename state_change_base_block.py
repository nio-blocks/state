from nio.common.signal.base import Signal
from nio.common.block.base import Block
from nio.common.command import command
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.metadata.properties.bool import BoolProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock

# Default starting state
class NoState(Exception):
    pass


@command('current_state')
class StateChangeBase(Block):
    """ A block mixin for keeping track of state
    use _process_state with the signal to determine if a state change is necessary

    """
    state_expr = ExpressionProperty(title='State Expression', default='{{$state}}')
    backup_interval = TimeDeltaProperty(title='Backup Interval',
                                        default={'seconds': 600})
    use_persistence = BoolProperty(title="Use Persistence", default=True,
            visible=False)

    def __init__(self):
        super().__init__()
        self._state = NoState
        self._backup_job = None
        self._state_lock = Lock()

    def configure(self, context):
        super().configure(context)
        if self.use_persistence:
            self._state = self.persistence.load('state') or self._state

    def start(self):
        super().start()
        self._backup_job = Job(
            self._backup,
            self.backup_interval,
            True
        )

    def stop(self):
        self._backup_job.cancel()
        self._backup()

    def _process_state(self, signal, exclude = True):
        '''changes state from signal. If signal cannot be processed, state
        remains unchanged.

        returns a Signal on successful change. Returns None if state did not change
        '''
        with self._state_lock:
            prev_state = self._state
            try:
                self._state = self.state_expr(signal)
            except Exception as e:
                # expression failed so don't set a state.
                self._logger.error("State Change failed: {}".format(str(e)))
            if prev_state is not NoState and self._state != prev_state:
                # notify signal if there was a prev_state and
                # the state has changed.
                self._logger.debug( "Changing state from {} to {}".format(
                    prev_state, self._state
                ))
                if exclude:
                    signal = Signal()
                setattr(signal, "state", self._state)
                setattr(signal, "prev_state", prev_state)
                return signal

    def _backup(self):
        ''' Persist the current state using the persistence module.

        '''
        self.persistence.store(
            "state",
            self._state
        )
        self.persistence.save()

    def current_state(self):
        return {"state": self._state}
