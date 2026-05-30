---
name: notebooklm-py
description: Research automation and interactive source compilation using NotebookLM-Py CLI.
---

# 📚 /notebooklm-py

A Python-based CLI wrapper for Google NotebookLM, allowing programmatic research automation, notebook management, and document generation via CLI.

> [!IMPORTANT]
> To run commands, you must first authenticate by running `notebooklm login` in your local terminal.

---

## 🚀 Quick Start & Session Flow

* **Authenticate**:
  ```bash
  notebooklm login
  ```
* **List and Set Active Notebook**:
  ```bash
  notebooklm list
  notebooklm use <notebook-id-or-prefix>
  ```
* **Get Current Status**:
  ```bash
  notebooklm status
  ```

---

## 📥 Research & Source Management

Configure notebooks and add research sources directly from files or drives:

* **Add File Source**:
  ```bash
  notebooklm source add <path-to-document>
  ```
* **List Sources in Notebook**:
  ```bash
  notebooklm source list
  ```
* **Get Full Source Text**:
  ```bash
  notebooklm source get <source-id>
  ```

---

## 💬 Chat & AI Summaries

* **Ask Active Notebook a Question**:
  ```bash
  notebooklm ask "What are the core findings in our research folder?"
  ```
* **Get AI-Generated Insights / Summary**:
  ```bash
  notebooklm summary
  ```

---

## 🎨 Generation of Artifacts

Generate rich study guides, briefing documents, flashcards, mind maps, or slide decks:

* **Generate Slide Deck**:
  ```bash
  notebooklm generate slide-deck
  ```
* **Download Generated Artifact**:
  ```bash
  notebooklm download slide-deck
  ```
