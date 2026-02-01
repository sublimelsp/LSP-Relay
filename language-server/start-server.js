/**
 * Wrapper script that spawns the Relay compiler's language server.
 * The relay-compiler package exports the path to its platform-specific binary.
 */
const { spawn } = require('child_process');

const relayBinary = require('relay-compiler');

if (!relayBinary) {
    process.stderr.write(`Platform "${process.platform} (${process.arch})" not supported.\n`);
    process.exit(1);
}

// Pass through any command line arguments (e.g., --output=quiet-with-errors, config path)
const args = ['lsp', ...process.argv.slice(2)];

const child = spawn(relayBinary, args, {
    stdio: 'inherit'
});

child.on('error', (err) => {
    process.stderr.write(`Failed to start Relay LSP: ${err.message}\n`);
    process.exit(1);
});

child.on('exit', (code, signal) => {
    if (signal) {
        process.exit(1);
    }
    process.exit(code || 0);
});
