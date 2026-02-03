# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LSP-relay is a Sublime Text plugin that provides an LSP client for the Relay Compiler's built-in language server. It enables IDE features (diagnostics, autocomplete, go-to-definition) for Relay projects in JavaScript/TypeScript files.

## Architecture

This is a Sublime Text package using the `lsp_utils` framework:

- **plugin.py** - Main plugin implementing `NpmClientHandler` from lsp_utils. Contains the `LspRelayPlugin` class that:
  - Validates Relay config exists before starting server (`can_start`)
  - Resolves config paths including VS Code settings interop (`_get_config_path`, `_get_vscode_relay_path_to_config`)
  - Configures CLI arguments (`get_binary_arguments`)

- **language-server/** - Contains `package.json` that declares `relay-compiler` as a dependency. The actual server binary comes from `node_modules/relay-compiler/cli.js`

- **LSP-relay.sublime-settings** - Default settings (pathToConfig, lspOutputLevel, useVSCodeRelaySettings)

- **sublime-package.json** - JSON schema definitions for settings validation in Sublime Text

## Key Implementation Details

The plugin starts `relay-compiler lsp` as the language server. Before starting, it validates that a valid Relay config exists by running the command in a subprocess and checking the exit code.

Config path resolution order:
1. `pathToConfig` setting (resolved relative to workspace if not absolute)
2. If `useVSCodeRelaySettings` is enabled, reads from `.vscode/settings.json`
3. Falls back to Relay compiler's default config discovery

## Testing Locally

Install the package in Sublime Text's Packages folder (symlink or copy), then open a project with Relay configuration.

## Code Style

**Python linting:**
```bash
flake8 plugin.py --max-line-length=120
pycodestyle plugin.py --max-line-length=120
```
