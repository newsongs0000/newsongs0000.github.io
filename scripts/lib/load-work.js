'use strict';
/*
 * Shared loader for the scripts: reads a work directory (work.js + the *.timing.js of its movements)
 * and returns plain data.
 */
const fs = require('fs');
const path = require('path');

const ASSETS_DIR = path.join(__dirname, '..', '..', 'assets');

// work.js and *.timing.js are not JSON: they call a global function with an object literal.
// Evaluate them with that function defined to capture the object.
function loadCall(file, fnName) {
  let result;
  new Function(fnName, fs.readFileSync(file, 'utf8'))(obj => { result = obj; });
  if (result === undefined) throw new Error(`${file} did not call ${fnName}()`);
  return result;
}

// Trim every physical line (drops layout indentation after embedded "\n") and skip empty ones.
const clean = s => String(s ?? '').split(/\r?\n/).map(x => x.trim()).filter(Boolean).join('\n');

// Every directory under `dir` that contains a work.js.
function findWorkDirs(dir = ASSETS_DIR) {
  const found = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) found.push(...findWorkDirs(full));
    else if (entry.name === 'work.js') found.push(dir);
  }
  return found;
}

/*
 * Returns {
 *   title, titleTranslation, language, translationLanguage,
 *   movements: [{ number, title, titleTranslation, voicing, voicingTranslation,
 *                 lines: [{ text, translation }] }]
 * }
 * `translation` is '' when a timing line has none.
 */
function loadWork(workDir) {
  const work = loadCall(path.join(workDir, 'work.js'), 'onePageMp3Work');

  // work.js "title" is "<main title> <translated title>" (or the reverse); keep the main part.
  const titleTranslation = work.titleTranslation || '';
  const title = titleTranslation && work.title.endsWith(titleTranslation)
    ? work.title.slice(0, -titleTranslation.length).trim()
    : work.title;

  const movements = work.movements.map(m => {
    const timingFile = path.join(workDir, m.audio.replace(/\.mp3$/, '.timing.js'));
    const timing = loadCall(timingFile, 'onePageMp3Timing');
    return {
      number: m.number,
      title: m.title,
      titleTranslation: m.titleTranslation ?? '',
      voicing: m.voicing ?? '',
      voicingTranslation: m.voicingTranslation ?? '',
      lines: timing.lines.map(l => ({ text: clean(l.text), translation: clean(l.translation) })),
    };
  });

  return {
    title, titleTranslation,
    language: work.language, translationLanguage: work.translationLanguage,
    movements,
  };
}

module.exports = { ASSETS_DIR, findWorkDirs, loadWork };
