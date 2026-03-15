"""Low-cost checks for report hygiene and generated artifact policy."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    errors: list[str] = []

    report_dir = Path("reports")
    if not report_dir.exists():
        errors.append("Missing reports/ directory")

    disallowed_pdf_roots = [Path("reports"), Path("artifacts")]
    disallowed_pdfs: list[Path] = []
    for root in disallowed_pdf_roots:
        if root.exists():
            disallowed_pdfs.extend(root.glob("**/*.pdf"))
    if disallowed_pdfs:
        names = ", ".join(str(p) for p in disallowed_pdfs)
        errors.append(f"PDF files found under reports/artifacts; keep generated outputs out of git: {names}")

    backlog = Path("reports/backlog.md")
    if not backlog.exists():
        errors.append("Missing reports/backlog.md")

    if errors:
        raise SystemExit("Report hygiene check failed:\n- " + "\n- ".join(errors))

    print("Report hygiene check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
