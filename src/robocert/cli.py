"""`robocert` command line interface with a closed production gate.

Public `certify` and `check` currently return `UNKNOWN`: no E2-approved checker
is registered, and neither command enters the historical search, transformation,
or artifact-checking paths. `schema` continues to print the packaged Phase 0
schemas. Historical handlers remain in this module only as quarantined research
code and are deliberately not connected to the parser.

Standard library only; `dependencies = []` is a deliberate project posture.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, NoReturn

from robocert.artifacts import ArtifactDigest, digest_json
from robocert.certificates import Certificate
from robocert.certify2r import CertificationOutcome, Planar2RProblem, certify_problem
from robocert.checking import verify_certificate
from robocert.errors import ValidationError
from robocert.problem2r import load_problem
from robocert.results import ResultStatus, certified_result, unknown_from_check, unknown_result
from robocert.schemas import SCHEMA_NAMES, schema_document
from robocert.specification import Claim

EXIT_CERTIFIED = 0
EXIT_NOT_CERTIFIED = 1
EXIT_ERROR = 2


def model_digest(problem: Planar2RProblem) -> ArtifactDigest:
    """Bind the certificate to the modeled robot, obstacle and margins.

    Any edit to the model changes this digest, so `check` will refuse a
    certificate whose problem file was altered after the fact.
    """
    return digest_json(
        {
            "kind": "planar_2r",
            "l1": str(problem.l1),
            "l2": str(problem.l2),
            "obstacle_center": [str(problem.obstacle_center[0]), str(problem.obstacle_center[1])],
            "obstacle_radius": str(problem.obstacle_radius),
            "clearance_margin": str(problem.clearance_margin),
            "epsilon": str(problem.epsilon),
            "t1_bounds": [str(problem.t1_bounds[0]), str(problem.t1_bounds[1])],
            "t2_bounds": [str(problem.t2_bounds[0]), str(problem.t2_bounds[1])],
        }
    )


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_deviation(deviation_squared: Fraction) -> str:
    return f"{math.sqrt(float(deviation_squared)):.3e}"


def _decimal(value: Fraction, places: int = 12) -> str:
    """Readable decimal rendering. Companion to the exact value, never a
    replacement for it -- the exact rational is what was actually certified."""
    return f"{float(value):.{places}f}"


def _point(point: tuple[Fraction, Fraction]) -> str:
    """A point shown both readably and exactly."""
    return f"`({_decimal(point[0])}, {_decimal(point[1])})` (exactly `{point[0]}`, `{point[1]}`)"


def _report(
    problem: Planar2RProblem,
    metadata: dict[str, Any],
    outcome: CertificationOutcome,
    status: ResultStatus,
) -> str:
    """Human-readable report following AGENTS.md SS65's explanation policy."""
    lines: list[str] = [
        f"# RoboCert result: {problem.problem_id}",
        "",
        f"**Status: `{status.value}`**",
        "",
    ]

    if outcome.accepted:
        assert outcome.achieved is not None and outcome.deviation_squared is not None
        assert outcome.configuration is not None and outcome.chart is not None
        q1, q2 = outcome.configuration
        lines += [
            "## What was certified",
            "",
            "A configuration of the modeled arm exists that simultaneously:",
            "",
            f"- places the tool at {_point(outcome.achieved)};",
            f"- keeps both links at least `{problem.clearance_margin}` beyond the "
            f"obstacle radius `{problem.obstacle_radius}`;",
            f"- holds `|det J| >= {problem.epsilon}`;",
            "- lies inside the certified joint-limit box below.",
            "",
            f"Configuration (radians, reporting only): `q1 = {q1:.12f}`, `q2 = {q2:.12f}`.",
            "",
            "## Distance from the point you asked for",
            "",
            f"Requested: {_point(problem.target)}",
            "",
            f"Certified: {_point(outcome.achieved)}",
            "",
            f"Exact squared deviation: `{outcome.deviation_squared}` "
            f"(distance ~ {_format_deviation(outcome.deviation_squared)}).",
            "",
            "The forward-kinematics conjunct is an exact equality, which a rational",
            "witness cannot satisfy for an arbitrary target. So what is certified is",
            "reachability of the achieved point above. The deviation is exact rational",
            "arithmetic on two constants -- check it by hand if you like. Certifying",
            "`||P(q) - P*|| <= tol` directly needs a different claim. The RC-003",
            "route was exactly refuted (`EX`); its actual-endpoint replacement is",
            "tracked as RC-005 and remains at E0.",
            "",
            f"Chart: `{outcome.chart}` (multiples of pi added to `q1`, `q2`).",
        ]
    else:
        lines += [
            "## No certificate was produced",
            "",
            "Diagnostics:",
            "",
        ]
        lines += [f"- {d}" for d in outcome.diagnostics]

    certified = metadata["joint_limits_certified"]
    requested = metadata["joint_limits_requested"]
    lines += [
        "",
        "## Joint limits actually certified",
        "",
        "| joint | requested (rad) | certified (rad) |",
        "|---|---|---|",
        f"| q1 | [{requested['q1'][0]}, {requested['q1'][1]}] | "
        f"[{certified['q1'][0]:.12f}, {certified['q1'][1]:.12f}] |",
        f"| q2 | [{requested['q2'][0]}, {requested['q2'][1]}] | "
        f"[{certified['q2'][0]:.12f}, {certified['q2'][1]:.12f}] |",
        "",
        "`tan(q/2)` is irrational for generic rational radian limits, so the limits",
        "are rounded INWARD to exact rationals. The certified interval is a subset of",
        "the one requested: a valid configuration near a limit may be missed, but none",
        "outside your limits can ever be accepted.",
        "",
        "## What this does not establish",
        "",
        "- **`UNKNOWN` is not infeasibility.** Failure to certify is not proof that no",
        "  configuration exists. The encoding provably misses configurations with",
        "  `q = +-pi` on any single chart (proof P2 Theorem 12.1); all four charts are",
        "  searched here, but inward-rounded limits and the reconstruction ladder remain",
        "  two further ways to come up empty on a reachable target.",
        "- This certifies a **mathematical model**, not a physical robot. Link thickness,",
        "  joint hardware, the volume swept while moving, controller behaviour, sensing",
        "  and actuation error are all outside the model (AGENTS.md SS61-SS64).",
        "- Only the single configuration above is certified. Nothing is claimed about a",
        "  path to it, about other targets, or about tolerance on the link lengths.",
        "",
        "## Reproducing this",
        "",
        "```",
        "robocert check <this directory>",
        "```",
        "",
        "That re-runs the deterministic checker against the stored claim and",
        "certificate. It does not re-run the search, and does not need to trust it.",
        "",
    ]
    return "\n".join(lines)


