/* ================================================================
   APP DATA
   Structure: artists[] > works[] > movements[]
   An artist's data is not here: it is read from the artist.js file in
   its assets folder, listed in artistFiles (see ARTIST AND WORK FILES),
   and becomes APP_DATA.artists = [artist, ...] once loaded.
   Likewise a work's data is read from the work.js file in its assets
   folder, listed in its artist's workFiles, and becomes
   artist.works = [work, ...] once loaded.
   A movement's lyrics are not here: they are read from the .timing.js
   file next to its audio (see LYRICS TIMING), and become
   movement.lyrics = [{ text, translation }] once loaded.
   If any line has a translation, the lyrics panel shows two columns:
   each line's original text beside its translation, highlighted together
   (see BILINGUAL LYRICS DIVIDER), unless the Original or Translation
   check box is unchecked (see LYRICS SHOWN). The work's language and
   translationLanguage tell which column is the Chinese one, which gets
   the narrower share of the width.
   Auto mode highlights by the timing in that file (or recorded in this
   browser), else by linear interpolation (approximate sync).
================================================================ */
const APP_DATA = {
  version: "1.0",
  artistFiles: [
    "assets/Handel/artist.js",
    "assets/HuangAnlun/artist.js",
    "assets/Mozart/artist.js"
    /* Add more artists' artist.js files here */
  ],
  artists: []  // filled from artistFiles
};

/* ================================================================
   ARTIST AND WORK FILES
   An artist.js file holds one artist (name, bio, workFiles, ...) wrapped
   in one onePageMp3Artist(...) call; a work.js file holds one work
   (title, description, movements, ...) wrapped in one onePageMp3Work(...)
   call. An artist's workFiles are named relative to its artist.js file
   (workFiles: ["Messiah/work.js"]), a movement's audio and thumbnail relative
   to its work.js file (audio: "Chapter1.mp3"); only artistFiles are relative
   to index.html. So a <script> can load them when the page is opened as file://
   (fetch of local files is blocked).
================================================================ */
const ARTIST_CALLBACK = 'onePageMp3Artist';  // what an artist.js file calls
const WORK_CALLBACK   = 'onePageMp3Work';    // what a work.js file calls
const loadedData      = new Map();           // <script> element -> { callback, data } it handed over

window[ARTIST_CALLBACK] = data => loadedData.set(document.currentScript, { callback: ARTIST_CALLBACK, data });
window[WORK_CALLBACK]   = data => loadedData.set(document.currentScript, { callback: WORK_CALLBACK, data });

// Run one artist.js or work.js file, which must call `callback`.
// Resolves to the data it handed over, or null if the file is missing or broken.
function loadDataFile(url, callback) {
  return new Promise(resolve => {
    const script = document.createElement('script');
    script.src = url + (location.protocol === 'file:' ? '' : `?t=${Date.now()}`);
    script.onerror = () => {
      script.remove();
      console.warn(`Cannot load ${url}`);
      resolve(null);
    };
    script.onload = () => {
      script.remove();
      const loaded = loadedData.get(script);
      loadedData.delete(script);
      if (loaded?.callback !== callback) console.warn(`${url} did not call ${callback}(...)`);
      const data = loaded?.callback === callback ? loaded.data : null;
      if (data && callback === WORK_CALLBACK) resolveWorkPaths(data, url);
      if (data && callback === ARTIST_CALLBACK) resolveArtistPaths(data, url);
      resolve(data);
    };
    document.head.append(script);
  });
}

// The folder of a data file's URL, with its trailing slash
function dirOf(url) {
  return url.slice(0, url.lastIndexOf('/') + 1);
}

// An artist's workFiles are named relative to its artist.js file
function resolveArtistPaths(artist, artistUrl) {
  const dir = dirOf(artistUrl);
  artist.workFiles = (artist.workFiles ?? []).map(file => dir + file);
}

// A work's movement files (audio, thumbnail) are named relative to its work.js file:
// make them relative to index.html, as the rest of app.js uses them
function resolveWorkPaths(work, workUrl) {
  const dir = dirOf(workUrl);
  (work.movements ?? []).forEach(movement => {
    ['audio', 'thumbnail'].forEach(key => {
      if (movement[key]) movement[key] = dir + movement[key];
    });
  });
}

// Load all files listed in urls, keeping the listed order and dropping those that fail
async function loadDataFiles(urls, callback) {
  return (await Promise.all((urls ?? []).map(url => loadDataFile(url, callback)))).filter(Boolean);
}

// Fill APP_DATA.artists from artistFiles, then each artist's works from its workFiles
async function loadArtists() {
  APP_DATA.artists = await loadDataFiles(APP_DATA.artistFiles, ARTIST_CALLBACK);
  await Promise.all(APP_DATA.artists.map(async artist => {
    artist.works = await loadDataFiles(artist.workFiles, WORK_CALLBACK);
  }));
}

/* ================================================================
   CONFIGURATION — apply URL params to CSS custom properties
   Example: index.html?above-color=%238888aa&below-bg=rgba(0,0,0,0.2)
   Lyrics highlight mode, audio mute, lyrics shown and font size are kept in the URL too
   (mute is used only by index-sound.html; index.html is always muted, see MUTE):
   index-sound.html?highlight-mode=auto&mute=0&show=both&font=100&chinese-width=45&timing=collapsed
   (see VIEW OPTIONS IN URL)
   Selected movement: index.html?movement=<artist id>/<work id>/<movement id>
   (see MOVEMENT IN URL), at a position in whole seconds: &t=83 (see POSITION IN URL)
================================================================ */
(function applyConfig() {
  const params = new URLSearchParams(window.location.search);
  const propMap = {
    'above-color': '--lyrics-above-color',
    'above-bg':    '--lyrics-above-bg',
    'below-color': '--lyrics-below-color',
    'below-bg':    '--lyrics-below-bg'
  };
  Object.entries(propMap).forEach(([param, prop]) => {
    const val = params.get(param);
    if (val) document.documentElement.style.setProperty(prop, val);
  });
})();

/* ================================================================
   STATE
================================================================ */
const state = {
  composerIdx:  null,
  workIdx:      null,
  movementIdx:  null,
  isPlaying:    false,
  lastLyricIdx: -1,
  allMovements: [],  // flat list for prev/next
  lyricsShown:  { original: true, translation: true },  // see LYRICS SHOWN
  highlightMode: 'auto'  // set from the URL, see VIEW OPTIONS IN URL
};

const audio = document.getElementById('audio');

/* ================================================================
   BUILD FLAT MOVEMENT LIST  (used for Prev/Next navigation)
================================================================ */
function buildFlatList() {
  state.allMovements = [];
  APP_DATA.artists.forEach((composer, ci) => {
    composer.works.forEach((work, wi) => {
      work.movements.forEach((movement, mi) => {
        state.allMovements.push({ composerIdx: ci, workIdx: wi, movementIdx: mi,
          data: movement, composer, work });
      });
    });
  });
}

/* ================================================================
   BUILD NAVIGATION TREE
================================================================ */
// Artists, and an artist's works, in tree order (alphabetical)
function sortedArtists() {
  return [...APP_DATA.artists].sort((a, b) =>
    (a.nameSort || a.name).localeCompare(b.nameSort || b.name)
  );
}

function sortedWorks(composer) {
  return [...composer.works].sort((a, b) =>
    (a.titleSort || a.title).localeCompare(b.titleSort || b.title)
  );
}

