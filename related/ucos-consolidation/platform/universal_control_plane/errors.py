"""UCOS-CTRL-000001 — Universal Control Plane error hierarchy."""

from __future__ import annotations


class ControlPlaneError(Exception):
    """Root error for the Universal Control Plane."""


class RegistrationError(ControlPlaneError):
    """A registration violated a constitutional constraint."""


class StateTransitionError(ControlPlaneError):
    """A lifecycle transition is not permitted from the current state."""


class ObjectNotFoundError(ControlPlaneError):
    """A referenced control-plane object does not exist in the registry."""


class DuplicateObjectError(ControlPlaneError):
    """An object with the same identity is already registered."""


class AssignmentError(ControlPlaneError):
    """An assignment could not be completed (agent unavailable, constraint violated, etc.)."""


class PromptRenderError(ControlPlaneError):
    """A prompt could not be rendered (missing context, template fault, etc.)."""


class DeterminationError(ControlPlaneError):
    """A determination could not be recorded or is structurally invalid."""


class ReplayError(ControlPlaneError):
    """A replay diverged from the recorded execution or is malformed."""


class EvidenceError(ControlPlaneError):
    """An evidence record is structurally invalid or its digest does not verify."""


class SchedulerError(ControlPlaneError):
    """The scheduler could not produce a valid schedule (cycle, missing dependency, etc.)."""


class ManifestError(ControlPlaneError):
    """The declared control-plane manifest is absent, unreadable or structurally invalid."""


class TruthDiscoveryError(ControlPlaneError):
    """Repository Truth could not be discovered from the declared sources."""


class GovernanceStateError(ControlPlaneError):
    """A governance state could not be resolved or is structurally invalid."""


class CertificationStateError(ControlPlaneError):
    """A certification state could not be resolved or is structurally invalid."""


class VersionError(ControlPlaneError):
    """A version could not be parsed, compared, promoted or rolled back."""


class EvolutionError(ControlPlaneError):
    """An evolution delta could not be computed or replayed."""


class JournalError(ControlPlaneError):
    """The durable journal is unreadable, corrupt, or its chain does not verify."""


class LinkageError(ControlPlaneError):
    """A constitutional linkage is incomplete — an orphan capability."""
