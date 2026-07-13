# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

import sys

if "Greeting" not in sys.modules:
    import importlib.util
    from pathlib import Path
    _p = Path(__file__).parent.parent.parent / "Greeting" / "Greeting.py"
    _spec = importlib.util.spec_from_file_location("Greeting", _p)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["Greeting"] = _mod
    _spec.loader.exec_module(_mod)

import Greeting

_last_name = ""
_template = "{last}, {full}! From Russia with love."
kernel = None

def last_name():
    return _last_name

def set_last_name(last_name):
    global _last_name
    _last_name = last_name
    if kernel:
        kernel.mark_revision("last_name", "setLastName")

def set_name(full_name):
    parts = full_name.split(maxsplit=1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""
    Greeting.setName(first)
    set_last_name(last)

def set_first_name(first_name):
    Greeting.setName(first_name)

def name():
    last = _last_name
    first = Greeting.name()
    return f"{first} {last}" if last else first

def greeting():
    return _template.format(last=_last_name, full=name(), first=Greeting.name())

def setup(kernel):
    meta = kernel.metadata.get("Bondiana", {})
    global _template
    Greeting.setName(meta.get("initial_first_name", "James"))
    set_last_name(meta.get("initial_last_name", "Bond"))
    _template = meta.get("greeting_template", _template)