function buildTree() {
  const tree = document.getElementById('composer-tree');
  tree.innerHTML = '';

  sortedArtists().forEach(composer => {
    const composerEl = document.createElement('div');
    composerEl.className = 'tree-composer';  // artist and work folders start collapsed

    const composerHeader = document.createElement('div');
    composerHeader.className = 'tree-composer-header';
    composerHeader.innerHTML =
      `<span class="tree-toggle">&#9658;</span><span>${escHtml(composer.name)}</span>`;
    composerHeader.addEventListener('click', () => composerEl.classList.toggle('open'));

    const worksEl = document.createElement('div');
    worksEl.className = 'tree-works';

    sortedWorks(composer).forEach(work => {
      const workEl = document.createElement('div');
      workEl.className = 'tree-work';

      const workHeader = document.createElement('div');
      workHeader.className = 'tree-work-header';
      workHeader.innerHTML =
        `<span class="tree-toggle">&#9658;</span><span>${escHtml(work.title)}</span>`;
      workHeader.addEventListener('click', () => workEl.classList.toggle('open'));

      const movementsEl = document.createElement('div');
      movementsEl.className = 'tree-movements';

      work.movements.forEach(movement => {
        const movEl = document.createElement('div');
        movEl.className = 'tree-movement';
        movEl.dataset.key = movementKey(movement);  // movement ids are only unique within a work
        movEl.textContent = `${movement.number}. ${movement.title}`;
        movEl.addEventListener('click', () => loadMovement(composer, work, movement));
        movementsEl.appendChild(movEl);
      });

      workEl.appendChild(workHeader);
      workEl.appendChild(movementsEl);
      worksEl.appendChild(workEl);
    });

    composerEl.appendChild(composerHeader);
    composerEl.appendChild(worksEl);
    tree.appendChild(composerEl);
  });
}

// On page load: select the movement named in the URL (see MOVEMENT IN URL), at the
// position in the URL (see POSITION IN URL), else the first movement of the first
// artist's first work in the tree (skipping any without one), opening their folders to
// show it
function selectInitialMovement() {
  const fromUrl = movementFromUrl();
  const entry = fromUrl ?? firstTreeMovement();
  if (!entry) return;
  loadMovement(entry.composer, entry.work, entry.data);
  if (fromUrl) startAtTimeFromUrl();
  const movEl = document.querySelector('.tree-movement.active');
  movEl?.closest('.tree-work').classList.add('open');
  movEl?.closest('.tree-composer').classList.add('open');
}

function firstTreeMovement() {
  for (const composer of sortedArtists()) {
    for (const work of sortedWorks(composer)) {
      const movement = work.movements?.[0];
      if (movement) return movementEntry(movement);
    }
  }
  return null;
}

/* ================================================================
   MOVEMENT IN URL
   The selected movement is kept in the URL parameter movement, as
   <artist id>/<work id>/<movement id>, so reloading or sharing the link
   opens the same movement:
   index.html?movement=anlun-huang/chinese-requiem/ch2
================================================================ */
const MOVEMENT_PARAM = 'movement';

// The flat-list entry of the movement named in the URL, or null
function movementFromUrl() {
  const key = new URLSearchParams(location.search).get(MOVEMENT_PARAM);
  if (!key) return null;
  const entry = state.allMovements.find(e => movementKey(e.data) === key);
  if (!entry) console.warn(`No movement "${key}" (URL parameter ${MOVEMENT_PARAM})`);
  return entry ?? null;
}

// Rewrite the URL to name the movement; selecting another movement drops the position
// (see POSITION IN URL)
function setMovementInUrl(movement) {
  const key = movementKey(movement);
  const values = { [MOVEMENT_PARAM]: key };
  if (new URLSearchParams(location.search).get(MOVEMENT_PARAM) !== key) values[TIME_PARAM] = null;
  rewriteUrlParams(values);
}

// Set the URL parameters (null removes one), keeping the others and adding no history
// entry
function rewriteUrlParams(values) {
  const params = new URLSearchParams(location.search);
  Object.entries(values).forEach(([name, value]) => {
    if (value == null) params.delete(name);
    else params.set(name, value);
  });
  if (params.has(TIME_PARAM)) {  // the position, which changes most often, goes last
    const time = params.get(TIME_PARAM);
    params.delete(TIME_PARAM);
    params.set(TIME_PARAM, time);
  }
  const search = params.toString().replace(/%2F/g, '/');  // keep the movement key readable
  try {
    history.replaceState(history.state, '', `?${search}${location.hash}`);
  } catch (err) {
    console.warn('Cannot rewrite the URL:', err.message);
  }
}

/* ================================================================
   POSITION IN URL
   The audio position of the selected movement is kept in the URL parameter t,
   in seconds rounded down, so reloading or sharing the link continues from there:
   index.html?movement=anlun-huang/chinese-requiem/ch2&t=83
   It is used only with the movement parameter, and dropped (as at 0) when another
   movement is selected. Browsers limit how often history.replaceState may be
   called, so it is rewritten at most once every TIME_URL_INTERVAL ms.
================================================================ */
const TIME_PARAM = 't';
const TIME_URL_INTERVAL = 1000;  // ms

const timeInUrl = {
  start:   null,  // seconds to seek to once the audio is loaded; the URL is kept until then
  written: 0,     // Date.now() of the last rewrite
  timer:   null   // pending rewrite, for a position given within the interval
};

// Seek the movement just loaded to the position in the URL, once its audio is loaded
// (see the loadedmetadata listener); a position that isn't a number above 0 is dropped
function startAtTimeFromUrl() {
  const time = Number(new URLSearchParams(location.search).get(TIME_PARAM));
  if (time > 0 && isFinite(time)) timeInUrl.start = time;
  else rewriteUrlParams({ [TIME_PARAM]: null });
}

// Write the audio position to the URL: now, or when the interval since the last
// rewrite ends (then it writes the position at that moment)
function updateTimeInUrl() {
  if (timeInUrl.start !== null || timeInUrl.timer) return;
  const wait = timeInUrl.written + TIME_URL_INTERVAL - Date.now();
  if (wait > 0) {
    timeInUrl.timer = setTimeout(() => {
      timeInUrl.timer = null;
      updateTimeInUrl();
    }, wait);
    return;
  }
  timeInUrl.written = Date.now();
  const time = Math.floor(audio.currentTime);
  rewriteUrlParams({ [TIME_PARAM]: time > 0 ? time : null });
}

/* ================================================================
   VIEW OPTIONS IN URL
   The view options are kept in URL parameters, always written in full, so
   reloading or sharing the link restores them (a missing or invalid value
   gives the default):
     highlight-mode  auto | manual                 (default auto; see LYRICS HIGHLIGHT MODE)
     mute            1 | 0                         (default 0, unmuted; see MUTE)
     show            original | translation | both (default both; see LYRICS SHOWN)
     font            lyrics font size in percent, 10-250 (default 100; see LYRICS FONT SIZE)
     chinese-width   the Chinese lyrics column's percent of the width, 20-80 (default 45;
                     see BILINGUAL LYRICS DIVIDER)
     timing          open | collapsed, the Lyrics Timing panel (default collapsed; see
                     setTimingPanelOpen)
     view-options    open | collapsed, the View Options panel, which only a smartphone layout can
                     collapse (default collapsed; see setViewPanelOpen)
   index-sound.html?highlight-mode=manual&mute=1&show=translation&font=150&chinese-width=45&timing=open&view-options=open
================================================================ */
function urlParam(name) {
  return new URLSearchParams(location.search).get(name);
}

/* ================================================================
   LOAD MOVEMENT
================================================================ */
// Now-playing header, following the Show check boxes (see LYRICS SHOWN): Original
// shows the work and movement titles, Translation their titleTranslations (if any)
// after them; Translation alone shows only the translations (a title without one
// shows its original)
function updateNowPlaying(work, movement) {
  const { original: showOriginal, translation: showTranslation } = state.lyricsShown;
  const [workTitle, movementTitle] = showOriginal
    ? [work.title, movement.title]
    : [work.titleTranslation || work.title, movement.titleTranslation || movement.title];
  document.getElementById('np-label').textContent = workTitle;
  document.getElementById('np-title').textContent = `${movement.number}. ${movementTitle}`;
  document.getElementById('np-label-translation').textContent = work.titleTranslation || '';
  document.getElementById('np-title-translation').textContent =
    movement.titleTranslation ? `${movement.number}. ${movement.titleTranslation}` : '';
  document.getElementById('np-translation').hidden =
    !showOriginal || !showTranslation || (!work.titleTranslation && !movement.titleTranslation);
}

