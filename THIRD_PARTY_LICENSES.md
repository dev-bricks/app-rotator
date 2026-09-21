# Third-Party Licenses & Software Inventory

- **Project:** `App Rotator` (`dev-bricks/app-rotator`)
- **License:** [MIT License](LICENSE)
- **Version:** `0.2.3`
- **Audit Date:** 2026-09-21
- **Organization:** [dev-bricks](https://github.com/dev-bricks)
- **Umbrella Ecosystem:** [open-bricks](https://github.com/open-bricks)
- **Security & Non-Elevation:** Non-elevation user-mode (`RunAsInvoker`) under `%LOCALAPPDATA%`
- **Zero-Copyleft Guarantee:** MIT application layer; third-party dependencies are permissively licensed (MIT, BSD-3-Clause, HPND) with LGPL-3.0 dynamic link isolation (`pystray`)

This document provides a Level 1 Software Bill of Materials (SBOM) and inventory of third-party dependencies, libraries, and runtime components utilized by **App Rotator** (`dev-bricks/app-rotator`).

---

## 1. Direct Python Dependencies

| Package | Version Constraint | License | Project URL | Purpose in App Rotator |
| :--- | :--- | :--- | :--- | :--- |
| **Pillow** | `>=10.0` | HPND-like (Historical Permission Notice and Disclaimer) | https://python-pillow.org/ | System tray icon rasterization, PNG/ICO loading, and state badge generation. |
| **psutil** | `>=5.9` | BSD-3-Clause | https://github.com/giampaolo/psutil | Process enumeration, path introspection, memory inspection, and graceful termination. |
| **pystray** | `>=0.19` | LGPL-3.0 / GPL-3.0 | https://github.com/moses-palmer/pystray | Windows system tray icon management, contextual popup menus, and background event handling (dynamically linked). |

---

## 2. Development & Build Dependencies

| Package | Version Constraint | License | Project URL | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **pytest** | `>=8.0` | MIT | https://pytest.org/ | Test framework for unit, integration, and metadata contract testing. |
| **ruff** | `>=0.6` | MIT / Apache-2.0 | https://astral.sh/ruff | Fast Python linter and static analysis engine. |
| **setuptools** | `>=69.0` | MIT | https://github.com/pypa/setuptools | PEP 517 / 621 package build and distribution backend. |

---

## 3. Platform & Runtime Components

| Component | Minimum Version | License | Distributor | Usage & Boundaries |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | `>=3.11` | Python Software Foundation (PSF) License | Python Software Foundation | Core execution runtime. |
| **Windows Shell (explorer.exe)** | Windows 10/11 | Microsoft Proprietary EULA | Microsoft Corporation | AppX / UWP modern application activation via `shell:AppsFolder\<AUMID>`. |
| **PowerShell Core / Windows PowerShell** | `>=5.1` | MIT / Microsoft EULA | Microsoft Corporation | Desktop shortcut installation script (`install-desktop-shortcut.ps1`). |

---

## 4. Invariant Cross-Reference Matrix

The 10 Governance and Runtime Invariants of `app-rotator` are mapped directly to supply chain and operational boundaries:

| Invariant ID | Name | Dependency / Boundary | Verification Rule |
| :--- | :--- | :--- | :--- |
| `INV-LOCAL-01` | **100% Local-First Privacy** | Pure local runtime, zero sockets | Automated contract tests verify zero outbound HTTP/network requests |
| `INV-UNPRIV-02` | **Unprivileged Execution (RunAsInvoker)** | Win32 unprivileged user context | `SECURITY.md` and runtime checks verify non-elevated operation |
| `INV-DRYRUN-03` | **Fail-Closed & Dry-Run by Default** | Engine configuration schema | Clean installation test verifies no process actions without opt-in |
| `INV-SCOPING-04` | **Strict Path-Restricted Process Scoping** | `psutil` process introspection | Rejects unmatched process names or ambiguous executable paths |
| `INV-ATOMIC-05` | **Atomic Persistence & Mailbox IPC** | `os.replace` & temporary files | State and mailbox writes execute via temporary file + atomic replacement |
| `INV-DELEGATION-06` | **Provider Delegation Contract** | External CLI (`controller.exe`) | Zero direct reads or modifications of provider internal configuration files |
| `INV-LOCKFILE-07` | **Single-Instance Mutex Lock** | `app-rotator.lock` file mutex | Exclusive file lock prevents concurrent engine or tray execution |
| `INV-AUMID-08` | **Non-Invasive AppX Shell Activation** | `explorer.exe shell:AppsFolder/` | Subprocess invocations use fixed parameter vectors without shell execution |
| `INV-SYNC-09` | **Cloud-Sync & Conflict Resilience** | `%LOCALAPPDATA%` path & `.gitignore` | State stored outside OneDrive; `.gitignore` contains sync conflict filters |
| `INV-SLA-10` | **48h Security SLA & 5-Day Triage** | Security policy & maintainers | Published commitments in `SECURITY.md`, `README.md`, `README_de.md` |

---

## 5. License Texts Summary

### 5.1. MIT License
*App Rotator, pytest, ruff, setuptools*
```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 5.2. BSD-3-Clause License
*psutil*
```text
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
```

### 5.3. HPND License
*Pillow*
```text
The Python Imaging Library (PIL) is
    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh
    Copyright © 2010-2024 by Jeffrey A. Clark and contributors

By obtaining, using, and/or copying this software and/or its associated
documentation, you agree that you have read, understood, and will comply
with the following terms and conditions:

Permission to use, copy, modify, and distribute this software and its
associated documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appears in all copies, and that
both that copyright notice and this permission notice appear in supporting
documentation.
```

### 5.4. LGPL-3.0 License
*pystray*
```text
This library is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at your
option) any later version.
```
