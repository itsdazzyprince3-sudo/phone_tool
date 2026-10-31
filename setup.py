#!/usr/bin/env python3
"""
setup.py — universal installer for the VirgoYT OSINT Toolkit.

Works on Android/Termux and on Linux PCs.

    python3 setup.py              # detect platform, pip-install, finish setup
    python3 setup.py install      # setuptools install + platform finishing
    pip install .                 # standard install (console script included)
    python3 setup.py deb          # build numbertrackervy_4.0.0_all.deb
    python3 setup.py test         # run the 10-point self-test suite
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import Command, setup
from setuptools.command.install import install

BASE_DIR = Path(__file__).resolve().parent
PACKAGE = "numbertrackervy"
VERSION = "5.0.0"
AUTHOR = "VIRGOYT707"
DESCRIPTION = "VirgoYT OSINT Toolkit — telecom metadata analysis and local evidence vault"

IS_TERMUX = (
    bool(os.environ.get("TERMUX_VERSION"))
    or "com.termux" in sys.prefix
    or Path("/data/data/com.termux/files/usr").is_dir()
)


def _run(cmd, check=False):
    print("  $ " + " ".join(str(part) for part in cmd))
    return subprocess.call([str(part) for part in cmd])


def _have(module):
    try:
        __import__(module)
        return True
    except Exception:
        return False


def _user_home():
    home = Path.home()
    if hasattr(os, "geteuid") and os.geteuid() == 0 and os.environ.get("SUDO_USER"):
        try:
            import pwd

            home = Path(pwd.getpwnam(os.environ["SUDO_USER"]).pw_dir)
        except Exception:
            pass
    return home


def _data_dir():
    home = _user_home()
    if IS_TERMUX:
        return home / "phone_tool"
    xdg = os.environ.get("XDG_DATA_HOME")
    return (Path(xdg) / "virgoyt") if xdg else (home / ".local" / "share" / "virgoyt")


def _ensure_phonenumbers():
    if _have("phonenumbers"):
        return True
    print("[setup] phonenumbers is missing; installing it with pip...")
    if _run([sys.executable, "-m", "pip", "install", "phonenumbers"]) == 0 and _have("phonenumbers"):
        return True
    if IS_TERMUX:
        print("[setup] run: pkg install python && pip install phonenumbers")
    else:
        print("[setup] run: sudo apt install python3-phonenumbers  (or pip install phonenumbers)")
    return False


def post_install():
    """Platform-aware finishing steps shared by install and bare setup."""
    data_dir = _data_dir()
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"[setup] evidence vault: {data_dir}")
    except Exception as exc:
        print(f"[setup] warning: could not create {data_dir}: {exc}")

    _ensure_phonenumbers()

    if shutil.which("git") is None:
        if IS_TERMUX:
            print("[setup] note: git not found; install with: pkg install git")
        else:
            print("[setup] note: git not found; install with: sudo apt install git")

    exe = shutil.which(PACKAGE)
    if exe:
        print(f"[setup] command ready: {exe}")
    else:
        print(f"[setup] command '{PACKAGE}' is not on PATH yet; re-open the shell or add the scripts directory to PATH")

    print("[setup] done. launch with: numbertrackervy")


class SmartInstall(install):
    """setuptools install plus platform finishing steps."""

    def run(self):
        install.run(self)
        post_install()


class TestCommand(Command):
    description = "run the VirgoYT 10-point self-test suite"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.path.insert(0, str(BASE_DIR))
        from virgoyt.test_suite import run_all_tests

        result = run_all_tests()
        if result.get("failed", 0):
            raise SystemExit(1)


class DebCommand(Command):
    description = "build a Debian .deb package (works on Termux and Linux)"
    user_options = [("output=", "o", "output directory (default: dist)")]

    def initialize_options(self):
        self.output = "dist"

    def finalize_options(self):
        self.output = str(Path(self.output).resolve())

    def run(self):
        dpkg = shutil.which("dpkg-deb")
        if not dpkg:
            raise SystemExit("[deb] dpkg-deb not found; install dpkg or build on Debian/Ubuntu")

        root = BASE_DIR / "build" / "deb" / f"{PACKAGE}_{VERSION}_all"
        if root.exists():
            shutil.rmtree(root)

        bin_dir = root / "usr" / "bin"
        lib_dir = root / "usr" / "lib" / "python3" / "dist-packages"
        doc_dir = root / "usr" / "share" / "doc" / PACKAGE
        ctl_dir = root / "DEBIAN"
        for directory in (bin_dir, lib_dir, doc_dir, ctl_dir):
            directory.mkdir(parents=True, exist_ok=True)

        launcher = bin_dir / PACKAGE
        source = (BASE_DIR / "phone_tool.py").read_text(encoding="utf-8")
        launcher.write_text(
            source.replace("#!/usr/bin/env python3", "#!/usr/bin/python3", 1),
            encoding="utf-8",
        )
        launcher.chmod(0o755)

        shutil.copytree(
            BASE_DIR / "virgoyt",
            lib_dir / "virgoyt",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )

        shutil.copy2(BASE_DIR / "README.md", doc_dir / "README.md")
        (doc_dir / "copyright").write_text(
            "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\n"
            f"Upstream-Name: {PACKAGE}\n"
            "Source: https://github.com/itsdazzyprince3-sudo/phone_tool\n\n"
            "Files: *\n"
            f"Copyright: {AUTHOR}\n"
            "License: MIT\n",
            encoding="utf-8",
        )

        control = (
            f"Package: {PACKAGE}\n"
            f"Version: {VERSION}\n"
            "Section: utils\n"
            "Priority: optional\n"
            "Architecture: all\n"
            "Depends: python3 (>= 3.8), python3-phonenumbers\n"
            f"Maintainer: {AUTHOR} <virgoyt707@users.noreply.github.com>\n"
            "Description: VirgoYT OSINT telecom metadata toolkit\n"
            " Analyze phone numbers against numbering-plan metadata, score risk\n"
            " with transparent signals, and store case evidence in a local SQLite vault.\n"
        )
        control_file = ctl_dir / "control"
        control_file.write_text(control, encoding="utf-8")
        control_file.chmod(0o644)

        root.chmod(0o755)
        for path in root.rglob("*"):
            if path.is_dir():
                path.chmod(0o755)
        launcher.chmod(0o755)

        out_dir = Path(self.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        deb = out_dir / f"{PACKAGE}_{VERSION}_all.deb"
        code = _run([dpkg, "--build", "--root-owner-group", str(root), str(deb)])
        if code != 0:
            raise SystemExit(code)
        print(f"[deb] built: {deb}")
        print(f"[deb] install with: sudo apt install {deb}")


def _full_setup():
    print(f"[setup] platform: {'Termux/Android' if IS_TERMUX else 'Linux PC'}")
    code = _run([sys.executable, "-m", "pip", "install", "."])
    if code != 0:
        print("[setup] pip install failed; retrying with --user...")
        code = _run([sys.executable, "-m", "pip", "install", "--user", "."])
    if code != 0:
        if IS_TERMUX:
            print("[setup] run manually: pip install .")
        else:
            print("[setup] run manually: pipx install .  or  sudo apt install ./dist/numbertrackervy_4.0.0_all.deb")
        raise SystemExit(code)
    post_install()


if len(sys.argv) == 1:
    _full_setup()
    raise SystemExit(0)


setup(
    name=PACKAGE,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    license="MIT",
    python_requires=">=3.8",
    packages=["virgoyt"],
    py_modules=["phone_tool"],
    install_requires=["phonenumbers>=8.12.0"],
    entry_points={
        "console_scripts": [
            f"{PACKAGE}=phone_tool:main",
            "virgoyt=phone_tool:main",
        ]
    },
    cmdclass={
        "install": SmartInstall,
        "test": TestCommand,
        "deb": DebCommand,
    },
    include_package_data=True,
    zip_safe=False,
)
