# LSP-relay

[Relay](https://relay.dev/) language server support for Sublime Text's LSP plugin.

Provides an LSP client for the [Relay Compiler](https://relay.dev/docs/guides/compiler/)'s built-in language server, enabling diagnostics, autocomplete, go-to-definition, and other IDE features for Relay projects in JavaScript and TypeScript files.

## Installation

* Install [LSP](https://packagecontrol.io/packages/LSP) and `LSP-relay` from Package Control.
* Restart Sublime.

## Project configuration

The Relay language server requires a `relay.config.json` (or `relay.config.js`) in your project root with at minimum:

```json
{
  "src": "./src",
  "schema": "./schema.graphql",
  "language": "typescript"
}
```

Refer to the [Relay Compiler Configuration](https://relay.dev/docs/guides/compiler/) documentation for more details.

## Configuration

### Global settings

Open the global settings file using the command palette with `Preferences: LSP-relay Settings` or from the Sublime menu (`Preferences > Package Settings > LSP > Servers > LSP-relay`).

Available settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `pathToConfig` | Path to a relay config file, absolute or relative to project root (`relay.config.json`, `.js`, `.cjs`, or `.mjs`). If not specified, the compiler searches for config in `package.json` or `relay.config.*` files. | `""` |
| `lspOutputLevel` | LSP output verbosity level. Options: `debug`, `quiet`, `quiet-with-errors`, `verbose` | `"quiet-with-errors"` |
| `useVSCodeRelaySettings` | When enabled, loads `pathToConfig` from `.vscode/settings.json` if not set above. | `false` |

### Project-specific settings

You can override settings per-project in your `.sublime-project` file:

```json
{
  "folders": [
    { "path": "." }
  ],
  "settings": {
    "LSP": {
      "LSP-relay": {
        "pathToConfig": "/path/to/your/relay.config.js",
        "lspOutputLevel": "debug"
      }
    }
  }
}
```

Project settings take precedence over global settings.

### VS Code settings interoperability

For teams where some developers use VS Code with the [Relay extension](https://marketplace.visualstudio.com/items?itemName=meta.relay), you can enable `useVSCodeRelaySettings` to automatically read the relay config path from `.vscode/settings.json`:

```json
{
  "useVSCodeRelaySettings": true
}
```

When enabled, LSP-relay will look for `relay.pathToConfig` in your project's `.vscode/settings.json`:

```json
{
  "relay.pathToConfig": "./relay.config.js"
}
```

This allows sharing relay configuration across both editors without duplicating settings.
