#!/usr/bin/env node
/*
 * Generate a two-column PDF (work.pdf) of a work: the original language on the left, the translation on the
 * right, one row per lyric line. The PDF is rendered by headless Chrome/Edge from a generated HTML page.
 * See scripts/README.md.
 *
 * Usage: node scripts/make-work-pdf.js [workDir ...]
 *   With no arguments, every directory under assets/ that contains a work.js is processed.
 *   Set CHROME=/path/to/chrome (or msedge) if the browser is not found automatically.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { findWorkDirs, loadWork } = require('./lib/load-work');

const OUTPUT_NAME = 'work.pdf';

const BROWSER_CANDIDATES = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  '/usr/bin/microsoft-edge',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
];

function findBrowser() {
  const found = process.env.CHROME || BROWSER_CANDIDATES.find(p => fs.existsSync(p));
  if (!found) throw new Error('Chrome/Edge not found: set the CHROME environment variable to its executable');
  return found;
}

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const CSS = `
  @page { size: A4; margin: 16mm 14mm 18mm;
          @bottom-center { content: counter(page) " / " counter(pages); font: 9pt sans-serif; color: #777; } }
  * { box-sizing: border-box; }
  body { margin: 0; color: #111; font: 11pt/1.45 -apple-system, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB",
         "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif; }
  .row { display: grid; grid-template-columns: 1fr 1fr; column-gap: 10mm; break-inside: avoid; }
  .row > div { white-space: pre-line; overflow-wrap: anywhere; }
  .lyric { padding: 1.4mm 0; border-bottom: 0.2mm solid #e4e4e4; }
  .lyric > div:last-child { color: #1c4a86; }
  .work-title { font-size: 24pt; font-weight: 700; padding-bottom: 3mm; margin-bottom: 4mm; border-bottom: 0.6mm solid #111; }
  .movement { margin-top: 7mm; padding: 2.5mm 3mm; background: #eceff3; border-left: 1.2mm solid #1c4a86;
              break-after: avoid; }
  .movement .head { font-size: 13pt; font-weight: 700; }
  .movement .voicing { font-size: 10pt; color: #444; }
  .work-title + .movement { margin-top: 0; }
`;

function buildHtml(work) {
  const left = work.language || 'en', right = work.translationLanguage || 'zh';
  const row = (cls, a, b) => `<div class="row ${cls}"><div lang="${left}">${a}</div><div lang="${right}">${b}</div></div>`;
  const head = (num, title, voicing) =>
    `<div class="head">${esc(`${num} ${title}`.trim())}</div>` + (voicing ? `<div class="voicing">${esc(voicing)}</div>` : '');

  const body = [row('work-title', esc(work.title), esc(work.titleTranslation))];
  for (const m of work.movements) {
    body.push(row('movement', head(m.number, m.title, m.voicing), head(m.number, m.titleTranslation, m.voicingTranslation)));
    for (const l of m.lines) body.push(row('lyric', esc(l.text), esc(l.translation)));
  }
  return `<!doctype html>\n<html><head><meta charset="utf-8"><title>${esc(work.title)}</title>`
    + `<style>${CSS}</style></head><body>\n${body.join('\n')}\n</body></html>\n`;
}

function makePdf(workDir, browser) {
  const html = buildHtml(loadWork(workDir));
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'work-pdf-'));
  const htmlFile = path.join(tmp, 'work.html');
  const out = path.resolve(workDir, OUTPUT_NAME);
  try {
    fs.writeFileSync(htmlFile, html);
    execFileSync(browser, [
      '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
      `--user-data-dir=${path.join(tmp, 'profile')}`,   // a private profile: works while Chrome is open
      `--print-to-pdf=${out}`, `file://${htmlFile}`,
    ], { stdio: ['ignore', 'ignore', 'ignore'] });
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
  if (!fs.existsSync(out)) throw new Error(`browser did not produce ${out}`);
  return out;
}

const browser = findBrowser();
const dirs = process.argv.length > 2 ? process.argv.slice(2) : findWorkDirs();
for (const dir of dirs) {
  console.log(`wrote ${path.relative(process.cwd(), makePdf(dir, browser))}`);
}
