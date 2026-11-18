# Select the first movement on page load

## Ask

When the app page is loaded, select the first artist's first song's first movement

## Answer

In `app.js`:

- The tree's alphabetical sorting moved into two helpers, `sortedArtists()` and
  `sortedWorks(composer)`. `buildTree()` uses them, so "first" means the first one
  shown in the tree.
- New `selectFirstMovement()`, called at the end of init after the tree is built:
  - It loads the first movement of the first artist's first work, skipping any
    artist or work that has no movements.
  - It does not autoplay.
  - It opens that artist's and work's folders so the active movement is visible.

Verified in headless Chrome (file://). On load, "An-Lun Huang 黄安伦 › 安魂曲 › I. 永远安息"
is active, its artist and work folders are open, and the top bar and lyrics show it.
Prev is disabled and Next is enabled.
