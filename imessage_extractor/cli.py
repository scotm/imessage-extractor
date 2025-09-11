import click
from .database import IMessageDatabase


@click.group()
@click.version_option()
def cli():
    """Parse and Extract iMessage Conversations.

    A command-line tool to extract iMessage conversations from the macOS Messages database.
    Provides functionality to export individual chats to CSV or all chats to JSON format.
    """


@cli.command(name="export-chat")
@click.argument("participant")
@click.option("-o", "--output", type=click.Path(), help="Output CSV file path", default="imessage_chat.csv")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
def export_chat_command(participant, output, db_path):
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

    Example:
        imessage-extractor export-chat "+1234567890" -o my_conversation.csv
    """
    db = IMessageDatabase(db_path)

    # Find chats matching the participant
    candidates = db.find_chat_by_participant(participant)

    if not candidates:
        click.echo("No chats found with the specified participant.")
        return

    # Display chat options if multiple found
    if len(candidates) > 1:
        click.echo("Multiple chats found. Please select one:")
        for i, chat in enumerate(candidates):
            click.echo(f"{i+1}. {chat['display_name'] or chat['chat_identifier']} - Participants: {chat['participants']}")

        choice = click.prompt("Enter the number of the chat to export", type=int)
        if choice < 1 or choice > len(candidates):
            click.echo("Invalid choice.")
            return

        chat_rowid = candidates[choice-1]["rowid"]
    else:
        chat_rowid = candidates[0]["rowid"]
        chat_name = candidates[0]["display_name"] or candidates[0]["chat_identifier"]
        click.echo(f"Exporting chat: {chat_name}")

    # Export the chat
    db.export_chat_to_csv(chat_rowid, output)
    click.echo(f"Chat exported to {output}")


@cli.command(name="export-all")
@click.option("-o", "--output", type=click.Path(), help="Output JSON file path", default="imessage_all.json")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
def export_all_command(output, db_path):
    """Export all chat conversations to JSON.

    Extracts all messages from all chat threads and saves them to a JSON file.
    Messages are grouped by conversation thread with complete metadata.

    Chats are sorted by most recent activity, with the most recently active
    threads appearing first in the output.

    Args:
        output: Path to the output JSON file. Defaults to "imessage_all.json"
        db_path: Optional path to chat.db file if not using the default location

    Example:
        imessage-extractor export-all -o all_conversations.json
    """
    db = IMessageDatabase(db_path)

    # Export all chats
    db.export_all_chats_to_json(output)
    click.echo(f"All chats exported to {output}")


@cli.command(name="list-chats")
@click.argument("participant")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
def list_chats_command(participant, db_path):
    """List all chats with a specific participant.

    Displays information about all chat threads that include a participant
    whose identifier (phone number or email) contains the provided substring.

    Args:
        participant: A substring of the phone number or email of the participant
                    (e.g. "+44" or "john@example.com")
        db_path: Optional path to chat.db file if not using the default location

    Example:
        imessage-extractor list-chats "+1234567890"
    """
    db = IMessageDatabase(db_path)

    # Find chats matching the participant
    candidates = db.find_chat_by_participant(participant)

    if not candidates:
        click.echo("No chats found with the specified participant.")
        return

    click.echo(f"Found {len(candidates)} chat(s):")
    for i, chat in enumerate(candidates):
        display_name = chat["display_name"] or "Unnamed chat"
        participants = chat["participants"]
        click.echo(f"{i+1}. {display_name}")
        click.echo(f"   Identifier: {chat['chat_identifier']}")
        click.echo(f"   Participants: {participants}")
        click.echo()
