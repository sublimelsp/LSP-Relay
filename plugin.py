"""LSP client for the Relay compiler's built-in language server."""
import os
import sublime
from lsp_utils import NpmClientHandler
from LSP.plugin.core.typing import List, Optional


def plugin_loaded() -> None:
    LspRelayPlugin.setup()


def plugin_unloaded() -> None:
    LspRelayPlugin.cleanup()


class LspRelayPlugin(NpmClientHandler):
    """Sublime Text LSP client for Relay language server."""

    package_name = __package__
    server_directory = 'language-server'
    server_binary_path = os.path.join(server_directory, 'start-server.js')

    @classmethod
    def _get_vscode_relay_path_to_config(cls, workspace_path: str) -> Optional[str]:
        """Load pathToConfig from .vscode/settings.json if it exists."""
        vscode_settings_path = os.path.join(workspace_path, '.vscode', 'settings.json')
        if not os.path.isfile(vscode_settings_path):
            return None
        try:
            with open(vscode_settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # sublime.decode_value handles JSON with comments (JSONC)
            settings = sublime.decode_value(content)
            if not isinstance(settings, dict):
                return None
            if 'relay.pathToConfig' in settings:
                return settings['relay.pathToConfig']
            relay_settings = settings.get('relay')
            if isinstance(relay_settings, dict):
                return relay_settings.get('pathToConfig')
        except Exception as e:
            print('LSP-relay: Failed to read VS Code settings: {}'.format(e))
        return None

    @classmethod
    def on_pre_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List,
        configuration: 'ClientConfig'  # type: ignore
    ) -> Optional[str]:
        """Configure command arguments before the language server starts."""
        settings = configuration.settings
        workspace_path = workspace_folders[0].path if workspace_folders else ''

        output_level = settings.get('lspOutputLevel') or 'quiet-with-errors'
        if output_level:
            configuration.command.append('--output={}'.format(output_level))

        path_to_config = settings.get('pathToConfig') or ''
        if not path_to_config and settings.get('useVSCodeRelaySettings') and workspace_path:
            path_to_config = cls._get_vscode_relay_path_to_config(workspace_path) or ''

        if path_to_config:
            # Resolve relative paths against workspace root
            if workspace_path and not os.path.isabs(path_to_config):
                path_to_config = os.path.join(workspace_path, path_to_config)
            configuration.command.append(path_to_config)

        return None
