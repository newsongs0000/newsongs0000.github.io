# Fix GitHub Pages deployment error

## Ask

how to fix the deployment error? https://github.com/songswords99/songswords99.github.io/actions/runs/44983217355

## Answer

### Diagnosis

Run 44983217355 (`pages-build-deployment`, commit `36b1ed5`) built fine, but the **deploy** job failed:

```
Error: Failed to create deployment (status: 400) with build version 36b1ed5...
Deployment request failed for 36b1ed5... due to in progress deployment.
Please cancel 3112aa7... first or wait for it to complete.
```

This was a race on GitHub's side, not a problem in the repo. Commits `3112aa7` and `36b1ed5` were
pushed about 12 minutes apart. When `36b1ed5`'s deploy started, GitHub Pages still treated `3112aa7`'s
deployment as in progress, so it rejected the new one. `3112aa7`'s deployment later finished
successfully, and the site served that commit until the fix below.

### Fix applied

1. `gh run rerun 44983217355 --failed` re-ran the failed job. The re-run stayed in "queued" with no
   jobs and never started. Re-runs of the automatic `pages-build-deployment` workflow are often unreliable.
2. `gh api -X POST repos/songswords99/songswords99.github.io/pages/builds` requested a fresh Pages build.
   This started run 44990409487 for `36b1ed5`; build, deploy and report-build-status all succeeded.
   The Pages status is now `built` for `36b1ed5`.

### Notes

- The stuck re-run 44983217355 still shows as "queued" (GitHub refuses to cancel it because it is
  "completed"). It is harmless: if it ever runs, it deploys the same commit again.
- The "Node.js 20 is deprecated" warning comes from GitHub's built-in Pages workflow
  (`actions/upload-artifact@v4`), not from this repo. There is nothing to change here.
- If this happens again: request a new build with the API call above, or push an empty commit
  (`git commit --allow-empty -m "Trigger Pages rebuild" && git push`). To avoid it, wait about
  2 minutes between pushes, or push several commits at once.