function loadMovement(composer, work, movement, autoplay = false) {
  // Update state
  const flatEntry = movementEntry(movement);
  if (flatEntry) {
    state.composerIdx  = flatEntry.composerIdx;
    state.workIdx      = flatEntry.workIdx;
    state.movementIdx  = flatEntry.movementIdx;
  }
  state.lastLyricIdx = -1;
  timeInUrl.start = null;
  setMovementInUrl(movement);

  // Highlight active tree node
  document.querySelectorAll('.tree-movement').forEach(el => {
    el.classList.toggle('active', el.dataset.key === movementKey(movement));
  });

  updateNowPlaying(work, movement);

  // Update info pane
  document.getElementById('info-composer').textContent = composer.name;
  document.getElementById('info-work').textContent =
    `${work.title}${work.opusNumber ? ' ' + work.opusNumber : ''}${work.year ? ' (' + work.year + ')' : ''}`;
  document.getElementById('info-dates').textContent =
    work.premiered ? `Premiere: ${work.premiered}` : '';
  document.getElementById('info-description').textContent = work.description || '';

  // Load audio
  audio.src = movement.audio;
  audio.load();  // stops what was playing, without a 'pause' event
  showPlaying(false);
  pickLineOnPlay = false;
  resetProgress();

  // Show thumbnail overlay if a thumbnail is available
  const overlay = document.getElementById('thumbnail-overlay');
  const thumbImg = document.getElementById('thumbnail-img');
  if (movement.thumbnail) {
    thumbImg.src = movement.thumbnail;
    thumbImg.alt = movement.title;
    overlay.classList.remove('hidden');
  } else {
    overlay.classList.add('hidden');
  }

  // Render lyrics (none until they are loaded)
  renderLyrics(movement);
  updateNavButtons();
  updateTimingPanel();

  // Lyrics come from the timing file next to the audio, loaded on first use
  if (!movement.lyrics) {
    loadTiming(movement).then(() => {
      if (currentMovement() !== movement) return;
      renderLyrics(movement);
      updateTimingPanel();
    });
  }

  if (autoplay) {
    audio.play().catch(() => {});
  }
}

/* ================================================================
   RENDER LYRICS
================================================================ */
// keepHighlight: re-rendering the same movement (the lyrics shown changed), so the
// highlighted line stays
function renderLyrics(movement, keepHighlight = false) {
  const inner = document.getElementById('lyrics-inner');
  inner.innerHTML = '';
  const hasTranslation = !!movement.lyrics?.some(l => l.translation);
  const { original: showOriginal, translation: showTranslation } = state.lyricsShown;
  // Two columns only when both are checked; Translation alone shows one column of
  // translations (a line without one shows its original)
  const bilingual       = hasTranslation && showOriginal && showTranslation;
  const translationOnly = hasTranslation && !showOriginal;
  inner.classList.toggle('bilingual', bilingual);
  // The Chinese column keeps its width on either side (see BILINGUAL LYRICS DIVIDER)
  inner.classList.toggle('chinese-translation', bilingual && translationIsChinese(currentWork()));
  if (bilingual) inner.appendChild(lyricsDivider);

  const topSpacer = document.createElement('div');
  topSpacer.className = 'lyrics-spacer';
  inner.appendChild(topSpacer);

  if (!movement.lyrics) {
    // Still loading (see loadMovement)
  } else if (movement.lyrics.length === 0) {
    const msg = document.createElement('p');
    msg.className = 'no-song-msg';
    msg.textContent = 'No lyrics available for this movement.';
    inner.appendChild(msg);
  } else {
    // Movement heading (bilingual: the translated heading heads the translation column)
    const meta = document.createElement('div');
    meta.className = 'lyric-meta';
    const heading = translationOnly
      ? movementHeading(movement.number, movement.titleTranslation || movement.title,
          movement.subtitleTranslation || movement.subtitle, movement.voicingTranslation || movement.voicing)
      : movementHeading(movement.number, movement.title, movement.subtitle, movement.voicing);
    if (bilingual) {
      const original    = document.createElement('span');
      const translation = document.createElement('span');
      original.className    = 'lyric-original';
      translation.className = 'lyric-translation';
      original.textContent    = heading;
      translation.textContent = movementHeading(movement.number, movement.titleTranslation,
        movement.subtitleTranslation, movement.voicingTranslation);
      meta.append(original, translation);
    } else {
      meta.textContent = heading;
    }
    meta.style.whiteSpace = 'pre-line';
    inner.appendChild(meta);

    // Lyric lines (bilingual: one row of two cells, so both are highlighted together)
    movement.lyrics.forEach((lyric, idx) => {
      const el = document.createElement('div');
      el.className = 'lyric-line';
      el.dataset.index = idx;
      if (bilingual) {
        const original    = document.createElement('span');
        const translation = document.createElement('span');
        original.className    = 'lyric-original';
        translation.className = 'lyric-translation';
        original.textContent    = lyric.text;
        translation.textContent = lyric.translation;
        el.append(original, translation);
      } else {
        el.textContent = translationOnly ? lyric.translation || lyric.text : lyric.text;
      }
      // Clicking seeks to where the line starts (see lyricLineStartTime); in manual mode it
      // also jumps the highlight to this line. While recording it doesn't seek: the click
      // records the line's time from where the audio is.
      el.addEventListener('click', () => {
        if (state.highlightMode === 'manual') selectLyricLine(idx);
        if (timing.recording) return;
        const time = lyricLineStartTime(movement, idx);
        if (time != null) audio.currentTime = time;
      });
      inner.appendChild(el);
    });
  }

  const bottomSpacer = document.createElement('div');
  bottomSpacer.className = 'lyrics-spacer';
  inner.appendChild(bottomSpacer);

  // Manual mode starts with no line highlighted; the first key press highlights line 0
  const idx = keepHighlight                   ? state.lastLyricIdx
            : state.highlightMode === 'manual' ? -1 : getCurrentLyricIdx();
  highlightLyricLine(idx, true);
}

// "number. title [subtitle]", then voicing on a second line; missing parts are left out
function movementHeading(number, title, subtitle, voicing) {
  const firstLine = [title && `${number}. ${title}`, subtitle && `[${subtitle}]`].filter(Boolean).join(' ');
  return [firstLine, voicing].filter(Boolean).join('\n');
}

/* ================================================================
   HIGHLIGHT LYRIC LINE   (idx -1 = nothing highlighted yet)
================================================================ */
function highlightLyricLine(idx, force = false) {
  if (idx === state.lastLyricIdx && !force) return;
  state.lastLyricIdx = idx;

  const lines = document.querySelectorAll('.lyric-line');
  lines.forEach((el, i) => {
    el.classList.remove('before', 'current', 'after', 'distant');
    const diff = i - idx;
    if (diff === 0)        el.classList.add('current');
    else if (diff < 0)     el.classList.add(Math.abs(diff) <= 4 ? 'before' : 'distant');
    else                   el.classList.add(diff <= 4 ? 'after' : 'distant');
  });

  updateSelectedLineTime();
  centerCurrentLine();
}

