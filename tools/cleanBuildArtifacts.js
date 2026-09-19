import fs from 'node:fs';
import path from 'node:path';

const ROOT_DIRECTORY = process.cwd();

const GENERATED_DIRECTORY_NAMES = new Set([
   '__pycache__',
   '.pytest_cache',
   '.ruff_cache',
]);

function removeDirectory(directoryPath) {
   fs.rmSync(directoryPath, {
      force: true,
      recursive: true,
   });
   console.log(`Removed ${path.relative(ROOT_DIRECTORY, directoryPath)}`);
}

function cleanGeneratedDirectories(directoryPath) {
   const entries = fs.readdirSync(directoryPath, {
      withFileTypes: true,
   });

   entries.forEach((entry) => {
      if (!entry.isDirectory()) {
         return;
      }

      const entryPath = path.join(directoryPath, entry.name);

      if (GENERATED_DIRECTORY_NAMES.has(entry.name)) {
         removeDirectory(entryPath);
         return;
      }

      cleanGeneratedDirectories(entryPath);
   });
}

cleanGeneratedDirectories(ROOT_DIRECTORY);
