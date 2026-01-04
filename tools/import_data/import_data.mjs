#!/usr/bin/env node

import crypto from "node:crypto";
import { execFile } from "node:child_process";
import fs from "node:fs";
import { createReadStream, promises as fsPromises } from "node:fs";
import http from "node:http";
import https from "node:https";
import os from "node:os";
import path from "node:path";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";

const ARCHIVE_TYPES = ["zip", "tar", "tar.gz", "tgz", "tar.bz2", "tar.xz"];
const NO_LICENSE_LABEL = "No license / unknown (omit license_kind_label)";
const START_MARKER = "# OMA_DATA_START";
const END_MARKER = "# OMA_DATA_END";
const MAX_LICENSE_RESULTS = 20;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function formatList(items) {
  return items.map((item, index) => `  ${index + 1}) ${item}` ).join("\n");
}

async function promptText(question, { defaultValue = "", required = false } = {}) {
  const suffix = defaultValue ? ` [${defaultValue}]` : "";
  const answer = (await rl.question(`${question}${suffix}: `)).trim();
  if (!answer) {
    if (required && !defaultValue) {
      return promptText(question, { defaultValue, required });
    }
    return defaultValue;
  }
  return answer;
}

async function promptYesNo(question, defaultValue = false) {
  const prompt = defaultValue ? "Y/n" : "y/N";
  const answer = (await rl.question(`${question} (${prompt}): `)).trim().toLowerCase();
  if (!answer) {
    return defaultValue;
  }
  return ["y", "yes"].includes(answer);
}

async function promptChoice(question, choices) {
  console.log(question);
  console.log(formatList(choices.map((choice) => choice.label ?? choice)));
  const answer = await promptText("Select an option", { required: true });
  const index = Number.parseInt(answer, 10);
  if (!Number.isNaN(index) && index >= 1 && index <= choices.length) {
    return choices[index - 1];
  }
  return promptChoice(question, choices);
}

function filterLicenseChoices(choices, query) {
  const normalized = query.toLowerCase();
  return choices.filter((choice) => choice.label.toLowerCase().includes(normalized));
}

async function promptLicenseChoice(choices) {
  const otherChoice = choices.find((choice) => choice.value === "custom");
  const noLicenseChoice = choices.find((choice) => choice.label === NO_LICENSE_LABEL);
  const standardChoices = choices.filter(
    (choice) => choice !== otherChoice && choice !== noLicenseChoice,
  );

  let query = "";
  while (true) {
    const filtered = query
      ? filterLicenseChoices(standardChoices, query)
      : standardChoices;
    const truncated = filtered.slice(0, MAX_LICENSE_RESULTS);
    const promptChoices = [];

    if (noLicenseChoice) {
      promptChoices.push(noLicenseChoice);
    }
    promptChoices.push(...truncated);
    if (filtered.length > MAX_LICENSE_RESULTS) {
      promptChoices.push({ label: "Refine search", value: "__refine__" });
    }
    if (otherChoice) {
      promptChoices.push(otherChoice);
    }

    console.log("\nLicense search:");
    if (query) {
      console.log(`  Filter: "${query}" (${filtered.length} matches)`);
    } else {
      console.log(`  Showing ${truncated.length} of ${filtered.length} licenses`);
    }
    const selection = await promptChoice("Select the license", promptChoices);
    if (selection.value === "__refine__") {
      query = await promptText("Enter a new filter (leave empty to reset)");
      continue;
    }
    return selection;
  }
}

async function promptArchiveType(defaultValue) {
  const answer = await promptText(
    `Archive type (${ARCHIVE_TYPES.join(", ")})`,
    { defaultValue, required: true },
  );
  if (!ARCHIVE_TYPES.includes(answer)) {
    console.log(`Unknown archive type. Expected one of: ${ARCHIVE_TYPES.join(", ")}`);
    return promptArchiveType(defaultValue);
  }
  return answer;
}

function sha256FromStream(stream) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash("sha256");
    stream.on("data", (chunk) => hash.update(chunk));
    stream.on("error", reject);
    stream.on("end", () => resolve(hash.digest("hex")));
  });
}

async function sha256FromFile(filePath) {
  const stream = createReadStream(filePath);
  return sha256FromStream(stream);
}

function downloadToFile(url, filePath) {
  const client = url.startsWith("https:") ? https : http;
  return new Promise((resolve, reject) => {
    const request = client.get(url, (response) => {
      if (response.statusCode && response.statusCode >= 400) {
        reject(new Error(`Download failed with status ${response.statusCode}`));
        response.resume();
        return;
      }
      const fileStream = fs.createWriteStream(filePath);
      response.pipe(fileStream);
      fileStream.on("finish", () => fileStream.close(resolve));
      fileStream.on("error", reject);
    });
    request.on("error", reject);
  });
}

function guessArchiveType(nameOrUrl) {
  const lowered = nameOrUrl.toLowerCase();
  const match = ARCHIVE_TYPES.find((type) => lowered.endsWith(`.${type}`));
  if (match) {
    return match;
  }
  if (lowered.endsWith(".tgz")) {
    return "tgz";
  }
  return "";
}

function buildPurl({ namespace, name, version, downloadUrl }) {
  const encodedUrl = encodeURIComponent(downloadUrl);
  if (version) {
    return `pkg:generic/${namespace}/${name}@${version}?download_url=${encodedUrl}`;
  }
  return `pkg:generic/${namespace}/${name}?download_url=${encodedUrl}`;
}

function normalizeUrls(input) {
  return input
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function repoRoot() {
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(scriptDir, "../..");
}

function parseArgs(argv) {
  const args = new Set(argv);
  return {
    dryRun: args.has("--dry-run"),
  };
}

function execBazelQuery(args, cwd) {
  return new Promise((resolve, reject) => {
    execFile("bazel", args, { cwd }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || error.message));
        return;
      }
      resolve(stdout);
    });
  });
}