// Scroll the current line to vertical center of container (top if none)
function centerCurrentLine() {
  const currentEl = document.querySelector('.lyric-line.current');
  const container = document.getElementById('lyrics-container');
  if (currentEl && container) {
    const cRect = container.getBoundingClientRect();
    const eRect = currentEl.getBoundingClientRect();
    const desired = container.scrollTop + (eRect.top - cRect.top)
                    - cRect.height / 2 + eRect.height / 2;
    container.scrollTo({ top: desired, behavior: 'smooth' });
  } else if (container) {
    container.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

/* ================================================================
   LYRICS HIGHLIGHT MODE
   auto:   current line follows audio time (timestamps or interpolation)
   manual: operator moves the highlight with the keyboard (see KEYBOARD
           SHORTCUTS) or by clicking a line (which also seeks there, unless
           recording); audio time doesn't move the highlight
================================================================ */
function setHighlightMode(mode) {
  state.highlightMode = mode;
  rewriteUrlParams({ 'highlight-mode': mode });
  document.querySelectorAll('#mode-toggle .ctrl-btn').forEach(btn => {
    const on = btn.dataset.mode === mode;
    btn.classList.toggle('active', on);
    btn.setAttribute('aria-pressed', on);
  });
  document.getElementById('manual-hint').hidden = mode !== 'manual';
  document.getElementById('lyrics-container').dataset.mode = mode;  // swipes only in manual (see SWIPE)

  // Recording captures manual selections only
  if (mode !== 'manual' && timing.recording) setRecording(false);

  // Back to auto: resync the highlight to the audio position
  if (mode === 'auto' && state.composerIdx !== null) {
    highlightLyricLine(getCurrentLyricIdx());
  }
}

function stepLyricLine(delta) {
  const movement = currentMovement();
  if (!movement || !movement.lyrics || movement.lyrics.length === 0) return;
  const idx = Math.max(-1, Math.min(movement.lyrics.length - 1, state.lastLyricIdx + delta));
  selectLyricLine(idx);
  // Lyrics may be driven without audio (e.g. live singing) — don't leave them hidden
  document.getElementById('thumbnail-overlay').classList.add('hidden');
}

// Operator moved the highlight (key or click) in manual mode
function selectLyricLine(idx) {
  const prevIdx = state.lastLyricIdx;
  highlightLyricLine(idx);
  recordLineTime(idx, prevIdx);
}

/* ================================================================
   SWIPE
   Touch screens have no arrow keys, so in manual mode a swipe on the lyrics
   steps the highlight like them: up or left = next line (↓ →), down or
   right = previous (↑ ←). A tap on a line still selects it. The lyrics
   do not scroll by touch in manual mode (touch-action: none in
   common.css); the highlighted line is kept centered anyway.
================================================================ */
const SWIPE_MIN = 40;  // px
(() => {
  const container = document.getElementById('lyrics-container');
  let start = null;
  container.addEventListener('pointerdown', e => {
    start = e.pointerType === 'touch' && e.isPrimary && !e.target.closest('.lyrics-divider')
      ? { x: e.clientX, y: e.clientY } : null;
  });
  container.addEventListener('pointercancel', () => { start = null; });
  container.addEventListener('pointerup', e => {
    if (!start || state.highlightMode !== 'manual') { start = null; return; }
    const dx = e.clientX - start.x, dy = e.clientY - start.y;
    start = null;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < SWIPE_MIN) return;  // a tap
    const delta = Math.abs(dy) >= Math.abs(dx) ? (dy < 0 ? 1 : -1) : (dx < 0 ? 1 : -1);
    stepLyricLine(delta);
  });
})();

document.querySelectorAll('#mode-toggle .ctrl-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    setHighlightMode(btn.dataset.mode);
    btn.blur();  // so Space doesn't re-activate the button
  });
});

/* ================================================================
   MAXIMIZE LYRICS PANEL
   Hides the left nav pane (including the Lyrics mode and Maximize
   buttons), the top-panel buttons, the bottom control section and the
   info pane; lyrics font grows (CSS). Esc restores. Space / arrow keys
   still control playback.
================================================================ */
function setLyricsMaximized(on) {
  const app = document.getElementById('app');
  if (app.classList.contains('lyrics-maximized') === on) return;
  app.classList.toggle('lyrics-maximized', on);
  // Also full screen at browser window level (not available everywhere, e.g. iPhone Safari)
  try {
    if (on && !document.fullscreenElement && document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else if (!on && document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    }
  } catch (_) { /* ignore */ }
  // Re-center after the lyric font-size transition (0.3s) settles
  setTimeout(centerCurrentLine, 350);
}

// The browser's own Esc (or F11-style exit) leaves full screen: leave maximized too
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement) setLyricsMaximized(false);
});

document.getElementById('btn-maximize').addEventListener('click', e => {
  e.currentTarget.blur();
  setLyricsMaximized(true);
});

document.getElementById('btn-restore').addEventListener('click', e => {
  e.currentTarget.blur();
  setLyricsMaximized(false);
});

/* ================================================================
   LYRICS SHOWN
   The Original / Translation check boxes: both checked shows the two
   columns (for a movement with a translation), Original alone the
   original lyrics, Translation alone the translations (a line without
   one shows its original). The top bar's titles follow them too (see
   updateNowPlaying). At least one stays checked: the last checked box
   is disabled. Kept in the URL parameter show (see VIEW OPTIONS IN URL).
================================================================ */
const lyricsShownBoxes = [...document.querySelectorAll('#lyrics-shown input')];

// Sync state, the disabled flags and the URL with the check boxes
function syncLyricsShown() {
  lyricsShownBoxes.forEach(b => { state.lyricsShown[b.value] = b.checked; });
  const checked = lyricsShownBoxes.filter(b => b.checked);
  lyricsShownBoxes.forEach(b => { b.disabled = checked.length === 1 && b.checked; });
  rewriteUrlParams({ show: checked.length === 1 ? checked[0].value : 'both' });
}

{
  const show = urlParam('show');
  lyricsShownBoxes.forEach(b => { b.checked = show !== 'original' && show !== 'translation' || b.value === show; });
  syncLyricsShown();
}

lyricsShownBoxes.forEach(box => {
  box.addEventListener('change', () => {
    syncLyricsShown();
    box.blur();  // so Space / arrow keys keep controlling playback and lyrics

    const movement = currentMovement();
    if (movement) {
      renderLyrics(movement, true);
      updateNowPlaying(currentWork(), movement);
    }
  });
});

/* ================================================================
   MUTE
   The Mute check box silences the audio without stopping it: playback
   goes on, so the lyrics, the progress bar and timing recording follow
   it as usual. The audio is unmuted by default: check the box to silence it.
   The box's state stays from one movement to the next. Kept in the URL
   parameter mute (see VIEW OPTIONS IN URL).

   index.html (the default page) ships the box checked and disabled (and
   hidden): the audio is then always silent, the URL parameter mute is ignored
   and not written, and the user cannot unmute. index-sound.html has the
   usual, visible, unchecked box.

   The silent page does NOT set audio.muted: on mobile browsers (iOS Safari
   in particular) an element that is muted from the start gets no audio
   output to keep time with, and its currentTime races to the end of the
   movement as soon as ▶ is pressed. Instead the element plays normally,
   into a Web Audio gain node set to 0, which keeps a real audio output
   (and so a real clock) running while nothing is heard. Browsers keep an
   AudioContext suspended until a user gesture, so it is resumed on the
   first gesture (and again after an interruption, e.g. a phone call).
   Without Web Audio the page falls back to audio.muted.
================================================================ */
const muteBox = document.getElementById('chk-mute');
const muteLocked = muteBox.disabled;

// Make the audio silent without muting the element; false if Web Audio is not available
function silenceAudioViaWebAudio() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return false;
  try {
    const context = new AudioContextClass();
    const gain = context.createGain();
    gain.gain.value = 0;
    context.createMediaElementSource(audio).connect(gain);
    gain.connect(context.destination);

    const resume = () => { if (context.state !== 'running') context.resume().catch(() => {}); };
    ['pointerdown', 'touchend', 'click', 'keydown'].forEach(type =>
      document.addEventListener(type, resume, { capture: true, passive: true }));
    document.addEventListener('visibilitychange', () => { if (!document.hidden) resume(); });
    audio.addEventListener('play', resume);
    return true;
  } catch (err) {
    console.warn('Cannot silence the audio with Web Audio, muting it instead:', err);
    return false;
  }
}

audio.muted = muteLocked ? !silenceAudioViaWebAudio() : urlParam('mute') === '1';
muteBox.checked = muteLocked || audio.muted;  // also overrides a box state a reload brings back (Firefox)
if (!muteLocked) rewriteUrlParams({ mute: audio.muted ? 1 : 0 });

muteBox.addEventListener('change', () => {
  if (muteLocked) return;
  audio.muted = muteBox.checked;
  rewriteUrlParams({ mute: audio.muted ? 1 : 0 });
  muteBox.blur();  // so Space / arrow keys keep controlling playback and lyrics
});

/* ================================================================
   LYRICS FONT SIZE
   A+ / A- scale the lyrics (--lyrics-font-scale, 10%-250%, steps of 10%);
   click the percentage to reset. Kept in the URL parameter font (see VIEW OPTIONS IN URL).
================================================================ */
(function () {
  let pct = 100;
  const label = document.getElementById('font-size-value');
  function apply(v) {
    pct = Math.max(10, Math.min(250, v));
    document.documentElement.style.setProperty('--lyrics-font-scale', pct / 100);
    label.textContent = pct + '%';
    rewriteUrlParams({ font: pct });
  }
  [['btn-font-down', -10], ['btn-font-up', 10]].forEach(([id, d]) => {
    const b = document.getElementById(id);
    b.addEventListener('click', () => { apply(pct + d); b.blur(); });
  });
  label.addEventListener('click', () => apply(100));
  const fromUrl = Number(urlParam('font'));
  apply(urlParam('font') && isFinite(fromUrl) ? Math.round(fromUrl) : 100);
})();

