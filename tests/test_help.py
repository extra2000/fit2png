import subprocess

CLI = ".venv/bin/fit2png-cli"

def test_cli_help() -> None:
    """Test that the fit2png-cli --help command runs successfully."""
    # Run the command
    result = subprocess.run(
        [CLI, "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    # Check that it executed successfully (return code 0)
    assert result.returncode == 0

    # Verify that the expected help text is in the standard output
    assert "usage:" in result.stdout.lower()
    assert "show this help message and exit" in result.stdout.lower()
    assert "fit" in result.stdout  # Checking for one of the subparsers
