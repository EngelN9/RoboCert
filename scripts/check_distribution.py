#!/usr/bin/env python3
"""Inspect RoboCert distributions and smoke-test a clean wheel installation."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path

SCHEMA_NAMES = frozenset(
    {
        "certificate.schema.json",
        "claim.schema.json",
        "problem.schema.json",
        "result.schema.json",
    }
)


class DistributionError(RuntimeError):
    """A built artifact is missing required content or fails clean installation."""


def _exactly_one(paths: list[Path], description: str) -> Path:
    if len(paths) != 1:
        rendered = ", ".join(path.name for path in paths) or "none"
        raise DistributionError(f"expected exactly one {description}, found: {rendered}")
    return paths[0]


def _required_package_files(repo_root: Path) -> set[str]:
    package_root = repo_root / "src" / "robocert"
    source_files = {
        f"robocert/{path.relative_to(package_root).as_posix()}"
        for path in package_root.rglob("*")
        if path.is_file() and (path.suffix == ".py" or path.name == "py.typed")
    }
    schema_files = {f"robocert/schemas/{name}" for name in SCHEMA_NAMES}
    return source_files | schema_files


def _check_wheel(wheel_path: Path, required_files: set[str]) -> None:
    with zipfile.ZipFile(wheel_path) as archive:
        members = set(archive.namelist())
    missing = sorted(required_files - members)
    if missing:
        raise DistributionError(f"wheel is missing required files: {', '.join(missing)}")


def _check_sdist(sdist_path: Path, required_files: set[str]) -> None:
    package_suffixes = {
        f"/src/{relative}"
        for relative in required_files
        if not relative.startswith("robocert/schemas/")
    }
    required_suffixes = package_suffixes | {f"/schemas/{name}" for name in SCHEMA_NAMES}

    with tarfile.open(sdist_path, mode="r:gz") as archive:
        members = set(archive.getnames())
    missing = sorted(
        suffix
        for suffix in required_suffixes
        if not any(member.endswith(suffix) for member in members)
    )
    if missing:
        raise DistributionError(f"sdist is missing required files: {', '.join(missing)}")


def _venv_python(environment_dir: Path) -> Path:
    if os.name == "nt":
        return environment_dir / "Scripts" / "python.exe"
    return environment_dir / "bin" / "python"


def _run_checked(command: list[str], cwd: Path, environment: dict[str, str]) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = completed.stdout + completed.stderr
        raise DistributionError(f"command failed ({' '.join(command)}):\n{output}")


def _clean_install_smoke_test(
    wheel_path: Path,
    work_dir: Path,
    module_names: tuple[str, ...],
) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="robocert-wheel-smoke-", dir=work_dir) as temporary:
        temporary_path = Path(temporary)
        environment_dir = temporary_path / "venv"
        venv.EnvBuilder(with_pip=True).create(environment_dir)
        python = _venv_python(environment_dir)
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

        _run_checked(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                str(wheel_path),
            ],
            temporary_path,
            environment,
        )
        smoke_code = (
            "import importlib; "
            "from robocert.checking import production_checker_families; "
            "from robocert.schemas import SCHEMA_NAMES, schema_document; "
            f"expected_schemas = {sorted(SCHEMA_NAMES)!r}; "
            "assert sorted(SCHEMA_NAMES) == expected_schemas; "
            "assert production_checker_families() == (); "
            "[schema_document(name) for name in expected_schemas]; "
            f"[importlib.import_module('robocert.' + name) for name in {module_names!r}]"
        )
        _run_checked([str(python), "-c", smoke_code], temporary_path, environment)


def check_distributions(dist_dir: Path, work_dir: Path, repo_root: Path) -> tuple[Path, Path]:
    """Validate archive contents and a clean wheel installation."""

    dist_dir = dist_dir.resolve()
    wheel_path = _exactly_one(sorted(dist_dir.glob("robocert-*.whl")), "wheel")
    sdist_path = _exactly_one(sorted(dist_dir.glob("robocert-*.tar.gz")), "sdist")
    required_files = _required_package_files(repo_root)
    _check_wheel(wheel_path, required_files)
    _check_sdist(sdist_path, required_files)

    module_names = tuple(
        sorted(
            path.stem
            for path in (repo_root / "src" / "robocert").glob("*.py")
            if path.name != "__init__.py"
        )
    )
    _clean_install_smoke_test(wheel_path.resolve(), work_dir.resolve(), module_names)
    return wheel_path, sdist_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist_dir", type=Path)
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path(".package-smoke"),
        help="parent for disposable clean-install environments",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        wheel_path, sdist_path = check_distributions(args.dist_dir, args.work_dir, repo_root)
    except (DistributionError, OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: inspected {wheel_path.name} and {sdist_path.name}; clean wheel install passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
