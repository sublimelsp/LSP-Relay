"""LSP client for the Relay compiler's built-in language server."""
import os
import sublime
from lsp_utils import NpmClientHandler
from LSP.plugin.core.typing import Any, List, Optional


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
    def _get_setting(cls, key: str, default: Any = None) -> Any:
        """Get a setting value, checking project-specific settings first."""
        window = sublime.active_window()
        if window:
            project_data = window.project_data() or {}
            project_settings = project_data.get('settings', {})
            lsp_settings = project_settings.get('LSP', {})
            relay_settings = lsp_settings.get('LSP-relay', {})
            if key in relay_settings:
                return relay_settings[key]
        settings = sublime.load_settings('LSP-relay.sublime-settings')
        return settings.get(key, default)

    @classmethod
    def _get_vscode_relay_path_to_config(cls) -> Optional[str]:
        """Load pathToConfig from .vscode/settings.json if it exists.

        Only checks the first project folder for VS Code settings, as this mirrors
        how VS Code handles single-root workspaces.
        """
        window = sublime.active_window()
        if not window:
            return None
        folders = window.folders()
        if not folders:
            return None
        vscode_settings_path = os.path.join(folders[0], '.vscode', 'settings.json')
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
    def get_binary_arguments(cls) -> List[str]:
        """Build command-line arguments for the Relay language server."""
        args = []
        output_level = cls._get_setting('lspOutputLevel', 'quiet-with-errors')
        if output_level:
            args.append('--output={}'.format(output_level))
        path_to_config = cls._get_setting('pathToConfig', '')
        if not path_to_config and cls._get_setting('useVSCodeRelaySettings', False):
            path_to_config = cls._get_vscode_relay_path_to_config() or ''
        if path_to_config:
            args.append(path_to_config)
        return args
