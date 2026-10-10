# Setup (delete this file after you push)

## 1. Push

Create a **public** repo named exactly `vivekboyina` (no README/.gitignore), then:

```bash
cd vivekboyina
git init -b main
git add .
git commit -m "feat: profile README"
git remote add origin https://github.com/vivekboyina/vivekboyina.git
git push -u origin main
```

## 2. Allow Actions to write

Repo → Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.

## 3. Run the workflows once

Actions tab → run **Generate Snake**, **Update Coding Stats** and **Nightly Contribution** manually (Run workflow). The snake image appears after the first Snake run creates the `output` branch.

## 4. Make nightly commits count

Commits only show on your graph if the author email belongs to your account.
`vivekboyina77@gmail.com` must be added and verified at GitHub → Settings → Emails. If it is not, set a repo variable `COMMIT_EMAIL` (Settings → Secrets and variables → Actions → Variables) to your `ID+vivekboyina@users.noreply.github.com` address.

Optional: add a classic PAT as secret `PROFILE_TOKEN` if the contribution check ever fails with a permissions error.

## 5. Check these links

- X handle is set to `https://x.com/vivekboyina`; change it in README.md if different.
- Student Management System repo link is `.../Student-Management-System`; fix the name if your repo differs.

## How the automation behaves

- **Coding stats**: every 30 min, pulls LeetCode, Codeforces and CodeChef numbers and edits only the block between the `CODING_START/END` markers. HackerRank and GeeksforGeeks have no public API, so they show fixed badges. Platforms don't notify GitHub when you submit, so updates are polled, not instant.
- **Nightly contribution**: at 23:00 IST (backup 23:30) it counts today's contributions and commits to `.activity/log.md` only if the count is zero.
