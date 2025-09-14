import os
import shutil
from typing import Dict, Any, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from PIL import Image

from .parsers import TextParser

class HTMLExporter:
    """Handles the generation of HTML chat exports."""

    def __init__(self, output_dir: str, attachment_path: str):
        self.output_dir = output_dir
        self.attachment_path = attachment_path
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

        self.html_output_path = os.path.join(self.output_dir, "index.html")
        self.styles_output_dir = os.path.join(self.output_dir, "styles")
        self.attachments_output_dir = os.path.join(self.output_dir, "attachments")

    def _prepare_output_directory(self):
        """Creates necessary output directories."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.styles_output_dir, exist_ok=True)
        os.makedirs(self.attachments_output_dir, exist_ok=True)

    def _copy_assets(self):
        """Copies static assets like CSS and any graphics."""
        # Copy CSS file
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "styles", "chat.css"),
            os.path.join(self.styles_output_dir, "chat.css")
        )
        # TODO: Copy simple and elegant graphics if available/designed.

    def _copy_attachment(self, attachment_info: Dict[str, Any], message_id: int) -> Dict[str, str]:
        """Copies an attachment, converts images to PNG, and returns new path and mime type."""
        original_path = attachment_info.get("path")
        if not original_path:
            return None

        full_original_path = os.path.expanduser(original_path)
        if not os.path.exists(full_original_path):
            full_original_path = os.path.join(self.attachment_path, original_path)

        if not os.path.exists(full_original_path):
            return None

        original_filename = os.path.basename(original_path)
        base_new_filename = f"{message_id}_{original_filename}"
        
        detected_mime_type = TextParser.detect_mime_type(full_original_path).lower()
        is_image = detected_mime_type.startswith("image/")
        new_filename = base_new_filename

        sub_dir = "documents"
        if is_image:
            sub_dir = "images"
            new_filename = os.path.splitext(base_new_filename)[0] + ".png"
        elif detected_mime_type.startswith("video/"):
            sub_dir = "videos"
        elif detected_mime_type.startswith("audio/"):
            sub_dir = "audio"

        type_specific_dir = os.path.join(self.attachments_output_dir, sub_dir)
        os.makedirs(type_specific_dir, exist_ok=True)
        new_attachment_path = os.path.join(type_specific_dir, new_filename)

        final_mime_type = detected_mime_type

        if is_image:
            try:
                with Image.open(full_original_path) as img:
                    img.save(new_attachment_path, "PNG")
                final_mime_type = "image/png"
            except Exception:
                shutil.copy(full_original_path, new_attachment_path)
        else:
            shutil.copy(full_original_path, new_attachment_path)
        
        return {"copied_path": os.path.relpath(new_attachment_path, self.output_dir), "mime": final_mime_type, "name": attachment_info.get("name")}

    def export_chat(self, chat_data: Dict[str, Any], messages: List[Dict[str, Any]]):
        """Exports chat data and messages to an HTML file."""
        self._prepare_output_directory()
        self._copy_assets()

        processed_messages = []
        for msg in messages:
            msg_copy = msg.copy()
            if msg_copy.get("attachments"):
                copied_attachments = []
                for att in msg_copy["attachments"]:
                    copied_attachment_info = self._copy_attachment(att, msg_copy["id"])
                    if copied_attachment_info:
                        copied_attachments.append(copied_attachment_info)
                msg_copy["attachments"] = copied_attachments
            processed_messages.append(msg_copy)

        template = self.env.get_template("chat_template.html")
        
        # Group messages by date for display
        messages_by_date = {}
        for msg in processed_messages:
            if msg.get("timestamp"):
                # Assuming timestamp is ISO format
                msg_date = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d")
                if msg_date not in messages_by_date:
                    messages_by_date[msg_date] = []
                messages_by_date[msg_date].append(msg)
            else:
                # Handle messages without timestamp (e.g., add to a 'No Date' group)
                if "No Date" not in messages_by_date:
                    messages_by_date["No Date"] = []
                messages_by_date["No Date"].append(msg)
        
        # Sort dates for display
        sorted_dates = sorted(messages_by_date.keys())
        
        # Prepare context for template
        context = {
            "chat": chat_data,
            "messages_by_date": {date: messages_by_date[date] for date in sorted_dates},
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_messages": len(messages)
        }

        with open(self.html_output_path, "w", encoding="utf-8") as f:
            f.write(template.render(context))