/* ================================================================
   BILINGUAL LYRICS DIVIDER
   The width belongs to the Chinese column, on whichever side it is: the
   original (left) column when the work's language is Chinese, the
   translation (right) column when its translationLanguage is. With no
   Chinese column it is the original's.
   Drag the line between the original and translation columns to set
   that column's share of the width (DIVIDER_MIN–DIVIDER_MAX percent);
   double-click it to go back to the default (45%, DEFAULT_CHINESE_WIDTH;
   keep --lyrics-chinese-width in common.css the same). The width is kept in
   the URL parameter chinese-width (see VIEW OPTIONS IN URL).
================================================================ */
const DIVIDER_MIN = 20;
const DIVIDER_MAX = 80;
const DEFAULT_CHINESE_WIDTH = 45;  // percent; the other column gets the rest

// True when the Chinese lyrics are the work's translations (the right column): its
// translationLanguage is Chinese ("zh", "zh-Hant", ...) and its language is not
function translationIsChinese(work) {
  const isChinese = language => /^zh\b/i.test(language ?? '');
  return isChinese(work?.translationLanguage) && !isChinese(work?.language);
}

// pct: the Chinese column's percent of the lyrics width, or null for the default;
// written to the URL
function setChineseWidth(pct) {
  if (pct === null) pct = DEFAULT_CHINESE_WIDTH;
  document.documentElement.style.setProperty('--lyrics-chinese-width', `${pct}%`);
  rewriteUrlParams({ 'chinese-width': pct });
}

{
  const fromUrl = Number(urlParam('chinese-width'));
  const valid = urlParam('chinese-width') && isFinite(fromUrl);
  setChineseWidth(valid ? Math.round(Math.min(DIVIDER_MAX, Math.max(DIVIDER_MIN, fromUrl)) * 10) / 10 : null);
}

// One divider, put back into #lyrics-inner by renderLyrics for bilingual lyrics
const lyricsDivider = (() => {
  const divider = document.createElement('div');
  divider.className = 'lyrics-divider';
  divider.setAttribute('role', 'separator');
  divider.setAttribute('aria-orientation', 'vertical');
  divider.title = 'Drag to resize the columns; double-click to reset';

  divider.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    e.preventDefault();  // no text selection while dragging
    divider.setPointerCapture(e.pointerId);
    divider.classList.add('dragging');
  });
  divider.addEventListener('pointermove', e => {
    if (!divider.hasPointerCapture(e.pointerId)) return;
    const inner = divider.parentElement;
    const rect  = inner.getBoundingClientRect();
    // The pointer is at the left column's right edge; the Chinese column may be the right one
    const left  = Math.min(DIVIDER_MAX, Math.max(DIVIDER_MIN, (e.clientX - rect.left) / rect.width * 100));
    const pct   = inner.classList.contains('chinese-translation') ? 100 - left : left;
    setChineseWidth(Math.round(pct * 10) / 10);
  });
  // Drag ended (pointer released or cancelled)
  divider.addEventListener('lostpointercapture', () => {
    divider.classList.remove('dragging');
    centerCurrentLine();  // lines re-wrapped, so the current one may have moved
  });
  divider.addEventListener('dblclick', () => {
    setChineseWidth(null);
    centerCurrentLine();
  });
  return divider;
})();

/* ================================================================
   COMPUTE CURRENT LYRIC INDEX from audio time
================================================================ */
function getCurrentLyricIdx() {
  const movement = currentMovement();
  if (!movement || !movement.lyrics || movement.lyrics.length === 0) return 0;

  const lyrics   = movement.lyrics;
  const duration = isFinite(audio.duration) ? audio.duration : 1;
  const t        = audio.currentTime;

  // Timed lyrics: the line that started most recently (-1 before the first line).
  // Untimed lines are skipped; a partial re-recording may leave times out of order.
  const times = lyricTimes(movement);
  if (times) {
    let idx = -1, start = -Infinity;
    times.forEach((time, i) => {
      if (time !== null && time <= t && time >= start) { idx = i; start = time; }
    });
    return idx;
  }

  // Linear interpolation fallback
  return Math.min(
    Math.floor((t / duration) * lyrics.length),
    lyrics.length - 1
  );
}

// Audio time where lyric line idx starts, for seeking to it (null while the duration
// needed is unknown). A timed line starts at its time. An untimed line is placed evenly
// between the nearest timed lines around it — the audio's start and end stand in where
// there is none — so with no timing at all this inverts the linear interpolation above.
function lyricLineStartTime(movement, idx) {
  const times = lyricTimes(movement) ?? [];
  if (times[idx] != null) return times[idx];

  const n = movement.lyrics.length;
  let prev = idx, next = idx;
  while (prev >= 0 && times[prev] == null) prev--;
  while (next < n && times[next] == null) next++;
  const [prevIdx, prevTime] = prev >= 0 ? [prev, times[prev]] : [0, 0];
  const [nextIdx, nextTime] = next < n  ? [next, times[next]] : [n, audio.duration];
  if (!isFinite(nextTime)) return null;
  const t = prevTime + (idx - prevIdx) / (nextIdx - prevIdx) * (nextTime - prevTime);
  // A hair later, so rounding can't land the interpolated highlight on the line before
  return Math.min(t + 0.01, nextTime);
}

/* ================================================================
   LYRICS TIMING — the lyrics and their timing: load, record, save
   Each movement's lyrics live in <audio>.timing.js next to its MP3 (the
   only copy: edit the text there). Every line has a start time, or null
   until it is timed, and optionally a translation.
   Rec:   arms recording (switches to manual mode). While the audio
          plays, each line the operator advances to (key or click) gets
          the current audio time as its start time. Moving back is a
          correction and records nothing; advancing again overwrites.
   Save:  writes the current movement's timing to <audio>.timing.js
   Load:  reads .timing.js (or older .timing.json) file(s); each names
          its own movement
   Clear: discards the timing recorded in this browser for the current movement
   Clear all: discards the timing recorded in this browser for every movement
   Export: writes every timing kept in this browser to <audio>.timing.js
          in its MP3's folder (Chromium: folder access; others: downloads)
   Recordings persist in localStorage and override the file's times
   (never its text or translations) until Clear.
   The file's "audio" is named relative to the file itself, which sits next
   to its MP3, so it is just the MP3's name ("audio": "Chapter1.mp3"). It
   is informational: the app finds the file from the movement's audio.
   The file is the timing JSON wrapped in one onePageMp3Timing(...)
   call, so a <script> can load it when the page is opened as file://
   (fetch can't).
   Auto mode uses these times instead of linear interpolation.
================================================================ */
const TIMING_FORMAT      = 'onepagemp3-lyrics-timing';
const TIMING_STORAGE_KEY = 'onepagemp3.timing:';
const TIMING_CALLBACK    = 'onePageMp3Timing';  // what a .timing.js file calls

const timing = {
  recording: false,
  byKey:     {},  // movementKey -> { times: [seconds | null per lyric line], source: 'local' | 'file' }
  files:     {},  // movementKey -> timing document read from its .timing.js file
  loads:     {}   // movementKey -> Promise of loadTiming, so each file is read once
};

function movementEntry(movement) {
  return state.allMovements.find(e => e.data === movement);
}

function movementKey(movement) {
  const e = movementEntry(movement);
  return `${e.composer.id}/${e.work.id}/${movement.id}`;
}

// assets/.../Chapter1.mp3 -> assets/.../Chapter1.timing.js
function timingFileUrl(movement) {
  return (movement.audio ?? movement.id).replace(/\.[^./]+$/, '') + '.timing.js';
}

function timingFileName(movement) {
  return timingFileUrl(movement).split('/').pop();
}

// The movement's audio named relative to its .timing.js file, which sits next to the MP3
function timingFileAudio(movement) {
  return movement.audio?.split('/').pop();
}

// Start time (seconds or null) of each lyric line, or null if the movement has no timing
function lyricTimes(movement) {
  return timing.byKey[movementKey(movement)]?.times ?? null;
}

