// news-image-20261121 entry: copy the pre-rendered front page to the output dir.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const src = fileURLToPath(new URL("./entry.png", import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const MAX_BYTES = 1_048_576;
const MAX_SIDE = 1024;
const PNG_SIG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(msg: string): never {
  console.error(`entry check failed: ${msg}`);
  process.exit(1);
}

let bytes: Buffer;
try {
  bytes = readFileSync(src);
} catch (e) {
  fail(`cannot read ${src}: ${(e as Error).message}`);
}
if (bytes.length > MAX_BYTES) fail(`file is ${bytes.length} bytes, limit ${MAX_BYTES}`);
if (bytes.length < 33) fail("file too small to be a PNG");
for (let i = 0; i < PNG_SIG.length; i++) {
  if (bytes[i] !== PNG_SIG[i]) fail("missing PNG signature");
}
if (bytes.toString("latin1", 12, 16) !== "IHDR") fail("first chunk is not IHDR");
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width < 1 || height < 1 || width > MAX_SIDE || height > MAX_SIDE) {
  fail(`image is ${width}x${height}, limit ${MAX_SIDE}x${MAX_SIDE}`);
}
if (bytes.toString("latin1", bytes.length - 8, bytes.length - 4) !== "IEND") fail("PNG is truncated (no IEND)");

mkdirSync(outDir, { recursive: true });
writeFileSync(path.join(outDir, "entry.png"), bytes);
console.log(`wrote ${bytes.length} bytes (${width}x${height} PNG) to ${path.join(outDir, "entry.png")}`);
