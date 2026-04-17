"""
seeds/patch_document_service.py

OPTIONAL: Applies a clean patch to document_service.py so that
_prepare_template_data() and _generate_pdf_from_template() both
accept an optional `override_dt` parameter.

This lets you pass any past datetime when regenerating PDFs so the
date printed on the document matches the fake transaction date.

HOW TO USE:
    # Apply the patch once:
    python -m seeds.patch_document_service

    # Then regenerate all backdated PDFs:
    python -m seeds.backdate_pdfs

The patch is safe to run multiple times — it checks whether it has
already been applied before modifying the file.
"""

import re
from pathlib import Path

SERVICE_FILE = Path(__file__).resolve().parents[1] / "app" / "services" / "document_service.py"

PATCH_MARKER = "# SEED_PATCH: override_dt applied"

OLD_PREPARE = '''\
def _prepare_template_data(form_data: dict) -> dict:
    now = datetime.now()'''

NEW_PREPARE = '''\
def _prepare_template_data(form_data: dict, override_dt=None) -> dict:  # SEED_PATCH: override_dt applied
    now = override_dt or datetime.now()'''

OLD_GENERATE = '''\
def _generate_pdf_from_template(
    template_bytes: bytes,
    form_data: dict
) -> bytes:
    try:
        tpl = DocxTemplate(BytesIO(template_bytes))
        template_data = _prepare_template_data(form_data)'''

NEW_GENERATE = '''\
def _generate_pdf_from_template(
    template_bytes: bytes,
    form_data: dict,
    override_dt=None,               # SEED_PATCH: accepts back-date override
) -> bytes:
    try:
        tpl = DocxTemplate(BytesIO(template_bytes))
        template_data = _prepare_template_data(form_data, override_dt=override_dt)'''


def apply_patch():
    if not SERVICE_FILE.exists():
        print(f"❌  File not found: {SERVICE_FILE}")
        return False

    source = SERVICE_FILE.read_text(encoding="utf-8")

    if PATCH_MARKER in source:
        print("✅  Patch already applied — nothing to do.")
        return True

    patched = source.replace(OLD_PREPARE, NEW_PREPARE)
    if patched == source:
        print("⚠   Could not find _prepare_template_data signature. Check indentation.")
        return False

    patched = patched.replace(OLD_GENERATE, NEW_GENERATE)

    SERVICE_FILE.write_text(patched, encoding="utf-8")
    print(f"✅  Patch applied to {SERVICE_FILE}")
    return True


if __name__ == "__main__":
    apply_patch()