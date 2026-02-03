"""LSP client for the Relay compiler's built-in language server."""
import os
import sublime
import subprocess
from lsp_utils import NpmClientHandler, ClientConfig
from LSP.plugin.core.typing import List, Optional


def plugin_loaded() -> None:
    LspRelayPlugin.setup()


def plugin_unloaded() -> None:
    LspRelayPlugin.cleanup()


class LspRelayPlugin(NpmClientHandler):
    """Sublime Text LSP client for Relay language server."""

    package_name = __package__
    server_directory = 'language-server'
    server_binary_path = os.path.join(server_directory, 'node_modules', 'relay-compiler', 'cli.js')

    @classmethod
    def get_binary_arguments(cls) -> List[str]:
        """Return arguments for the relay-compiler CLI."""
        settings = sublime.load_settings('LSP-relay.sublime-settings').get('settings', {})
        args = ['lsp']

        output_level = settings.get('lspOutputLevel') or 'quiet-with-errors'
        if output_level:
            args.append(f'--output={output_level}')

        return args

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List,
        configuration: ClientConfig
    ) -> Optional[str]:
        """Check if a valid Relay configuration exists before starting the server."""
        reason = super().can_start(window, initiating_view, workspace_folders, configuration)
        if reason:
            return reason
        try:
            workspace_path = workspace_folders[0].path
            config_path = cls._get_config_path(workspace_path, configuration)
            if config_path is not None:
                validate_cmd = cls.get_command() + [config_path]
            else:
                validate_cmd = cls.get_command()
            result = subprocess.run(
                validate_cmd,
                cwd=workspace_folders[0].path,
                capture_output=True,
                text=True,
                timeout=10
            )
            # if it is started in a subprocess, it terminates with a protocol error if the configuration is valid
            if result.returncode != 0 and 'Relay LSP unexpectedly terminated: ProtocolError' not in result.stderr:
                return "No Relay configuration found. Create relay.config.json or check LSP-Relay readme."
        except subprocess.TimeoutExpired as e:
            print(f'LSP-relay can_start: TimeoutExpired: {e}')
        except Exception as e:
            print(f'LSP-relay can_start: Exception: {e}')
        return None

    @classmethod
    def on_pre_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List,
        configuration: ClientConfig
    ) -> Optional[str]:
        """Handle workspace-dependent config path resolution."""
        workspace_path = workspace_folders[0].path if workspace_folders else ''
        command = configuration.command
        config_path = cls._get_config_path(workspace_path, configuration)
        if config_path is not None:
            command.append(config_path)
        return None

    @classmethod
    def _get_config_path(
        cls,
        workspace_path: str,
        configuration: ClientConfig
    ) -> Optional[str]:
        """Handle workspace-dependent config path resolution."""
        settings = configuration.settings
        path_to_config = settings.get('pathToConfig') or ''
        # Handle relative paths - resolve against workspace root
        if path_to_config and not os.path.isabs(path_to_config) and workspace_path:
            resolved_path = os.path.join(workspace_path, path_to_config)
            print(f'LSP-relay on_pre_start: added relative config path={resolved_path}')
            return resolved_path
        # Fallback to VS Code settings if enabled and no pathToConfig set
        elif not path_to_config and settings.get('useVSCodeRelaySettings') and workspace_path:
            vscode_path = cls._get_vscode_relay_path_to_config(workspace_path)
            if vscode_path:
                if not os.path.isabs(vscode_path):
                    vscode_path = os.path.join(workspace_path, vscode_path)
                print(f'LSP-relay on_pre_start: added VS Code config path={vscode_path}')
                return vscode_path
        return None

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
            print(f'LSP-relay: Failed to read VS Code settings: {e}')
        return None
