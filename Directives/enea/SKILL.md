# Agent Skill Manual: `notebook-press` CLI

This document defines the agent "muscle memory" and operational workflow for utilizing the `notebook-press` custom agent-native CLI tool. It completely replaces standard, fragile browser or plain `nlm` tool calls for paper ingestion, artifact polling, and media retrieval.

---

## 🚀 Core Strategy & Muscle Memory

The `notebook-press` tool provides robust, virtual-environment-compliant, and token-efficient interfaces to NotebookLM.

### 📍 Script Location & Execution
- **Wrapper Executable**: `/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press` (fully executable, wraps `.venv/bin/python3` automatically)
- **Primary Script**: `/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook_press.py`

Always call `/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press <command> [args]` to execute.

---

## 🛠️ CLI Interface Commands

### 1. `auth`
Verifies active authentication profiles and session validity.
```bash
/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press auth
```
*   **Returns**: High-speed, token-efficient JSON mapping active profile state.

### 2. `upload`
Moves a local paper PDF into the dedicated Google Drive sync folder, renames it to the exact chosen title (forcing the watermark overlay), polls macOS extended attributes until Drive assigns a File ID, and registers the file in the notebook.
```bash
/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press upload <pdf_path> --title "<title>" [--notebook-id <nb_id>]
```
*   **Behavior**: If `--notebook-id` is omitted, it automatically creates a new notebook with the specified title and returns its UUID.

### 3. `generate`
Triggers generation for the chosen studio artifact with predefined custom templates and Italian language constraints.
```bash
/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press generate <notebook_id> --type <video|infographic> --focus "<prompt>"
```

### 4. `status`
Returns ultra-compact JSON detailing current generation states for both video and infographic.
```bash
/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press status <notebook_id>
```
*   **Example Output**:
    ```json
    {
      "status": "success",
      "notebook_id": "8b51d137-...",
      "video": { "id": "...", "status": "completed", "updated_at": "..." },
      "infographic": { "id": "...", "status": "completed", "updated_at": "..." }
    }
    ```

### 5. `download`
Retrieves generated media using standard CLI. If it encounters a missing file, HTML login redirect, or corruption, it automatically switches to a direct HTTP session stream using authenticated cookies.
```bash
/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press download <notebook_id> <video|infographic> --output <path>
```

### 6. `sync`
The unified master command that executes the entire paper-to-assets pipeline sequentially (Upload → Create → Ingest → Generate Video & Info → Poll Status → Download Assets).
```bash
/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press sync <pdf_path> --title "<title>" [--video-prompt "<v_prompt>"] [--info-prompt "<i_prompt>"] [--output-dir "<dir>"] [--clean-title "<clean_title>"]
```

---

## ⚠️ Operational Directives & Fail-safes
1.  **Watermark Integrity**: The title specified in the `--title` argument is applied directly as the filename in Google Drive. This enforces correct branding in all overlay frames.
2.  **HTML Redirect Bypass**: If a download returns `<text/html>` (login redirect / service issue), the `download` command automatically isolates the error, deletes the hijacked payload, and streams directly from Google storage nodes using the cached cookies.
