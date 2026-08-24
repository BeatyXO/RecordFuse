"""Narrow Windows compatibility shim for the installed gltest Direct harness.

gltest replaces fd 0 with a temporary file and immediately unlinks it. Windows
keeps that descriptor open, so unlink raises WinError 32 before the contract is
loaded. Leave only those locked temp files in place; the OS cleans them up.
"""

import os
import tempfile


if os.name == "nt":
    _unlink = os.unlink
    _temp_dir = os.path.normcase(os.path.abspath(tempfile.gettempdir()))

    def _unlink_windows_gltest_safe(path, *args, **kwargs):
        try:
            return _unlink(path, *args, **kwargs)
        except PermissionError:
            candidate = os.path.normcase(os.path.abspath(os.fspath(path)))
            if not candidate.startswith(_temp_dir + os.sep):
                raise
            return None

    os.unlink = _unlink_windows_gltest_safe