def _cmd_certify(args: argparse.Namespace) -> int:
    """Public handler: stay fail-closed until a reviewed MVP replaces this seam."""

    return _cmd_certify_disabled(args)


def _cmd_certify_legacy_research(args: argparse.Namespace) -> int:
    """Historical research workflow; deliberately not wired into the CLI."""

    problem, metadata = load_problem(Path(args.problem))
    model_hash = model_digest(problem)
    outcome = certify_problem(problem, model_hash)

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    if outcome.accepted:
        assert outcome.claim is not None and outcome.certificate is not None
        report_obj = verify_certificate(outcome.claim, model_hash, outcome.certificate)
        assert report_obj.checked_certificate is not None
        result = certified_result(report_obj.checked_certificate)
        _write_json(outdir / "claim.json", outcome.claim.to_dict())
        _write_json(outdir / "certificate.json", outcome.certificate.to_dict())
    else:
        result = unknown_result_for(model_hash, outcome)

    _write_json(outdir / "result.json", result.to_dict())
    (outdir / "problem.json").write_text(
        Path(args.problem).read_text(encoding="utf-8"), encoding="utf-8"
    )
    (outdir / "report.md").write_text(
        _report(problem, metadata, outcome, result.status), encoding="utf-8"
    )

    print(f"{result.status.value}  ({problem.problem_id})")
    if outcome.accepted and outcome.deviation_squared is not None:
        print(f"  deviation from requested target: {_format_deviation(outcome.deviation_squared)}")
        print(f"  chart: {outcome.chart}")
    else:
        for diagnostic in outcome.diagnostics:
            print(f"  {diagnostic}")
        print("  UNKNOWN does not mean infeasible -- see report.md")
    print(f"  artifacts: {outdir}")
    return EXIT_CERTIFIED if outcome.accepted else EXIT_NOT_CERTIFIED


def _reject_disabled_float(literal: str) -> NoReturn:
    raise ValidationError(
        f"problem file contains the float literal {literal}; quote it as a string "
        f'("{literal}") so it is parsed exactly'
    )


