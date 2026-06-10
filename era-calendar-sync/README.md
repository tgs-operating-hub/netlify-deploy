# Era Group calendar sync

Runs every 5 minutes. Pulls Tarang's and Amit's Outlook .ics feeds, expands recurring meetings, and mirrors their busy times into the Era Group GHL round-robin calendar so the SynthFlow agent only ever offers genuinely free slots.

## One-time setup (all in the browser, no command line)

1. **Create the repo.** github.com -> top-right **+** -> **New repository**. Name it `tgs-era-calendar-sync`. Set **Private**. Click **Create repository**.

2. **Upload the three files.** On the new empty repo page click **uploading an existing file**. Drag in `sync.py` and `requirements.txt`. Click **Commit changes**.

3. **Add the workflow file** (it lives in a folder, so create it by hand). Click **Add file -> Create new file**. In the name box type exactly:
   ```
   .github/workflows/sync.yml
   ```
   (typing the slashes creates the folders). Paste the contents of `sync.yml` from this package into the editor. Click **Commit changes**.

4. **Add the secret token.** Repo **Settings -> Secrets and variables -> Actions -> New repository secret**.
   - Name: `GHL_PIT`
   - Secret: paste the Era Group token from `05_GHL/41. Era Group GHL.txt` (the long value after `"JqaksLDzySXCTQPHXNi3":`, without the quotes).
   - Click **Add secret**.

5. **Turn Actions on and run it once.** Open the **Actions** tab. If prompted, click **I understand my workflows, enable them**. Click **Era ICS to GHL calendar sync** -> **Run workflow** -> **Run workflow**. After about a minute it should show a green tick.

That's it. From then on it runs itself every 5 minutes.

## Notes

- GitHub's scheduled runs are best-effort and can lag a few minutes under load. That is fine for this use; the manual-add email is the clash backstop.
- To change the look-ahead window, edit `SYNC_WINDOW_DAYS` in `.github/workflows/sync.yml` (default 30 days).
- If a run goes red, open it and read the log. The usual cause is a wrong or expired `GHL_PIT` secret.
