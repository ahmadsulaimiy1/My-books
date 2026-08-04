# Deployment Guide

How this site actually gets from a commit to the live URL, and the git workflow that keeps it reliable.

## Hosting

**Vercel**, deploying from GitHub (`ahmadsulaimiy1/My-books`), framework preset **Next.js**, project name `al-balagh-digital-campus`. The app lives at the **repo root** — this matters: an earlier attempt to keep the app in a subdirectory (`albalagh-nextjs/`) failed because this Vercel project's Root Directory setting couldn't be changed through the dashboard on this account/plan, so the app was moved to the repo root instead of fighting that setting. Don't reintroduce a subdirectory layout without first confirming Root Directory is actually configurable on the current plan.

Every push to a branch gets its own preview deployment automatically. **`main` is production** — pushing to `main` (or merging into it) triggers a production deploy to the live domain.

## Branching model used throughout this project

- **`main`** — production. Every commit here is live.
- **A feature branch** (e.g. `claude/my-books-vercel-deploy-89ydtp`) — where day-to-day work happens.

The established, safe cycle for shipping a change:

```bash
# 1. Work on the feature branch, verify locally
git checkout <feature-branch>
# ... make changes ...
npx next build   # must pass with zero errors before committing
npx next lint    # must pass with zero errors (one pre-existing warning is expected, see below)
grep -rn "Al-Balagh" --exclude-dir=.git --exclude-dir=node_modules .   # must return nothing
git add <files>
git commit -m "..."
git push -u origin <feature-branch>

# 2. Merge into main to deploy
git checkout main
git pull origin main
git merge --no-ff --no-edit <feature-branch>
git push origin main
git checkout <feature-branch>   # return to the working branch, don't stay on main
```

**Always `--no-ff` merge, never rebase `main`, never force-push `main`.** If a push to the feature branch is rejected because the remote moved (e.g. two people/agents pushed concurrently), `git pull --rebase origin <feature-branch>` first and resolve keeping both sides' changes — never discard either side without understanding what it was.

**Never commit directly on `main`.** If you catch yourself having done so (it's happened during this project — checked with `git branch --show-current` and caught before pushing), don't push it: `git reset --soft origin/main`, stash, checkout the feature branch, pop the stash, commit there instead.

## The pre-commit checklist (applied to every single commit in this project's history)

1. `npx next build` — zero errors. This is non-negotiable; a broken build should never reach `main`.
2. `npx next lint` — zero errors. The one expected, pre-existing, deliberately-not-fixed warning is `no-page-custom-font` in `src/app/layout.jsx` (fixing it means migrating four font families to `next/font`, judged too large/risky a change for the value it adds — see `RELEASE_REPORT.md`).
3. `grep -rn "Al-Balagh" --exclude-dir=.git --exclude-dir=node_modules .` — must return nothing. The institution was renamed from "Al-Balagh International Premium College" to "Albalagh Global" mid-project; this grep is the trip-wire against the old name resurfacing.
4. Tag balance on any HTML file touched (the 19 legacy pages have no build step to catch a malformed tag — verify manually, e.g. with a quick Python `HTMLParser` stack check, or by re-reading the diff carefully).
5. If a `data-i18n` key changed on a legacy page, confirm **both** `en` and `ar` entries were updated — a change to only one language is a real, shipped bug, not a draft.

## Verifying a deploy actually went live

After pushing to `main`, the Vercel deployment can be checked via the Vercel MCP tools (`list_deployments`, `get_deployment` — poll `readyState` until `READY`), or by fetching the live URL directly and checking for the expected content (`web_fetch_vercel_url` handles Vercel's deployment-protection layer if a raw fetch gets blocked). Production URL: `https://al-balagh-digital-campus.vercel.app` (and the project's configured custom domain, if any).

## Environment variables

None are currently required — the site has no backend yet. When Firebase integration begins (`FIREBASE_INTEGRATION_GUIDE.md`), the Firebase web config values go into Vercel's Environment Variables (Project Settings → Environment Variables), prefixed `NEXT_PUBLIC_` for anything the client bundle needs to read (the config itself is safe to expose; see the integration guide's note on why). Never commit a real Firebase config, API key, or credential to the repository, even though the config values themselves aren't secret by Firebase's own design — keep them in Vercel's environment settings so rotation doesn't require a code change.

## Rollback

Vercel keeps every deployment; the dashboard (or `list_deployments` via MCP, looking for `isRollbackCandidate: true` entries) shows prior production deployments that can be promoted back to production directly, without needing a git revert first. A git revert is still the right move if the underlying commit is wrong and shouldn't stay in history — use Vercel's instant rollback only as an emergency stop-gap while you prepare the real fix.
