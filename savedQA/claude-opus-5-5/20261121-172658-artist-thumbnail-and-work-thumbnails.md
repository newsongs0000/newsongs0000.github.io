# Artist thumbnail, and new work thumbnails

## Ask

Copy the current thumbnail in work.js to the corresponding artist.js, display it when an artist is selected; find
appropriate thumbnail for work

## Answer

### Artist thumbnails

The composer portraits that were the works' thumbnails are now the artists' thumbnails, moved (`git mv`) from each
work folder to its artist folder, since no work uses them any more:

| Artist | `thumbnail` in artist.js | Moved from |
|---|---|---|
| Handel | `assets/Handel/Handel.jpg` | `assets/Handel/Messiah/Handel.jpg` |
| Mozart | `assets/Mozart/Mozart.jpg` | `assets/Mozart/Requiem/Mozart.jpg` |
| Huang, An-Lun | `assets/HuangAnlun/HuangAnlun.jpg` (artist.js already named it; the file was missing there) | `assets/HuangAnlun/ChineseRequiem/HuangAnlun.jpg` |

An artist's `thumbnail` is relative to its artist.js (`resolveArtistPaths` in app.js).

### Selecting an artist (app.js, SELECT ARTIST)

Opening an artist in the tree now selects it, as opening a work does (unless music is playing):

- the artist's thumbnail covers the lyrics area with "▶ Click to play" (else its first work's thumbnail);
- the header shows the artist's name, the info pane its name and `bio`;
- the artist's header is highlighted in the tree (`.tree-composer-header.active` in common.css);
- ▶, Space or a click on the picture plays the first movement of the artist's first work; Next selects that
  movement and Prev the one before it (data order);
- the selection is kept in the URL as `?artist=<artist id>`, and restored on load;
- closing an artist folder changes nothing.

### New work thumbnails (`work.jpg` in each work folder)

All public domain, from Wikimedia Commons, 1280 px wide, credited in the work's `backgrounds.md`:

| Work | Picture |
|---|---|
| Messiah | Handel's autograph: the beginning of the Hallelujah chorus (1741) |
| 弥赛亚 (Chinese) | Handel's autograph: the end of the Hallelujah chorus, dated 6 September 1741 |
| Mozart Requiem | the first page of Mozart's autograph score |
| 安魂曲 (Chinese Requiem) | the head of the Nestorian Stele 大秦景教流行中國碑 (Xi'an, 781): Christian art made in China, like image set 1 |

### Also updated

README.md (tree, picture, info pane, `artist` URL parameter, data files, project structure) and the app.js comments.

### Verified

In headless Chrome, served over HTTP: `?artist=` for each artist and `?work=` for each work show the right picture,
info and highlight; opening/closing artist folders, Next/Prev from an artist, clicking the picture to play, opening an
artist while playing, and the Show check boxes with an artist selected all behave as above, with no console errors.

---

## Ask

please add (captions for the artist and work thumbnails, offered at the end of the previous answer)

## Answer

New optional fields `thumbnailTitle` and `thumbnailPainter` (in artist.js for an artist, in work.js for a work or a
movement) give a thumbnail a caption above "▶ Click to play", like `backgroundTitle` and `backgroundPainter` do for
a movement's background. `pictureCaptionFor` in app.js (PICTURE CAPTION) now looks up the picture shown in the
selected movement's background2, background and thumbnail, then its work's thumbnail, then its artist's, so a work's
thumbnail keeps its caption when a movement without a picture of its own shows it.

| Selection | Caption |
|---|---|
| Handel | *George Frideric Handel* by Thomas Hudson |
| Mozart | *Wolfgang Amadeus Mozart* by Barbara Krafft |
| Huang, An-Lun | *An-lun Huang 黄安伦: Piano Music (Toccata Classics album cover)* |
| Messiah | *Hallelujah, autograph score (1741)* by George Frideric Handel |
| 弥赛亚 | *Hallelujah, autograph score, final bars (6 September 1741)* by George Frideric Handel |
| Mozart Requiem | *Requiem, autograph score, first page (1791)* by Wolfgang Amadeus Mozart |
| 安魂曲 | *大秦景教流行中國碑 The Nestorian Stele (781)* (no painter) |

README.md (Caption, the artist.js and work.js examples, the data files table) is updated. Checked in headless
Chrome for every artist and work, and that movement background captions still show (in None and Image modes).
