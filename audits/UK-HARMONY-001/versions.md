# Environment & Dependency Lock (UK-HARMONY-001)

This audit was executed in a minimal environment relying exclusively on standard Python library components.

## 1. Operating System
*   **OS:** Linux (Ubuntu 24.04 LTS / Debian-based)
*   **Kernel:** x86_64 Linux

## 2. Runtimes
*   **Python:** 3.12.3 (GCC 13.3.0)

## 3. Library Dependencies
*   **Standard Libraries Only:** No external pip packages (such as `pandas`, `numpy`, or `scipy`) are required to run the verification pipeline, ensuring zero dependency decay over time.
*   **Standard imports utilized:**
    *   `os` (system path utilities)
    *   `sys` (runtime environment hooks)
    *   `json` (data parsing)
    *   `hashlib` (SHA-256 integrity calculation)
    *   `argparse` (CLI parsing)
