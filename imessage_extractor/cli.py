import click
from typing import Optional

from .commands import (
    export_chat_command,
    export_all_command,
    list_chats_command,
)


@click.group()
@click.version_option()
def cli():
    """Parse and Extract iMessage Conversations.

    A command-line tool to extract iMessage conversations from the macOS Messages database.
    Provides functionality to export individual chats to CSV or all chats to JSON format.
    """


@cli.command(name="export-chat")
@click.argument("participant")
@click.option("-o", "--output", type=click.Path(), help="Output CSV file path")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def export_chat(participant, output, db_path, verbose):
    """Export a chat conversation with a specific participant to CSV.

    Extracts messages from a chat thread containing the specified participant
    and saves them to a CSV file with detailed metadata.

    If multiple chats match the participant identifier, you will be prompted to
    select which chat to export.

    Args:
        participant: A substring of the phone number or email of the participant
                    (e.g. "+44" or "john@example.com")
        output: Path to the output CSV file. Defaults to "imessage_chat.csv"
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Example:
        imessage-extractor export-chat "+1234567890" -o my_conversation.csv
    """
    exit_code = export_chat_command(participant, output, db_path, verbose)
    return exit_code


@cli.command(name="export-all")
@click.option("-o", "--output", type=click.Path(), help="Output JSON file path")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def export_all(output, db_path, verbose):
    """Export all chat conversations to JSON.

    Extracts all messages from all chat threads and saves them to a JSON file.
    Messages are grouped by conversation thread with complete metadata.

    Chats are sorted by most recent activity, with the most recently active
    threads appearing first in the output.

    Args:
        output: Path to the output JSON file. Defaults to "imessage_all.json"
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Example:
        imessage-extractor export-all -o all_conversations.json
    """
    exit_code = export_all_command(output, db_path, verbose)
    return exit_code


@cli.command(name="list-chats")
@click.argument("participant")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def list_chats(participant, db_path, verbose):
    """List all chats with a specific participant.

    Displays information about all chat threads that include a participant
    whose identifier (phone number or email) contains the provided substring.

    Args:
        participant: A substring of the phone number or email of the participant
                    (e.g. "+44" or "john@example.com")
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Example:
        imessage-extractor list-chats "+1234567890"
    """
    exit_code = list_chats_command(participant, db_path, verbose)
    return exit_code
