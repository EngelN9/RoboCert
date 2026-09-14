"""Sampled falsification search over a candidate configuration region.

This module attacks claims. It never supports them.

The three outcomes mean exactly this, and nothing wider:

`COUNTEREXAMPLE_FOUND`
    A sampled configuration violated the property **in the simulation backend's physics
    model**. That model is not the model RoboCert certifies, so this is a *candidate*
    counterexample: promoting it to `ResultStatus.COUNTEREXAMPLE` requires re-validating the
    witness against RoboCert's own model in exact arithmetic (AGENTS.md SS31). This module
    performs no such validation and imports nothing that could.

`NO_COUNTEREXAMPLE_FOUND`
    A finite sample of `samples` points did not violate the property. It says nothing about
    the points that were not sampled, and sampling is not universal quantification
    (AGENTS.md SS4.4). It is not evidence that the property holds.

`SIMULATION_ERROR`
    The search could not be carried out: the backend raised, the region was malformed, or
    the requested clearance exceeded what the model's collision margin can see. Fails
    closed -- an error is never reported as an absence of counterexamples.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from robocert.artifacts import ArtifactDigest, JSONValue, digest_json
from robocert.simulation.backend import (
    SimulationBackend,
    SimulationObservation,
    SimulationProvenance,
    encode_float,
    observe,
)
from robocert.specification import BoxDomain, Rational

Region = tuple[tuple[float, float], ...]


class FalsificationOutcome(StrEnum):
    """See the module docstring; each member's meaning is deliberately narrow."""

    COUNTEREXAMPLE_FOUND = "COUNTEREXAMPLE_FOUND"
    NO_COUNTEREXAMPLE_FOUND = "NO_COUNTEREXAMPLE_FOUND"
    SIMULATION_ERROR = "SIMULATION_ERROR"


@dataclass(frozen=True, slots=True)
class SimulationProperty:
    """A property the search tries to break.

    `holds` returns True when the observation SATISFIES the property, so the search reports
    a violation when it returns False. `required_clearance` is the separation distance the
    property needs to be able to see; the search refuses to run when the model's collision
    margin is smaller, because the simulator would then report "no contact" for a pair it
    never examined.
    """

    property_id: str
    holds: Callable[[SimulationObservation], bool]
    required_clearance: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.property_id, str) or not self.property_id:
            raise ValueError("property_id must be a non-empty string")
        if not callable(self.holds):
            raise ValueError("simulation property holds must be callable")
        if self.required_clearance is not None:
            required = float(self.required_clearance)
            if not math.isfinite(required) or required < 0.0:
                raise ValueError("required clearance must be nonnegative and finite")
            object.__setattr__(self, "required_clearance", required)


def no_penetration() -> SimulationProperty:
    """No reported contact pair is interpenetrating (all distances non-negative)."""

    def holds(observation: SimulationObservation) -> bool:
        return all(contact.distance >= 0.0 for contact in observation.contacts)

    return SimulationProperty(property_id="no_penetration", holds=holds)


def minimum_distance_at_least(delta: float) -> SimulationProperty:
    """Every reported pair keeps at least `delta` separation.

    `minimum_distance is None` means nothing was within the collision margin. Because the
    search refuses to run unless `delta <= collision_margin`, that case genuinely implies
    separation of at least `delta` in this model -- which is why the margin guard is not
    optional.
    """

    def holds(observation: SimulationObservation) -> bool:
        if observation.minimum_distance is None:
            return True
        return observation.minimum_distance >= delta

    return SimulationProperty(
        property_id=f"minimum_distance_at_least:{encode_float(delta)}",
        holds=holds,
        required_clearance=delta,
    )


def actuator_force_within(limit: float) -> SimulationProperty:
    """Every actuator force stays within +-`limit` in the simulation model's units."""

    normalized_limit = float(limit)
    if not math.isfinite(normalized_limit) or normalized_limit < 0.0:
        raise ValueError("actuator force limit must be nonnegative and finite")

    def holds(observation: SimulationObservation) -> bool:
        return all(abs(force) <= normalized_limit for force in observation.actuator_forces)

    return SimulationProperty(
        property_id=f"actuator_force_within:{encode_float(normalized_limit)}",
        holds=holds,
    )


