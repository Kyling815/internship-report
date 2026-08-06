const fs = require("fs");
const os = require("os");
const path = require("path");
const { pathToFileURL } = require("url");
const { spawnSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");
const contentRoot = path.join(repoRoot, "content");
const outputRoot = path.join(repoRoot, "report", "generated", "mermaid");
const mermaidScript = path.join(
  repoRoot,
  "themes",
  "hugo-theme-learn",
  "static",
  "mermaid",
  "mermaid.js",
);
const chromeCandidates = [
  process.env.CHROME_PATH,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
].filter(Boolean);
const chromePath = chromeCandidates.find((candidate) => fs.existsSync(candidate));

if (!chromePath) {
  throw new Error("Chrome or Edge was not found; cannot render Mermaid diagrams.");
}

const blockPattern = /\{\{<\s*mermaid(?:\s+[^>]*)?\s*>\}\}([\s\S]*?)\{\{<\s*\/mermaid\s*>\}\}/g;

function markdownFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name);
    if (entry.isDirectory()) return markdownFiles(entryPath);
    return entry.isFile() && /^_index(?:\.vi)?\.md$/.test(entry.name)
      ? [entryPath]
      : [];
  });
}

function assetStem(relativeDirectory, index) {
  const safeDirectory = relativeDirectory
    .replace(/\\/g, "/")
    .replace(/[^A-Za-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return `${safeDirectory}_${String(index).padStart(2, "0")}`;
}

function mermaidDocument(source) {
  const mermaidUrl = pathToFileURL(mermaidScript).href;
  // Mermaid labels may intentionally contain placeholders such as
  // <github.sha>. Escape those as text while preserving supported <br/> tags.
  const htmlSource = source.replace(
    /<(?!br\s*\/?>)([^<>]+)>/gi,
    (_match, label) => `&lt;${label}&gt;`,
  );

  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; background: white; }
  .mermaid { display: inline-block; }
  .mermaid > svg { max-width: none !important;
    font-family: Arial, Helvetica, sans-serif !important; }
</style>
</head>
<body>
<div class="mermaid">${htmlSource}</div>
<script src="${mermaidUrl}"></script>
<script>
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: "neutral",
    flowchart: { useMaxWidth: false },
    sequence: { useMaxWidth: false }
  });
  mermaid.init(undefined, document.querySelectorAll(".mermaid"));
</script>
</body>
</html>`;
}

function printableSvgDocument(svg, width, height) {
  const padding = 24;
  const pageWidth = Math.ceil(width + padding * 2);
  const pageHeight = Math.ceil(height + padding * 2);

  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page { size: ${pageWidth}px ${pageHeight}px; margin: 0; }
  html, body { width: ${pageWidth}px; height: ${pageHeight}px; margin: 0; overflow: hidden; }
  body { box-sizing: border-box; padding: ${padding}px; background: white; }
  body > svg { display: block; width: ${width}px !important; height: ${height}px !important;
    max-width: none !important; font-family: Arial, Helvetica, sans-serif !important; }
</style>
</head>
<body>${svg}</body>
</html>`;
}

function renderDiagram(source, outputPath) {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "report-mermaid-"));
  const sourceHtmlPath = path.join(tempRoot, "source.html");
  const printHtmlPath = path.join(tempRoot, "print.html");
  const dumpProfilePath = path.join(tempRoot, "chrome-dump-profile");
  const printProfilePath = path.join(tempRoot, "chrome-print-profile");

  try {
    fs.writeFileSync(sourceHtmlPath, mermaidDocument(source.trim()), "utf8");
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });

    const dumpResult = spawnSync(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--allow-file-access-from-files",
      "--dump-dom",
      "--window-size=2400,1800",
      "--user-data-dir=" + dumpProfilePath,
      "--virtual-time-budget=5000",
      pathToFileURL(sourceHtmlPath).href,
    ], { encoding: "utf8", timeout: 30000 });

    if (dumpResult.error || dumpResult.status !== 0) {
      const details = [dumpResult.error && dumpResult.error.message, dumpResult.stderr]
        .filter(Boolean)
        .join("\n");
      throw new Error(`Chrome failed to render Mermaid DOM for ${outputPath}: ${details}`);
    }

    const dom = dumpResult.stdout || "";
    const svgStart = dom.indexOf("<svg");
    const svgEnd = dom.lastIndexOf("</svg>");
    if (svgStart < 0 || svgEnd < svgStart) {
      throw new Error(`Rendered Mermaid SVG was not found for ${outputPath}`);
    }

    const svg = dom.slice(svgStart, svgEnd + "</svg>".length);
    const viewBoxMatch = svg.match(/viewBox="[^\"]*?([0-9.]+)\s+([0-9.]+)"/i);
    if (!viewBoxMatch) {
      throw new Error(
        `Rendered Mermaid viewBox was not found for ${outputPath}: ` +
        svg.slice(0, 500),
      );
    }

    const width = Number(viewBoxMatch[1]);
    const height = Number(viewBoxMatch[2]);
    if (!(width > 0 && height > 0)) {
      throw new Error(`Invalid Mermaid viewBox for ${outputPath}: ${width} x ${height}`);
    }

    fs.writeFileSync(printHtmlPath, printableSvgDocument(svg, width, height), "utf8");
    const printResult = spawnSync(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--allow-file-access-from-files",
      "--no-pdf-header-footer",
      "--print-to-pdf-no-header",
      "--print-to-pdf=" + outputPath,
      "--user-data-dir=" + printProfilePath,
      "--virtual-time-budget=3000",
      pathToFileURL(printHtmlPath).href,
    ], { encoding: "utf8", timeout: 30000 });

    if (printResult.error || printResult.status !== 0 || !fs.existsSync(outputPath)) {
      const details = [printResult.error && printResult.error.message, printResult.stderr]
        .filter(Boolean)
        .join("\n");
      throw new Error(`Chrome failed to print ${outputPath}: ${details}`);
    }
  } finally {
    fs.rmSync(tempRoot, { recursive: true, force: true });
  }
}

let diagramCount = 0;

for (const markdownPath of markdownFiles(contentRoot)) {
  const filename = path.basename(markdownPath);
  const lang = filename.includes(".vi.") ? "vi" : "en";
  const relativeDirectory = path.relative(contentRoot, path.dirname(markdownPath));
  const sourceText = fs.readFileSync(markdownPath, "utf8");
  let match;
  let blockIndex = 0;

  blockPattern.lastIndex = 0;
  while ((match = blockPattern.exec(sourceText)) !== null) {
    blockIndex += 1;
    diagramCount += 1;
    const outputPath = path.join(
      outputRoot,
      lang,
      assetStem(relativeDirectory, blockIndex) + ".pdf",
    );
    renderDiagram(match[1], outputPath);
    console.log(`Rendered ${path.relative(repoRoot, outputPath)}`);
  }
}

console.log(`Mermaid rendering complete: ${diagramCount} diagram(s)`);
