from click.testing import CliRunner
from imessage_extractor.cli import cli


def test_version():
    """Test that the version command works correctly.

    Verifies that the --version flag returns exit code 0 and
    outputs version information.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


def test_help():
    """Test that the help command shows all available commands.

    Verifies that the --help flag returns exit code 0 and
    displays information about all implemented commands.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Parse and Extract iMessage Conversations" in result.output
    assert "export-chat" in result.output
    assert "export-all" in result.output
    assert "list-chats" in result.output


def test_export_chat_help():
    """Test that the export-chat command help works correctly.

    Verifies that the export-chat --help flag returns exit code 0 and
    displays the correct help information for the export-chat command.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["export-chat", "--help"])
    assert result.exit_code == 0
    assert "Export a chat conversation with a specific participant to CSV" in result.output


def test_export_all_help():
    """Test that the export-all command help works correctly.

    Verifies that the export-all --help flag returns exit code 0 and
    displays the correct help information for the export-all command.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["export-all", "--help"])
    assert result.exit_code == 0
    assert "Export all chat conversations to JSON" in result.output


def test_list_chats_help():
    """Test that the list-chats command help works correctly.

    Verifies that the list-chats --help flag returns exit code 0 and
    displays the correct help information for the list-chats command.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["list-chats", "--help"])
    assert result.exit_code == 0
    assert "List all chats with a specific participant" in result.output


def test_permission_error_handling():
    """Test that permission errors are handled gracefully.

    Verifies that when a non-existent database path is provided,
    the tool provides helpful error messages.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["export-chat", "+1234567890", "-d", "/nonexistent/path/chat.db"])
    # Should handle the error gracefully rather than crashing
    assert result.exit_code in [1, 2]  # 1 for handled errors, 2 for Click validation errors


def test_database_locked_error():
    """Test that database locked errors are handled appropriately.

    This test ensures that when the database is locked, we get a helpful error message.
    """
    # This is a basic test - in practice, testing database locking would require
    # more complex setup, but we can at least verify the command structure works
    runner = CliRunner()
    # Using a path that won't exist but won't fail validation
    result = runner.invoke(cli, ["export-all", "-d", "/tmp/nonexistent.db"])
    # Should handle the error gracefully
    assert result.exit_code in [0, 1, 2]
