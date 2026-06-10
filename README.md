# TGS Media Inbox Command, deploy folder

This folder is the website that Netlify serves. It is one file, `index.html`, the TGS Inbox Command dashboard. Connect it to Netlify through Git once, and from then on every push redeploys it automatically.

## One-time setup (about 5 minutes)

1. Create a new GitHub repository, private, named for example `tgs-inbox-command`. Do not add a README from GitHub, this folder already has one.

2. Push this folder to it. From this folder run:
   ```
   git init
   git add .
   git commit -m "Initial TGS Inbox Command dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/tgs-inbox-command.git
   git push -u origin main
   ```

3. In Netlify, click Add new site, then Import an existing project, then connect to GitHub and pick this repo. Leave the build command empty and the publish directory as `.` (the netlify.toml already sets this). Click Deploy.

4. Netlify gives you a URL like `tgs-inbox-command.netlify.app`. Open that from any device, including your laptop while you travel. Optional: set a custom domain such as inbox.tgsmedia.org in Netlify, Domain settings.

## How it refreshes

Each morning at 6:30am NZ the inbox task on your desktop rebuilds the dashboard data and commits the new `index.html` to this repo. Netlify sees the push and redeploys within about 30 seconds, so your laptop always shows the latest triage when you open the URL.

For that automatic morning commit to work, the task needs permission to push to the repo. Send Peter's setup contact (this assistant) the repo URL and a GitHub fine-grained personal access token with Contents read and write on this one repo, and the push step gets wired in. The token is stored only in this repo's local git config on your desktop, never in chat history or memory.

## Manual refresh, any time

If you ever want to force an update yourself, run from this folder:
```
git add index.html
git commit -m "Refresh dashboard"
git push
```
Netlify redeploys automatically.