def _normalize_region(bounds: Sequence[Sequence[float]]) -> Region:
    try:
        if any(len(pair) != 2 for pair in bounds):
            raise ValueError("each region axis requires exactly two bounds")
        region = tuple((float(pair[0]), float(pair[1])) for pair in bounds)
    except (IndexError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("region must contain numeric (lower, upper) pairs") from exc
    if not region:
        raise ValueError("region must be non-empty")
    if any(not math.isfinite(low) or not math.isfinite(high) for low, high in region):
        raise ValueError("region bounds must be finite")
    if any(low > high for low, high in region):
        raise ValueError("region lower bounds cannot exceed upper bounds")
    return region


def region_from_box_domain(domain: BoxDomain) -> Region:
    """Convert an exact claim-side `BoxDomain` into the float box the simulator samples.

    This is the one place exact rational bounds become binary floating point, and the
    direction is one-way: the resulting box is what was *sampled*, and carries none of the
    domain's exactness with it.
    """

    return tuple(
        (
            component.lower.numerator / component.lower.denominator,
            component.upper.numerator / component.upper.denominator,
        )
        for component in domain.components
    )


def candidate_assignment(
    violation: Violation,
    variable_ids: Sequence[str],
    *,
    transform: Callable[[float], Fraction] | None = None,
    max_denominator: int | None = None,
) -> dict[str, Rational]:
    """Turn a simulator violation into an exact rational point, for `robocert.refutation`.

    This produces a *candidate* and nothing more. It performs no validation, and this module
    never calls the refutation machinery itself: the untrusted layer proposes, the trusted
    core decides. A candidate that the simulator liked may well be rejected -- it may fall
    outside the claim's declared domain, or satisfy the claim's formula despite violating the
    simulator's property, because the two models are not the same model.

    The default conversion is EXACT and lossless: a Python float is a dyadic rational, so
    `Fraction(value)` is the sampled point itself, not an approximation of it.
    `max_denominator` instead rounds to a smaller, more auditable rational. Rounding moves
    the point, which is harmless here precisely because the result is re-checked from
    scratch -- a counterexample need not be the simulator's point, only *a* point of the
    domain where the formula is false.

    `variable_ids` states which claim variable each sampled coordinate is, positionally, and
    the caller owns that correspondence. The identity default is only right when coordinates
    and units already agree. A claim in tangent-half-angle variables does NOT correspond to
    sampled radians (`AGENTS.md` SS7.2): pass
    `transform=robocert.witness_search2r.angle_to_t_candidate` for that, or any callable
    turning one sampled coordinate into one exact `Fraction`. The transform runs before
    `max_denominator`, and one that raises -- as the half-angle transport does at `+-pi`,
    which its chart cannot represent -- propagates rather than being swallowed.
    """

    if not isinstance(violation, Violation):
        raise ValueError("candidate assignment requires a Violation")
    if len(variable_ids) != len(violation.configuration):
        raise ValueError(
            f"{len(variable_ids)} variable ids for {len(violation.configuration)} coordinates"
        )
    if any(not isinstance(variable_id, str) or not variable_id for variable_id in variable_ids):
        raise ValueError("variable ids must be non-empty strings")
    if len(variable_ids) != len(set(variable_ids)):
        raise ValueError("variable ids must be unique")
    if max_denominator is not None and (
        not isinstance(max_denominator, int)
        or isinstance(max_denominator, bool)
        or max_denominator < 1
    ):
        raise ValueError("max_denominator must be a positive integer")
    assignment: dict[str, Rational] = {}
    for variable_id, value in zip(variable_ids, violation.configuration, strict=True):
        if not math.isfinite(value):
            raise ValueError("candidate coordinates must be finite")
        exact = Fraction(value) if transform is None else transform(value)
        if not isinstance(exact, Fraction):
            raise ValueError("candidate transform must return an exact Fraction")
        if max_denominator is not None:
            exact = exact.limit_denominator(max_denominator)
        assignment[variable_id] = Rational(exact.numerator, exact.denominator)
    return assignment


def region_from_sequence(bounds: Sequence[Sequence[float]]) -> Region:
    """Normalize a nested sequence of (lower, upper) pairs into a `Region`."""

    return _normalize_region(bounds)


@dataclass(frozen=True, slots=True)
class Violation:
    """One sampled configuration whose observation failed the property."""

    sample_index: int
    configuration: tuple[float, ...]
    observation: SimulationObservation

    def __post_init__(self) -> None:
        if not isinstance(self.sample_index, int) or isinstance(self.sample_index, bool):
            raise ValueError("sample_index must be an integer")
        if self.sample_index < 0:
            raise ValueError("sample_index cannot be negative")
        configuration = tuple(float(value) for value in self.configuration)
        if any(not math.isfinite(value) for value in configuration):
            raise ValueError("violation configuration must be finite")
        if not isinstance(self.observation, SimulationObservation):
            raise ValueError("violation requires a SimulationObservation")
        object.__setattr__(self, "configuration", configuration)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "sample_index": self.sample_index,
            "configuration": [encode_float(item) for item in self.configuration],
            "observation": self.observation.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class FalsificationReport:
    """The structured, hashable record of one falsification search."""

    outcome: FalsificationOutcome
    property_id: str
    region: Region
    seed: int
    samples_requested: int
    samples_evaluated: int
    settle_steps: int
    provenance: SimulationProvenance | None
    violations: tuple[Violation, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "outcome": self.outcome.value,
            "property_id": self.property_id,
            "region": [[encode_float(low), encode_float(high)] for low, high in self.region],
            "seed": self.seed,
            "samples_requested": self.samples_requested,
            "samples_evaluated": self.samples_evaluated,
            "settle_steps": self.settle_steps,
            "provenance": None if self.provenance is None else self.provenance.to_dict(),
            "violations": [item.to_dict() for item in self.violations],
            "diagnostics": list(self.diagnostics),
        }

    def digest(self) -> ArtifactDigest:
        return digest_json(self.to_dict())


def sample_configurations(region: Region, samples: int, seed: int) -> list[tuple[float, ...]]:
    """Deterministic uniform samples of `region`, in a fixed axis order.

    Exposed so a report's `seed` can be replayed independently of any backend.
    """

    normalized_region = _normalize_region(region)
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 1:
        raise ValueError("sample count must be a positive integer")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    generator = random.Random(seed)
    configurations = [
        tuple(generator.uniform(low, high) for low, high in normalized_region)
        for _ in range(samples)
    ]
    if any(not math.isfinite(value) for item in configurations for value in item):
        raise ValueError("sampling produced a non-finite configuration")
    return configurations


def search_for_counterexample(
    *,
    backend: SimulationBackend,
    region: Region,
    property: SimulationProperty,
    samples: int,
    seed: int,
    settle_steps: int = 0,
    command_actuators: bool = False,
) -> FalsificationReport:
    """Sample `region`, look for a configuration violating `property`, stop at the first.

    `command_actuators` passes each sampled configuration through as the actuator command,
    which is what makes `get_actuator_forces` report the load a pose requires rather than a
    servo error. It assumes actuators correspond one-to-one with the sampled coordinates; a
    model where they do not raises in the backend and yields `SIMULATION_ERROR`.

    Returns a `FalsificationReport`, never a `robocert.results.CertificationResult`. See the
    module docstring for what each outcome does and does not mean.
    """

    property_id = property.property_id if isinstance(property, SimulationProperty) else "invalid"
    report_region: Region = ()

    def failed(
        reason: str,
        provenance: SimulationProvenance | None = None,
        evaluated: int = 0,
    ) -> FalsificationReport:
        return FalsificationReport(
            outcome=FalsificationOutcome.SIMULATION_ERROR,
            property_id=property_id,
            region=report_region,
            seed=seed,
            samples_requested=samples,
            samples_evaluated=evaluated,
            settle_steps=settle_steps,
            provenance=provenance,
            diagnostics=(reason,),
        )

    if not isinstance(property, SimulationProperty):
        return failed("property must be a SimulationProperty")
    try:
        report_region = _normalize_region(region)
    except ValueError as exc:
        return failed(str(exc))
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 1:
        return failed("sample count must be a positive integer")
    if not isinstance(seed, int) or isinstance(seed, bool):
        return failed("seed must be an integer")
    if not isinstance(settle_steps, int) or isinstance(settle_steps, bool) or settle_steps < 0:
        return failed("settle step count must be a nonnegative integer")

    try:
        provenance = backend.provenance
    except Exception as exc:  # fail closed: an unreadable backend is not a clean search
        return failed(f"backend provenance raised {type(exc).__name__}: {exc}")
    if not isinstance(provenance, SimulationProvenance):
        return failed("backend provenance is not a SimulationProvenance")

    required = property.required_clearance
    if required is not None and required > provenance.collision_margin:
        return failed(
            f"property requires clearance {encode_float(required)} but the model's collision "
            f"margin is {encode_float(provenance.collision_margin)}; the simulator cannot "
            "observe separation beyond its margin, so a negative answer would be meaningless",
            provenance,
        )

    try:
        configurations = sample_configurations(report_region, samples, seed)
        if len(configurations) != samples:
            raise ValueError("sampler returned an incorrect sample count")
    except Exception as exc:
        return failed(f"sampling raised {type(exc).__name__}: {exc}", provenance)

    for index, configuration in enumerate(configurations):
        try:
            if len(configuration) != len(report_region) or any(
                not math.isfinite(value) or not low <= value <= high
                for value, (low, high) in zip(configuration, report_region, strict=True)
            ):
                raise ValueError("sampler returned an invalid configuration")
            backend.set_configuration(
                configuration, control=configuration if command_actuators else None
            )
            if settle_steps:
                backend.step(settle_steps)
            observation = observe(backend)
            satisfied = property.holds(observation)
            if not isinstance(satisfied, bool):
                raise TypeError("simulation property must return bool")
        except Exception as exc:  # fail closed
            return failed(f"sample {index} raised {type(exc).__name__}: {exc}", provenance, index)
        if not satisfied:
            return FalsificationReport(
                outcome=FalsificationOutcome.COUNTEREXAMPLE_FOUND,
                property_id=property.property_id,
                region=report_region,
                seed=seed,
                samples_requested=samples,
                samples_evaluated=index + 1,
                settle_steps=settle_steps,
                provenance=provenance,
                violations=(Violation(index, configuration, observation),),
                diagnostics=(
                    "candidate counterexample in the simulation model only; it does not "
                    "falsify a RoboCert claim until re-validated exactly against RoboCert's "
                    "own model",
                ),
            )

    return FalsificationReport(
        outcome=FalsificationOutcome.NO_COUNTEREXAMPLE_FOUND,
        property_id=property.property_id,
        region=report_region,
        seed=seed,
        samples_requested=samples,
        samples_evaluated=samples,
        settle_steps=settle_steps,
        provenance=provenance,
        diagnostics=(
            f"{samples} sampled configurations did not violate the property; this is not "
            "evidence that the property holds on the region",
        ),
    )


__all__ = [
    "FalsificationOutcome",
    "FalsificationReport",
    "Region",
    "SimulationProperty",
    "Violation",
    "actuator_force_within",
    "candidate_assignment",
    "minimum_distance_at_least",
    "no_penetration",
    "region_from_box_domain",
    "region_from_sequence",
    "sample_configurations",
    "search_for_counterexample",
]