def _cmd_certify_disabled(args: argparse.Namespace) -> int:
    """Emit UNKNOWN without entering an unrefereed search/transformation path."""

    problem_path = Path(args.problem)
    try:
        raw_problem = problem_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read problem file {problem_path}: {exc}") from exc
    try:
        document = json.loads(raw_problem, parse_float=_reject_disabled_float)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"problem file is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValidationError("problem document must be a JSON object")

    problem_id = document.get("problem_id", "unidentified-problem")
    if not isinstance(problem_id, str) or not problem_id:
        problem_id = "unidentified-problem"
    diagnostics = (
        "certification is disabled because no E2-approved production checker is registered",
        "no search, chart transformation, or certificate construction was run",
    )
    model_hash = digest_json({"unreviewed_problem_document": document})
    result = unknown_result(
        digest_json({"unresolved": list(diagnostics)}),
        model_hash,
        diagnostics,
    )

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    _write_json(outdir / "result.json", result.to_dict())
    (outdir / "problem.json").write_text(raw_problem, encoding="utf-8")
    report = "\n".join(
        [
            f"# RoboCert result: {problem_id}",
            "",
            "**Status: `UNKNOWN`**",
            "",
            "No E2-approved production checker is registered. RoboCert did not run",
            "the legacy four-chart search, radian-to-half-angle conversion, or any",
            "certificate construction path.",
            "",
            "`UNKNOWN` is not infeasibility and establishes no mathematical or",
            "physical safety claim.",
            "",
        ]
    )
    (outdir / "report.md").write_text(report, encoding="utf-8")

    print(f"{ResultStatus.UNKNOWN.value}  ({problem_id})")
    for diagnostic in diagnostics:
        print(f"  {diagnostic}")
    print("  UNKNOWN does not mean infeasible -- see report.md")
    print(f"  artifacts: {outdir}")
    return EXIT_NOT_CERTIFIED


def unknown_result_for(model_hash: ArtifactDigest, outcome: CertificationOutcome) -> Any:
    from robocert.results import unknown_result

    # No claim was accepted, so there is no claim digest to bind to; use the
    # digest of the failure itself, which is at least reproducible.
    return unknown_result(
        digest_json({"unresolved": list(outcome.diagnostics)}),
        model_hash,
        outcome.diagnostics,
    )


def _cmd_check(args: argparse.Namespace) -> int:
    """Public handler: accept no artifacts until reviewed reconstruction exists."""

    del args
    print(ResultStatus.UNKNOWN.value, file=sys.stderr)
    print(
        "  no E2-approved production checker is registered; no artifact was accepted",
        file=sys.stderr,
    )
    return EXIT_NOT_CERTIFIED


def _cmd_check_legacy_research(args: argparse.Namespace) -> int:
    """Historical artifact check; deliberately not wired into the CLI."""

    outdir = Path(args.directory)
    claim_path = outdir / "claim.json"
    certificate_path = outdir / "certificate.json"
    problem_path = outdir / "problem.json"

    if not claim_path.is_file() or not certificate_path.is_file():
        print(
            f"no certificate to check in {outdir} (the run produced no accepted witness)",
            file=sys.stderr,
        )
        return EXIT_NOT_CERTIFIED

    problem, _ = load_problem(problem_path)
    model_hash = model_digest(problem)
    claim = Claim.from_dict(json.loads(claim_path.read_text(encoding="utf-8")))
    certificate = Certificate.from_dict(json.loads(certificate_path.read_text(encoding="utf-8")))

    report = verify_certificate(claim, model_hash, certificate)
    if not report.accepted:
        print(f"{unknown_from_check(report).status.value}", file=sys.stderr)
        for diagnostic in report.diagnostics:
            print(f"  {diagnostic}", file=sys.stderr)
        return EXIT_NOT_CERTIFIED

    assert report.checked_certificate is not None
    result = certified_result(report.checked_certificate)
    print(f"{result.status.value}  ({claim.claim_id})")
    print(f"  claim hash:  {result.claim_hash}")
    print(f"  model hash:  {result.model_hash}")
    print(f"  checker:     {certificate.checker_id} v{certificate.checker_version}")
    print(f"  arithmetic:  {certificate.arithmetic_mode}")
    print("  re-checked from stored artifacts; the solver was not run")
    return EXIT_CERTIFIED


def _cmd_schema(args: argparse.Namespace) -> int:
    print(json.dumps(schema_document(args.name), indent=2, sort_keys=True))
    return EXIT_CERTIFIED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="robocert",
        description=(
            "RoboCert research pre-alpha. The production certification gate is "
            "closed: certify and check currently return UNKNOWN without running "
            "the historical backend."
        ),
        epilog=(
            "For certify/check: 0 is reserved for an accepted certificate, 1 is "
            "UNKNOWN/not certified, and 2 is an input or I/O error. The schema "
            "command returns 0 after printing a schema. UNKNOWN does not mean the "
            "property is false or the target unreachable."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    certify = sub.add_parser(
        "certify", help="emit UNKNOWN while the production certification gate is closed"
    )
    certify.add_argument("problem", help="path to a problem JSON file")
    certify.add_argument("-o", "--output", required=True, help="directory for artifacts")
    certify.set_defaults(handler=_cmd_certify)

    check = sub.add_parser(
        "check", help="emit UNKNOWN; no stored certificate family is currently accepted"
    )
    check.add_argument("directory", help="directory produced by `robocert certify`")
    check.set_defaults(handler=_cmd_check)

    schema = sub.add_parser("schema", help="print a packaged JSON Schema")
    schema.add_argument("name", choices=sorted(SCHEMA_NAMES))
    schema.set_defaults(handler=_cmd_schema)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        exit_code: int = args.handler(args)
        return exit_code
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["build_parser", "main", "model_digest"]
