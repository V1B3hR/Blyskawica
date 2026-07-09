"""
Smoke tests for Nethical Recon package
These tests verify basic functionality is working
"""

from nethical_recon import __author__, __version__


def test_version():
    """Test that version is defined"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_author():
    """Test that author is defined"""
    assert __author__ is not None
    assert isinstance(__author__, str)


def test_package_import():
    """Test that the main package can be imported"""
    import nethical_recon

    assert nethical_recon is not None


def test_cli_import():
    """Test that CLI module can be imported"""
    from nethical_recon import cli

    assert cli is not None
    assert hasattr(cli, "main")
    assert hasattr(cli, "app")


def test_cli_app_structure():
    """Test that CLI app has expected commands"""
    from nethical_recon.cli import app

    # Get registered commands - Typer stores them differently
    commands = []
    for cmd in app.registered_commands:
        if hasattr(cmd, "callback") and cmd.callback:
            commands.append(cmd.callback.__name__)

    # Get registered subapps/groups
    subapps = []
    for group in app.registered_groups:
        if hasattr(group, "name"):
            subapps.append(group.name)

    # Check for expected commands
    expected_commands = ["version", "interactive", "scan", "report"]
    for cmd in expected_commands:
        assert cmd in commands, f"Expected command '{cmd}' not found in CLI. Found: {commands}"

    # Check for expected subapps
    expected_subapps = ["job"]
    for subapp in expected_subapps:
        assert subapp in subapps, f"Expected subapp '{subapp}' not found in CLI. Found: {subapps}"
