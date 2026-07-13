# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

_name = "World"
_template = "Hello, {name}!"
kernel = None

def name():
    return _name

def set_name(name):
    global _name
    _name = name
    if kernel:
        kernel.mark_revision("name", "setName")
        kernel.mark_revision("first_name", "setName")

def greeting():
    return _template.format(name=_name)

def setup(kernel):
    meta = kernel.metadata.get("Greeting", {})
    global _name, _template
    _name = meta.get("initial_name", _name)
    _template = meta.get("greeting_template", _template)