function recordLineTime(idx, prevIdx) {
  if (!timing.recording || audio.paused || idx < 0 || idx <= prevIdx) return;
  const movement = currentMovement();
  const key = movementKey(movement);
  // Build on existing timing so a section can be re-recorded
  const rec = timing.byKey[key] ??=
    { times: (lyricTimes(movement) ?? movement.lyrics.map(() => null)).slice() };
  rec.source = 'local';
  rec.times[idx] = Math.round(audio.currentTime * 1000) / 1000;
  storeTiming(movement);
  updateTimingPanel();
}

function timingDoc(movement) {
  const e = movementEntry(movement);
  const times = lyricTimes(movement) ?? [];
  return {
    format:   TIMING_FORMAT,
    version:  1,
    composer: e.composer.id,
    work:     e.work.id,
    movement: movement.id,
    audio:    timingFileAudio(movement),
    saved:    new Date().toISOString(),
    // A line without a translation has no "translation" key (JSON drops undefined)
    lines:    movement.lyrics.map((l, i) => ({ time: times[i] ?? null, text: l.text,
                                               translation: l.translation || undefined }))
  };
}

// Contents of a .timing.js file: the timing JSON wrapped in one TIMING_CALLBACK call,
// pretty-printed with one lyric line per row so it is easy to read and hand-edit
function timingFileText(doc) {
  const { lines, ...head } = doc;
  return `${TIMING_CALLBACK}(` + JSON.stringify(head, null, 2).slice(0, -2) + ',\n  "lines": [\n' +
    lines.map(l => '    ' + JSON.stringify(l)).join(',\n') + '\n  ]\n});\n';
}

// The timing document in a .timing.js file, or in a plain .timing.json one
function parseTimingFile(text) {
  const json = text.trim().replace(new RegExp(`^${TIMING_CALLBACK}\\(([\\s\\S]*)\\);?$`), '$1');
  return JSON.parse(json);
}

// The movement a timing document names; throws if it is not a valid timing document
function timingDocMovement(doc) {
  if (doc?.format !== TIMING_FORMAT || !Array.isArray(doc.lines)) {
    throw new Error('not a lyrics timing file');
  }
  const e = state.allMovements.find(m =>
    m.composer.id === doc.composer && m.work.id === doc.work && m.data.id === doc.movement);
  if (!e) throw new Error(`unknown movement ${doc.composer}/${doc.work}/${doc.movement}`);
  return e.data;
}

// Attach a timing document to the movement it names; returns that movement.
// The timing file (source 'file') supplies the lyrics; a recording (source 'local') only
// times them, unless the movement has no timing file.
function applyTimingDoc(doc, source) {
  const movement = timingDocMovement(doc);
  if (source === 'file' || !movement.lyrics?.length) {
    movement.lyrics = doc.lines.map(l => ({ text: String(l?.text ?? ''),
                                            translation: String(l?.translation ?? '') }));
  } else if (doc.lines.length !== movement.lyrics.length) {
    console.warn(`Timing for ${doc.movement} has ${doc.lines.length} lines, lyrics have ${movement.lyrics.length}`);
  }
  const times = movement.lyrics.map((_, i) => {
    const t = doc.lines[i]?.time;
    return typeof t === 'number' && isFinite(t) && t >= 0 ? t : null;
  });
  if (times.some(t => t !== null)) {
    timing.byKey[movementKey(movement)] = { times, source };
  } else if (source !== 'file') {
    throw new Error('no timed lines');  // a timing file may hold lyrics not timed yet
  }
  return movement;
}

function storeTiming(movement) {
  try {
    localStorage.setItem(TIMING_STORAGE_KEY + movementKey(movement), JSON.stringify(timingDoc(movement)));
  } catch (err) {
    console.warn('Could not store lyrics timing:', err);
  }
}

// Load a movement's lyrics and timing, once: the timing file next to its audio, then this
// browser's recording on top. Afterwards movement.lyrics is set ([] if there is no file).
function loadTiming(movement) {
  const key = movementKey(movement);
  return timing.loads[key] ??= (async () => {
    const doc = await loadTimingFile(movement);
    try {
      if (doc) applyTimingDoc(doc, 'file');
    } catch (err) {
      delete timing.files[key];
      console.warn(`Ignoring ${timingFileName(movement)}:`, err.message);
    }
    try {
      const stored = localStorage.getItem(TIMING_STORAGE_KEY + key);
      if (stored) applyTimingDoc(JSON.parse(stored), 'local');
    } catch (err) {
      console.warn('Ignoring stored lyrics timing:', err);
    }
    movement.lyrics ??= [];
  })();
}

// Run the .timing.js file next to the audio, which hands its document to TIMING_CALLBACK.
// Resolves to that document, or null if there is no file.
function loadTimingFile(movement) {
  const key = movementKey(movement);
  return new Promise(resolve => {
    const script = document.createElement('script');
    script.src = timingFileUrl(movement) + (location.protocol === 'file:' ? '' : `?t=${Date.now()}`);
    script.onerror = () => { script.remove(); resolve(null); };
    script.onload  = () => {
      script.remove();
      if (!timing.files[key]) console.warn(`${timingFileName(movement)} is not the timing of ${key}`);
      resolve(timing.files[key] ?? null);
    };
    document.head.append(script);
  });
}

window[TIMING_CALLBACK] = doc => {
  timing.files[`${doc?.composer}/${doc?.work}/${doc?.movement}`] = doc;
};

async function saveTimingFile() {
  const movement = currentMovement();
  if (!movement || !lyricTimes(movement)) return;
  const text = timingFileText(timingDoc(movement));
  const name = timingFileName(movement);

  // Chromium: let the user save straight into the assets folder next to the MP3
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: name,
        types: [{ description: 'Lyrics timing', accept: { 'text/javascript': ['.js'] } }]
      });
      const writable = await handle.createWritable();
      await writable.write(text);
      await writable.close();
      return;
    } catch (err) {
      if (err.name === 'AbortError') return;  // user cancelled
      console.warn('Save picker failed, downloading instead:', err);
    }
  }
  downloadFile(name, text);
}

function downloadFile(name, text) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: 'text/javascript' }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// Movements whose timing is kept in this browser (localStorage)
function storedTimingMovements() {
  try {
    return state.allMovements.map(e => e.data)
      .filter(m => localStorage.getItem(TIMING_STORAGE_KEY + movementKey(m)) !== null);
  } catch {
    return [];
  }
}

let timingRootDir = null;  // folder picked for Export, reused for the rest of the session

// The MP3's folder inside the picked one: the picked folder is either the app folder
// (audio paths are relative to index.html) or the MP3's own folder
async function mp3Folder(root, movement) {
  const parts   = movement.audio.split('/');
  const mp3Name = parts.pop();
  try {
    let dir = root;
    for (const part of parts) dir = await dir.getDirectoryHandle(part);
    await dir.getFileHandle(mp3Name);
    return dir;
  } catch {
    await root.getFileHandle(mp3Name);  // throws NotFoundError if the MP3 isn't here either
    return root;
  }
}

// Write every timing kept in this browser next to its MP3, as <audio>.timing.js
async function exportStoredTimings() {
  let root = null;
  if (window.showDirectoryPicker) {
    try {
      root = timingRootDir ??= await window.showDirectoryPicker({ id: 'onepagemp3', mode: 'readwrite' });
    } catch (err) {
      if (err.name !== 'AbortError') alert('Could not open the folder:\n' + err.message);
      return;
    }
  }

  const written = [], failed = [];
  for (const movement of storedTimingMovements()) {
    await loadTiming(movement);  // not in memory yet if the movement wasn't opened this session
    const name = timingFileName(movement);
    const text = timingFileText(timingDoc(movement));
    if (!root) {
      // No folder access (Firefox / Safari): download, to be moved next to the MP3 by hand
      downloadFile(name, text);
      written.push(name);
      continue;
    }
    try {
      const dir = await mp3Folder(root, movement);
      const writable = await (await dir.getFileHandle(name, { create: true })).createWritable();
      await writable.write(text);
      await writable.close();
      written.push(timingFileUrl(movement));
    } catch (err) {
      failed.push(err.name === 'NotFoundError'
        ? `${name}: ${movement.audio.split('/').pop()} is not in the picked folder`
        : `${name}: ${err.message}`);
    }
  }
  if (root && written.length === 0) timingRootDir = null;  // wrong folder: ask again next time

  const report = [];
  if (written.length) {
    report.push(root ? `Exported ${written.length} lyrics timing file(s):`
                     : `Downloaded ${written.length} lyrics timing file(s); move each next to its MP3:`,
                ...written.map(f => '  ' + f));
  }
  if (failed.length) {
    report.push('Could not export (pick the folder that contains index.html):', ...failed.map(f => '  ' + f));
  }
  alert(report.join('\n'));
}

