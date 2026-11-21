# Swap ChapterN-bg.jpg and ChapterN-bg2.jpg (安魂曲)

## Ask

Swap the file name of Chapter1-bg.jp and Chapter1-bg2.jp under assets/HuangAnlun/ChineseRequiem and other similar
files under assets/HuangAnlun/ChineseRequiem

## Answer

Swapped the names of all 8 pairs in `assets/HuangAnlun/ChineseRequiem/` (Chapter1..8), using a temporary name for
each pair. Checksums confirmed each swap:

- `ChapterN-bg.jpg` is now the Christian painting (Xu Jihua, Giulio Aleni's woodcuts, the Khocho mural). These were
  the old `-bg2.jpg` files.
- `ChapterN-bg2.jpg` is now the Chinese landscape painting (Song–Yuan). These were the old `-bg.jpg` files.

`work.js` still uses `background` for version 1 and `background2` for version 2. So the Christian paintings are now
the default (Pictures 1) and the landscapes are Pictures 2. These docs name the files, so I updated them to match:

- `backgrounds.md`: Version 1 is now "Christian paintings" and Version 2 "Chinese landscape paintings". Each credit
  row moved with its picture, so the licenses still match the files.
- `work.js`: the `pictureVersions` tooltips are swapped: `1: 基督教绘画 Christian paintings`, `2: 中国山水画 Chinese
  landscape paintings`.
- `README.md`: updated the Picture versions bullet, the `pictureVersions` example, the asset tree (`-bg.jpg` /
  `-bg2.jpg`) and the example painting in the Image paragraph. Auspicious Cranes is now a version 2 picture, so the
  example is now Xu Jihua's *The Wedding at Cana* for 诗篇二十三.

Not changed: the `local/ChapterN-bg2.jpg` override (He Qi's copyrighted paintings) is still on `background2`.
So on a computer that has those files, He Qi's paintings would replace the Chinese landscapes, not the Christian
set. To keep He Qi as the alternative to the Christian pictures, the override would move to
`background: ["local/ChapterN-bg.jpg", "ChapterN-bg.jpg"]`, with the local files renamed to match.

## Ask

Remove anything related to He Qi

## Answer

Removed every He Qi reference outside `savedQA` and `HumanReadOnly`:

- `assets/HuangAnlun/ChineseRequiem/work.js`: each `background2` is now just `"ChapterN-bg2.jpg"`. The
  `local/ChapterN-bg2.jpg` entry and its "He Qi's painting…" comment are gone from all 8 movements.
- `assets/HuangAnlun/ChineseRequiem/SOURCES.md` (untracked, it listed only He Qi's paintings and licensing):
  deleted.
- `assets/HuangAnlun/ChineseRequiem/backgrounds.md`: removed the paragraph about `local/` He Qi paintings.
- `README.md`: removed the He Qi sentence from "Pictures on this computer only", the `local/` line in the asset
  tree, and the `local/` entry in the `work.js` example (it is now a single file, with a note that a list also works).
- `.gitignore`: the `assets/**/local/` comment now points to the README instead of `local/SOURCES.md`.

Kept: the general feature in `app.js` (a `background` / `background2` may be a list of files, tried in order) and
the `assets/**/local/` ignore rule. Neither names He Qi, and no work uses a `local/` folder now.

## Ask

The two terms image and picture are used here in lines 90 and 94 (index.html), is it confusing?

## Answer

Yes, a little. The rows read "Background: None | Graphics | Image" and "Pictures: 1 | 2". Both words mean the
movement's background picture, but the different word suggests the second row controls something else (such as the
thumbnail, which the README also calls "pictures"). The Pictures row only appears in Image mode, right below the
Image button, so the harm is small, but one word is clearer. Suggested renaming the second row to "Image set: 1 | 2"
and leaving internal names (`pictures` URL parameter, `data-pictures`, `pictureVersions`) alone, since users don't
see them and renaming the URL parameter would break saved links.

## Ask

yes

## Answer

Renamed the "Pictures" row to "Image set" everywhere users or readers see it:

- `index.html`, `index1.html`: label "Image set:", `aria-label="Image set"`.
- `app.js`: the fallback button tooltip is now "Image set 1" / "Image set 2" (shown when a work has no
  `pictureVersions`), and the comments say "the Image set buttons".
- `README.md`: the View Options row is **Image set: 1 | 2**. The **Picture versions** bullet is now **Image sets**,
  and the `pictures` URL parameter row links to it. Also updated the `pictureVersions` comment, the `background2`
  example and the asset tree ("set 1" / "set 2").
- `assets/HuangAnlun/ChineseRequiem/backgrounds.md`: headings "Image set 1: Christian paintings" and
  "Image set 2: Chinese landscape paintings", with the text to match.
- `assets/HuangAnlun/ChineseRequiem/work.js`: the comment above `pictureVersions`.

Unchanged: the `pictures` URL parameter, `id="pictures-toggle"`, `data-pictures`, `pictureVersions`, and the
PICTURE VERSIONS section name in `app.js` comments. The "Pictures on this computer only" README bullet is also
unchanged, because it is about picture files, not the buttons. `common.css` gives the label no fixed width, so
the longer label fits.

## Ask

commit the changes

## Answer

Created branch `chinese-requiem-image-sets` from `main` and committed everything there in one commit. That
includes the uncommitted image-set work from the earlier session (`background2`, the 1 | 2 buttons, the `local/`
fallback), because it shares files with this session's edits. Not pushed; `main` is unchanged. To put it on `main`:
`git switch main && git merge --ff-only chinese-requiem-image-sets`.
