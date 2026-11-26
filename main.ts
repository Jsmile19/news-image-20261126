import { copyFile, mkdir, stat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

async function main() {
  const source = join(dirname(fileURLToPath(import.meta.url)), 'entry.png');

  // Validate the bundled poster before creating anything in the output folder.
  let sourceInfo;
  try {
    sourceInfo = await stat(source);
  } catch (error) {
    if (error && error.code === 'ENOENT') {
      throw new Error(`Poster not found: ${source}. Run python3 draw_poster.py first.`);
    }
    throw error;
  }
  if (!sourceInfo.isFile()) {
    throw new Error(`Poster is not a regular file: ${source}`);
  }

  const outputDirectory = resolve(process.env.MAKEFUN_OUTPUT_DIR || '/output');
  const destination = join(outputDirectory, 'entry.png');
  await mkdir(outputDirectory, { recursive: true });
  await copyFile(source, destination);
  const copied = await stat(destination);
  console.log(`${destination} (${copied.size} bytes)`);
}

main().catch((error) => {
  console.error(`news-image: ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
});
