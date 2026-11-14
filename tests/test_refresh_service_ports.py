import importlib.util
import sys
import types
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_module(relative, stubs=None, name="tested_module"):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, stubs or {}):
        spec.loader.exec_module(module)
    return module


def settings_stubs():
    settings = types.ModuleType("openplotterSettings")
    for name in ("conf", "platform", "language"):
        setattr(settings, name, types.SimpleNamespace())
    return {"openplotterSettings": settings, "ujson": json}


class DashboardPortsTest(unittest.TestCase):
    def test_repeated_queries_are_snapshots(self):
        stubs = settings_stubs()
        stubs["openplotterSettings"].language.Language = mock.Mock()
        stubs["openplotterSettings"].platform.Platform = mock.Mock()
        module = load_module("openplotterDashboards/ports.py", stubs)
        ports = module.Ports(mock.Mock(), "en")
        with mock.patch.object(
            module.subprocess, "check_output", return_value=b"active"
        ):
            self.assertEqual(len(ports.usedPorts()), 2)
            self.assertEqual(len(ports.usedPorts()), 2)
        with mock.patch.object(
            module.subprocess,
            "check_output",
            side_effect=module.subprocess.CalledProcessError(3, "systemctl"),
        ):
            self.assertEqual(ports.usedPorts(), [])


if __name__ == "__main__":
    unittest.main()
