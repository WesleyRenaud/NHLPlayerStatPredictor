import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '../..');
const EXCLUDES = JSON.parse(
   readFileSync(join(ROOT, 'tools/coverage/jsCoverageExcludes.json'), 'utf8')
).exclude ?? [];

const args = [
   '--test',
   '--experimental-test-coverage',
   '--test-coverage-include=scripts/**/*.js',
   ...EXCLUDES.flatMap((pattern) => [`--test-coverage-exclude=${pattern}`]),
   'tests/scripts/**/*.test.mjs',
];

const child = spawn(process.execPath, args, {
   cwd: ROOT,
   stdio: 'inherit',
});

child.on('exit', (code, signal) => {
   if (signal) {
      process.kill(process.pid, signal);
      return;
   }

   process.exit(code ?? 1);
});