function setRecording(on) {
  timing.recording = on;
  const btn = document.getElementById('btn-record');
  btn.classList.toggle('recording', on);
  btn.setAttribute('aria-pressed', on);
  btn.innerHTML = on ? '&#9632; Stop' : '&#9679; Rec';
  document.getElementById('rec-indicator').hidden = !on;
  if (on && state.highlightMode !== 'manual') setHighlightMode('manual');
  updateTimingPanel();
}

// Under the buttons: number, elapsed time and start time of the selected (highlighted) lyric
// line; with no line selected, the audio time elapsed and a hint. Hidden without lyrics.
function updateSelectedLineTime() {
  const el       = document.getElementById('timing-line-time');
  const movement = currentMovement();
  const idx      = state.lastLyricIdx;
  if (!movement?.lyrics?.length) {
    el.hidden = true;
    return;
  }
  const selected = idx >= 0 && idx < movement.lyrics.length;
  // Times are seconds, in the same format as in the .timing.js file
  document.getElementById('line-elapse').textContent = String(Math.round(audio.currentTime * 1000) / 1000);
  document.getElementById('line-text').hidden  = !selected;
  document.getElementById('line-start').hidden = !selected;
  document.getElementById('line-hint').hidden  = selected;
  if (selected) {
    const time = lyricTimes(movement)?.[idx];
    // First 6 characters (by code point, so a Chinese or accented character is never split)
    const start = [...(movement.lyrics[idx].text ?? '').trim()].slice(0, 6).join('');
    document.getElementById('line-number').textContent = `Line ${idx + 1}`;
    document.getElementById('line-text').textContent   = start;
    document.getElementById('line-start').textContent  = time == null ? 'not timed' : String(time);
  } else {
    document.getElementById('line-number').textContent = 'Line –';
  }
  el.hidden = false;
}

function updateTimingPanel() {
  const movement  = currentMovement();
  const hasLyrics = !!movement?.lyrics?.length;
  const times     = hasLyrics ? lyricTimes(movement) : null;
  const rec       = hasLyrics ? timing.byKey[movementKey(movement)] : null;

  const lines = [];
  if (!hasLyrics) {
    lines.push(!movement         ? 'Select a movement to record its timing.'
             : !movement.lyrics ? 'Loading lyrics…'
             :                    `This movement has no lyrics (no ${timingFileName(movement)}).`);
  } else {
    const timed  = times ? times.filter(t => t !== null).length : 0;
    const origin = !times                ? ''
                 : rec.source === 'file' ? ` · ${timingFileName(movement)}`
                 :                         ' · this browser';
    lines.push(`${movement.number}. ${movement.title}`);
    lines.push(`${timed} / ${movement.lyrics.length} lines timed${origin}`);
  }
  if (timing.recording) {
    lines.push(audio.paused ? 'Play the audio, then press ↓ as each line starts.'
                            : '● Recording — press ↓ as each line starts.');
  }
  document.getElementById('timing-status').textContent = lines.join('\n');

  document.getElementById('btn-record').disabled       = !hasLyrics && !timing.recording;
  document.getElementById('btn-timing-save').disabled  = !times;
  document.getElementById('btn-timing-clear').disabled = rec?.source !== 'local';

  const stored = storedTimingMovements().length;
  document.getElementById('btn-timing-clear-all').disabled = stored === 0;
  const exportBtn = document.getElementById('btn-timing-export');
  exportBtn.disabled    = stored === 0;
  exportBtn.textContent = stored ? `Export ${stored} to MP3 folders` : 'Export to MP3 folders';

  updateSelectedLineTime();
}

// Timing of the current movement changed: refresh the panel and, in auto mode, the highlight
function refreshAfterTimingChange() {
  updateTimingPanel();
  if (state.highlightMode === 'auto' && currentMovement()) {
    highlightLyricLine(getCurrentLyricIdx());
  }
}

// The panel is collapsed to its arrow button unless the URL says open (see VIEW OPTIONS IN
// URL); the button opens and closes it, and the URL follows
function setTimingPanelOpen(open) {
  const btn = document.getElementById('btn-timing-toggle');
  document.getElementById('timing-panel').classList.toggle('collapsed', !open);
  btn.setAttribute('aria-expanded', open);
  btn.title = open ? 'Hide lyrics timing' : 'Show lyrics timing';
  rewriteUrlParams({ timing: open ? 'open' : 'collapsed' });
}

setTimingPanelOpen(urlParam('timing') === 'open');

document.getElementById('btn-timing-toggle').addEventListener('click', e => {
  const btn = e.currentTarget;
  setTimingPanelOpen(btn.getAttribute('aria-expanded') !== 'true');
  btn.blur();  // so Space doesn't re-activate the button
});

// The View Options panel (#view-panel: lyrics mode, Maximize, Show, Audio / Font) can be collapsed
// on a smartphone only (the CSS shows its title bar and hides its body in a narrow window); it
// starts collapsed to its title and arrow unless the URL says open (see VIEW OPTIONS IN URL)
function setViewPanelOpen(open) {
  const btn = document.getElementById('btn-view-toggle');
  document.getElementById('view-panel').classList.toggle('collapsed', !open);
  btn.setAttribute('aria-expanded', open);
  btn.title = open ? 'Hide view options' : 'Show view options';
  rewriteUrlParams({ 'view-options': open ? 'open' : 'collapsed' });
}

setViewPanelOpen(urlParam('view-options') === 'open');

document.getElementById('btn-view-toggle').addEventListener('click', e => {
  const btn = e.currentTarget;
  setViewPanelOpen(btn.getAttribute('aria-expanded') !== 'true');
  btn.blur();  // so Space doesn't re-activate the button
});

document.getElementById('btn-record').addEventListener('click', e => {
  setRecording(!timing.recording);
  e.currentTarget.blur();  // so Space doesn't re-activate the button
});

document.getElementById('btn-timing-save').addEventListener('click', e => {
  e.currentTarget.blur();
  saveTimingFile();
});

document.getElementById('btn-timing-export').addEventListener('click', e => {
  e.currentTarget.blur();
  exportStoredTimings();
});

document.getElementById('btn-timing-load').addEventListener('click', e => {
  e.currentTarget.blur();
  document.getElementById('timing-file-input').click();
});

document.getElementById('timing-file-input').addEventListener('change', async e => {
  const errors = [];
  for (const file of e.target.files) {
    try {
      const doc = parseTimingFile(await file.text());
      await loadTiming(timingDocMovement(doc));  // its lyrics come from its own timing file
      storeTiming(applyTimingDoc(doc, 'local'));
    } catch (err) {
      errors.push(`${file.name}: ${err.message}`);
    }
  }
  e.target.value = '';  // allow re-loading the same file
  if (errors.length) alert('Could not load lyrics timing:\n' + errors.join('\n'));
  refreshAfterTimingChange();
});

// Discard the timing recorded in this browser for a movement, going back to the timing in
// the file next to its audio, if it has any
function discardBrowserTiming(movement) {
  const key = movementKey(movement);
  delete timing.byKey[key];
  try { localStorage.removeItem(TIMING_STORAGE_KEY + key); } catch { /* storage unavailable */ }
  if (timing.files[key]) applyTimingDoc(timing.files[key], 'file');
}

document.getElementById('btn-timing-clear').addEventListener('click', e => {
  e.currentTarget.blur();
  const movement = currentMovement();
  if (!movement || !confirm(`Discard the timing recorded in this browser for "${movement.number}. ${movement.title}"?`)) return;
  discardBrowserTiming(movement);
  refreshAfterTimingChange();
});

