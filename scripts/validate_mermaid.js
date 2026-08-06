const fs = require("fs");
const path = require("path");

// The Hugo theme ships a browser-oriented UMD build. The parser itself only
// needs a window-like global, so this shim lets CI validate the exact version
// that renders the website without installing another Mermaid release.
global.window = global;

const repoRoot = path.resolve(__dirname, "..");
const contentRoot = path.join(repoRoot, "content");
const mermaid = require(path.join(
  repoRoot,
  "themes",
  "hugo-theme-learn",
  "static",
  "mermaid",
  "mermaid.js",
));

mermaid.initialize({ startOnLoad: false });

const blockPattern = /\{\{<\s*mermaid(?:\s+[^>]*)?\s*>\}\}([\s\S]*?)\{\{<\s*\/mermaid\s*>\}\}/g;
const openingPattern = /\{\{<\s*mermaid(?:\s+[^>]*)?\s*>\}\}/g;
const closingPattern = /\{\{<\s*\/mermaid\s*>\}\}/g;

function markdownFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      return markdownFiles(entryPath);
    }

    return entry.isFile() && entry.name.endsWith(".md") ? [entryPath] : [];
  });
}

let diagramCount = 0;
const failures = [];

for (const filePath of markdownFiles(contentRoot)) {
  const sourceText = fs.readFileSync(filePath, "utf8");
  const openings = sourceText.match(openingPattern) || [];
  const closings = sourceText.match(closingPattern) || [];

  if (openings.length !== closings.length) {
    failures.push(
      `${path.relative(repoRoot, filePath)}: unmatched Mermaid shortcode ` +
        `(open=${openings.length}, close=${closings.length})`,
    );
  }

  let match;
  let blockIndex = 0;
  blockPattern.lastIndex = 0;

  while ((match = blockPattern.exec(sourceText)) !== null) {
    blockIndex += 1;
    diagramCount += 1;
    const diagramSource = match[1].trim();

    try {
      mermaid.parse(diagramSource);
    } catch (error) {
      const message = error && error.message ? error.message : String(error);
      failures.push(
        `${path.relative(repoRoot, filePath)} [diagram ${blockIndex}]: ${message}`,
      );
    }
  }
}

if (failures.length > 0) {
  console.error(`Mermaid validation failed: ${failures.length} error(s)`);
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`Mermaid validation passed: ${diagramCount} diagram(s)`);