async function loadLicenseChoices() {
  const cwd = repoRoot();
  const output = await execBazelQuery(
    ["query", "--output=label", "@package_metadata//licenses/spdx:*"],
    cwd,
  );
  const labels = output
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b));

  const choices = labels.map((label) => {
    const id = label.split(":").pop() || label;
    return { label: id, value: label };
  });

  return [
    { label: NO_LICENSE_LABEL, value: "" },
    ...choices,
    { label: "Other (enter custom label)", value: "custom" },
  ];
}

function buildStanza({
  kind,
  archiveType,
  extract,
  stripPrefix,
  name,
  licenseKindLabel,
  purl,
  sha256,
  urls,
}) {
  const lines = [];
  lines.push(kind === "file" ? "oma.file(" : "oma.archive(");
  if (kind === "archive") {
    lines.push(`    archive_type = \"${archiveType}\",`);
    lines.push(`    extract = ${extract ? "True" : "False"},`);
    if (stripPrefix) {
      lines.push(`    strip_prefix = \"${stripPrefix}\",`);
    }
  }
  lines.push(`    name = \"${name}\",`);
  if (licenseKindLabel) {
    lines.push(`    license_kind_label = \"${licenseKindLabel}\",`);
  }
  lines.push(`    purl = \"${purl}\",`);
  lines.push(`    sha256 = \"${sha256}\",`);
  lines.push("    urls = [");
  for (const url of urls) {
    lines.push(`        \"${url}\",`);
  }
  lines.push("    ],");
  lines.push(")");
  return lines.join("\n");
}

async function appendToModuleBazel(stanza) {
  const modulePath = path.join(repoRoot(), "MODULE.bazel");
  const content = await fsPromises.readFile(modulePath, "utf8");
  let updated = content;
  const startIndex = content.indexOf(START_MARKER);
  const endIndex = content.indexOf(END_MARKER);
  if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
    const insertionPoint = endIndex;
    updated =
      content.slice(0, insertionPoint).trimEnd() +
      `\n\n${stanza}\n` +
      content.slice(insertionPoint);
  } else {
    updated = `${content.trimEnd()}\n\n# OMA data artifacts (managed by tools/import_data)\n${START_MARKER}\n${stanza}\n${END_MARKER}\n`;
  }
  await fsPromises.writeFile(modulePath, updated, "utf8");
  return modulePath;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  console.log("OMA Import Data TUI");
  console.log("This tool will generate an oma.file or oma.archive stanza.\n");

  const artifactKind = await promptChoice("What would you like to import?", [
    { label: "File", value: "file" },
    { label: "Archive", value: "archive" },
  ]);

  const sourceKind = await promptChoice("Select the source for the artifact", [
    { label: "Remote URL", value: "url" },
    { label: "Local file path", value: "local" },
  ]);

  let sourcePath = "";
  if (sourceKind.value === "url") {
    sourcePath = await promptText("Enter the URL to download", { required: true });
  } else {
    sourcePath = await promptText("Enter the local file path", { required: true });
  }

  const artifactName = await promptText("Artifact name (oma rule name)", { required: true });
  const packageNamespace = await promptText("Package namespace", { defaultValue: "oma" });
  const packageVersion = await promptText("Package version (optional)", { defaultValue: "" });

  const defaultUrls = sourceKind.value === "url" ? sourcePath : `file://${path.resolve(sourcePath)}`;
  const urlsInput = await promptText("URLs (comma-separated)", { defaultValue: defaultUrls, required: true });
  const urls = normalizeUrls(urlsInput);

  const downloadUrl = urls[0];
  const purl = buildPurl({
    namespace: packageNamespace,
    name: artifactName,
    version: packageVersion,
    downloadUrl,
  });

  let sha256 = "";
  if (sourceKind.value === "url") {
    const tempDir = await fsPromises.mkdtemp(path.join(os.tmpdir(), "oma-import-"));
    const fileName = path.basename(new URL(sourcePath).pathname) || "artifact";
    const tempFile = path.join(tempDir, fileName);
    console.log(`Downloading ${sourcePath}...`);
    await downloadToFile(sourcePath, tempFile);
    sha256 = await sha256FromFile(tempFile);
  } else {
    sha256 = await sha256FromFile(sourcePath);
  }

  const licenseChoices = await loadLicenseChoices();
  const licenseChoice = await promptLicenseChoice(licenseChoices);
  let licenseKindLabel = licenseChoice.value;
  if (licenseKindLabel === "custom") {
    licenseKindLabel = await promptText("Enter the full license_kind_label", { required: true });
  }

  let archiveType = "";
  let extract = false;
  let stripPrefix = "";
  if (artifactKind.value === "archive") {
    archiveType = await promptArchiveType(guessArchiveType(sourcePath) || "tar.gz");
    extract = await promptYesNo("Extract archive?", true);
    if (extract) {
      stripPrefix = await promptText("Strip prefix (optional)");
    }
  }

  const stanza = buildStanza({
    kind: artifactKind.value,
    archiveType,
    extract,
    stripPrefix,
    name: artifactName,
    licenseKindLabel,
    purl,
    sha256,
    urls,
  });

  console.log("\nGenerated stanza:\n");
  console.log(stanza);

  if (options.dryRun) {
    console.log("\nDry run enabled; MODULE.bazel was not modified.");
  } else {
    const modulePath = await appendToModuleBazel(stanza);
    console.log(`\nAppended to ${modulePath}.`);
  }
}

try {
  await main();
} finally {
  rl.close();
}
