#!/usr/bin/env node
/*
 * Generate a plain-text version (work.txt) of a work from its work.js and the
 * *.timing.js files of its movements. See scripts/README.md.
 *
 * Usage: node scripts/make-work-txt.js [workDir ...]
 *   With no arguments, every directory under assets/ that contains a work.js is processed.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { findWorkDirs, loadWork } = require('./lib/load-work');

const OUTPUT_NAME = 'work.txt';

function buildText(workDir) {
  const work = loadWork(workDir);
  const blocks = [[work.title, work.titleTranslation].filter(Boolean).join('\n')];

  for (const m of work.movements) {
    blocks.push([
      `${m.number} ${m.title}`, m.voicing,
      `${m.number} ${m.titleTranslation}`.trim(), m.voicingTranslation,
    ].filter(Boolean).join('\n'));

    for (const line of m.lines) {
      blocks.push([line.text, line.translation].filter(Boolean).join('\n'));
    }
  }
  return blocks.join('\n\n') + '\n';
}

const dirs = process.argv.length > 2 ? process.argv.slice(2) : findWorkDirs();
for (const dir of dirs) {
  const out = path.join(dir, OUTPUT_NAME);
  fs.writeFileSync(out, buildText(dir));
  console.log(`wrote ${path.relative(process.cwd(), out)}`);
}
