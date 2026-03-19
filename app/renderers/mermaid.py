import re
from pathlib import Path


# Allow only safe filename characters: alphanumerics, hyphens, underscores,
# and colons (used in "telegram:<chat_id>" session IDs).  Everything else is
# replaced with an underscore so the final filename stays inside base_dir.
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9:\-_]")


class MermaidRenderer:
    """Placeholder renderer.

    In production, replace this with Mermaid CLI or a rendering microservice.
    The current implementation saves the Mermaid source to a .mmd file so you can
    inspect it immediately.
    """

    def __init__(self, base_dir: str = "tmp/diagrams") -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_filename(session_id: str) -> str:
        """Return a safe filename component derived from *session_id*.

        Strips any path separators and characters that could be used for
        directory traversal, keeping only ``[A-Za-z0-9:_-]``.
        """
        sanitized = _SAFE_FILENAME_RE.sub("_", session_id)
        # Guarantee we always have at least one character.
        return sanitized or "_"

    def save_source(self, session_id: str, mermaid_text: str) -> str:
        filename = self._safe_filename(session_id)
        file_path = self.base_path / f"{filename}.mmd"
        file_path.write_text(mermaid_text, encoding="utf-8")
        return str(file_path)
