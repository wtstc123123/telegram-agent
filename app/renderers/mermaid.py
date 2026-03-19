from pathlib import Path


class MermaidRenderer:
    """Placeholder renderer.

    In production, replace this with Mermaid CLI or a rendering microservice.
    The current implementation saves the Mermaid source to a .mmd file so you can
    inspect it immediately.
    """

    def __init__(self, base_dir: str = "tmp/diagrams") -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_source(self, session_id: str, mermaid_text: str) -> str:
        file_path = self.base_path / f"{session_id}.mmd"
        file_path.write_text(mermaid_text, encoding="utf-8")
        return str(file_path)
