#!/usr/bin/env node

"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const shareUrl =
  "https://unilj-my.sharepoint.com/:u:/g/personal/leon_todorov_fe1_uni-lj_si/" +
  "EXPI80C7nVJGm8L130BWR2IBhcaUoDusyDMBYtXdJxgnHQ?e=D4OiAr";
const expectedSha256 =
  "642433f4fcd5d88c072c94f9e9fe6765f46875f2fede69a046924ea6c8cb80d4";
const outputDirectory = process.env.CHECKPOINT_OUTPUT_DIR || "/downloads";
const destination = path.join(outputDirectory, "SelfMADpp_SMDD.tar");
const partial = `${destination}.part`;

async function sha256(filePath) {
  const digest = crypto.createHash("sha256");
  for await (const chunk of fs.createReadStream(filePath)) digest.update(chunk);
  return digest.digest("hex");
}

async function captureDownload(page, action) {
  const pending = page.waitForEvent("download", { timeout: 120_000 });
  try {
    await action();
  } catch (error) {
    const message = String(error);
    if (!message.includes("Download is starting") && !message.includes("ERR_ABORTED")) {
      pending.catch(() => {});
      throw error;
    }
  }
  return pending;
}

async function saveDownload(download) {
  console.log(`Downloading ${download.suggestedFilename()} from ${download.url()}`);
  await download.saveAs(partial);
  const failure = await download.failure();
  if (failure) throw new Error(`Browser download failed: ${failure}`);
}

async function main() {
  fs.mkdirSync(outputDirectory, { recursive: true });
  if (fs.existsSync(destination) && (await sha256(destination)) === expectedSha256) {
    console.log(`Checkpoint already verified: ${destination}`);
    return;
  }
  fs.rmSync(partial, { force: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();
  let download;

  try {
    await page.goto(shareUrl, { waitUntil: "domcontentloaded", timeout: 120_000 });
    await page.waitForTimeout(5_000);

    const candidates = [
      page.getByRole("button", { name: /download/i }).first(),
      page.getByRole("link", { name: /download/i }).first(),
      page.locator('[data-automationid="download"]').first(),
    ];
    for (const candidate of candidates) {
      if (!(await candidate.isVisible().catch(() => false))) continue;
      try {
        download = await captureDownload(page, () => candidate.click());
        await saveDownload(download);
        break;
      } catch (error) {
        console.error(`SharePoint Download control failed: ${error}`);
        download = undefined;
        fs.rmSync(partial, { force: true });
      }
    }

    if (!download) {
      download = await captureDownload(page, () =>
        page.goto(`${shareUrl}&download=1`, {
          waitUntil: "domcontentloaded",
          timeout: 120_000,
        }),
      );
      await saveDownload(download);
    }
  } finally {
    await browser.close();
  }

  const actual = await sha256(partial);
  if (actual !== expectedSha256) {
    fs.rmSync(partial, { force: true });
    throw new Error(`Checkpoint checksum mismatch: expected ${expectedSha256}, got ${actual}`);
  }
  fs.renameSync(partial, destination);
  console.log(`Downloaded and verified checkpoint: ${destination}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
