import json
import subprocess
import sys


def test_cli_health_command_outputs_json() -> None:
    result = subprocess.run(
        [sys.executable, "bin/radar.py", "health"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    assert payload["surface"] == "cli"