document.getElementById('btn-timing-clear-all').addEventListener('click', e => {
  e.currentTarget.blur();
  const movements = storedTimingMovements();
  if (!movements.length) return;
  if (!confirm(`Discard the timing recorded in this browser for all ${movements.length} movement(s)?\n\n` +
               'Export them first to keep them.')) return;
  movements.forEach(discardBrowserTiming);
  refreshAfterTimingChange();
});

/* ================================================================
   AUDIO EVENTS
================================================================ */
// Manual mode leaves the highlight to the operator, but when the audio starts playing with
// no line highlighted, it highlights the line being played (as Auto mode would), once: from
// then on the operator moves it. Not while recording, where the first line is timed by the
// operator's first key press.
let pickLineOnPlay = false;

function pickLineBeingPlayed() {
  if (state.lastLyricIdx >= 0 || timing.recording || state.composerIdx === null) {
    pickLineOnPlay = false;  // a line is selected already, or the operator is timing them
    return;
  }
  if (!currentMovement()?.lyrics?.length) return;  // lyrics not loaded yet
  const idx = getCurrentLyricIdx();
  if (idx < 0) return;  // before the first timed line: try again as the audio goes on
  pickLineOnPlay = false;
  highlightLyricLine(idx);
}

audio.addEventListener('timeupdate', () => {
  if (audio.duration && isFinite(audio.duration)) {
    const ratio = audio.currentTime / audio.duration;
    document.getElementById('progress-bar').value = Math.round(ratio * 10000);
    setTimeDisplay(audio.currentTime, audio.duration);
  }

  if (state.composerIdx !== null && state.highlightMode === 'auto') {
    highlightLyricLine(getCurrentLyricIdx());
  } else if (pickLineOnPlay) {
    pickLineBeingPlayed();
  }
  updateSelectedLineTime();  // the elapsed time
  updateTimeInUrl();
});

audio.addEventListener('loadedmetadata', () => {
  setTimeDisplay(0, audio.duration);
  if (timeInUrl.start !== null) {
    audio.currentTime = Math.min(timeInUrl.start, audio.duration);
    timeInUrl.start = null;
  }
});

// The play / pause button shows what a click does: ❚❚ while playing, ▶ otherwise
function showPlaying(playing) {
  const icon = playing ? '&#9646;&#9646;' : '&#9654;';
  document.getElementById('btn-play-pause').innerHTML = icon;
  document.getElementById('btn-play-pause-max').innerHTML = icon;  // top bar, maximized lyrics mode
  state.isPlaying = playing;
}

audio.addEventListener('play', () => {
  showPlaying(true);
  pickLineOnPlay = true;
  document.getElementById('thumbnail-overlay').classList.add('hidden');
  updateTimingPanel();
});

document.getElementById('thumbnail-overlay').addEventListener('click', () => {
  if (audio.src) audio.play().catch(() => {});
});

audio.addEventListener('pause', () => {
  showPlaying(false);
  updateTimingPanel();
});

audio.addEventListener('ended', () => {
  // Auto-advance to next movement
  const idx = currentFlatIdx();
  if (idx >= 0 && idx < state.allMovements.length - 1) {
    const next = state.allMovements[idx + 1];
    loadMovement(next.composer, next.work, next.data, true);
  }
});

audio.addEventListener('error', () => {
  // Gracefully handle a missing or unplayable audio file — lyrics still display.
  // "Format error" on an MP3 that plays elsewhere usually means the HTTP server (see README)
  console.warn('Cannot play audio:', audio.src, audio.error?.message || `error code ${audio.error?.code}`);
});

/* ================================================================
   PLAYBACK CONTROLS
================================================================ */
['btn-play-pause', 'btn-play-pause-max'].forEach(id => {
  document.getElementById(id).addEventListener('click', e => {
    e.currentTarget.blur();  // so Space doesn't re-activate the button
    if (audio.src) {
      audio.paused ? audio.play().catch(() => {}) : audio.pause();
    }
  });
});

document.getElementById('btn-rewind-start').addEventListener('click', () => {
  audio.currentTime = 0;
  if (state.highlightMode === 'manual') highlightLyricLine(-1);
});

document.getElementById('btn-rewind-15').addEventListener('click', () => {
  audio.currentTime = Math.max(0, audio.currentTime - 15);
});

document.getElementById('btn-ff-15').addEventListener('click', () => {
  if (isFinite(audio.duration)) {
    audio.currentTime = Math.min(audio.duration, audio.currentTime + 15);
  }
});

document.getElementById('btn-ff-end').addEventListener('click', () => {
  if (isFinite(audio.duration)) audio.currentTime = audio.duration;
});

document.getElementById('progress-bar').addEventListener('input', e => {
  if (isFinite(audio.duration)) {
    audio.currentTime = (e.target.value / 10000) * audio.duration;
  }
});

document.getElementById('btn-prev').addEventListener('click', () => {
  const idx = currentFlatIdx();
  if (idx > 0) {
    const entry = state.allMovements[idx - 1];
    loadMovement(entry.composer, entry.work, entry.data, state.isPlaying);
  }
});

document.getElementById('btn-next').addEventListener('click', () => {
  const idx = currentFlatIdx();
  if (idx >= 0 && idx < state.allMovements.length - 1) {
    const entry = state.allMovements[idx + 1];
    loadMovement(entry.composer, entry.work, entry.data, state.isPlaying);
  }
});

/* ================================================================
   KEYBOARD SHORTCUTS
   Both modes:
     Space:            Play / Pause
     Esc:              Leave maximized lyrics panel
   Auto mode:
     Left/Right:       ±5 seconds
     Shift+Left/Right: ±15 seconds
   Manual mode:
     Down / Right:     highlight next lyric line (recorded while Rec is on)
     Up / Left:        highlight previous lyric line
================================================================ */
const MANUAL_KEYS = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 };

document.addEventListener('keydown', e => {
  const t = e.target;
  // Range inputs (progress bar) keep focus after dragging; don't let them swallow keys
  if (t.tagName === 'TEXTAREA' || (t.tagName === 'INPUT' && t.type !== 'range')) return;

  if (e.code === 'Escape') {
    setLyricsMaximized(false);
    return;
  }

  if (state.highlightMode === 'manual' && e.code in MANUAL_KEYS) {
    if (!e.metaKey && !e.ctrlKey && !e.altKey) {
      e.preventDefault();
      if (!e.repeat) stepLyricLine(MANUAL_KEYS[e.code]);  // holding a key advances one line only
    }
    return;
  }

  switch (e.code) {
    case 'Space':
      e.preventDefault();
      if (audio.src) audio.paused ? audio.play().catch(() => {}) : audio.pause();
      break;
    case 'ArrowLeft':
      e.preventDefault();
      audio.currentTime = Math.max(0, audio.currentTime - (e.shiftKey ? 15 : 5));
      break;
    case 'ArrowRight':
      e.preventDefault();
      if (isFinite(audio.duration))
        audio.currentTime = Math.min(audio.duration, audio.currentTime + (e.shiftKey ? 15 : 5));
      break;
  }
});

/* ================================================================
   HELPERS
================================================================ */
function currentWork() {
  if (state.composerIdx === null) return null;
  return APP_DATA.artists[state.composerIdx]?.works[state.workIdx] ?? null;
}

function currentMovement() {
  return currentWork()?.movements[state.movementIdx] ?? null;
}

function currentFlatIdx() {
  const m = currentMovement();
  if (!m) return -1;
  return state.allMovements.findIndex(e => e.data === m);
}

function updateNavButtons() {
  const idx = currentFlatIdx();
  document.getElementById('btn-prev').disabled = idx <= 0;
  document.getElementById('btn-next').disabled = idx < 0 || idx >= state.allMovements.length - 1;
}

function resetProgress() {
  document.getElementById('progress-bar').value = 0;
  setTimeDisplay(0, 0);
}

function setTimeDisplay(current, duration) {
  document.getElementById('time-display').textContent =
    `${fmt(current)} / ${fmt(duration)}`;
}

function fmt(s) {
  if (!isFinite(s) || isNaN(s)) return '0:00';
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, '0')}`;
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ================================================================
   INIT
================================================================ */
setHighlightMode(urlParam('highlight-mode') === 'manual' ? 'manual' : 'auto');
loadArtists().then(() => {
  buildFlatList();
  buildTree();
  updateNavButtons();
  updateTimingPanel();
  selectInitialMovement();
});
