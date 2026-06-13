# Git and GitHub Command Notes

This guide covers the Git commands needed to manage and publish this project.
Run these commands from the repository root:

```bash
cd ~/Documents/projects/audio-voice
```

## Git Concepts

- **Working tree:** files currently on your computer
- **Staging area:** changes selected for the next commit
- **Commit:** a saved snapshot with a message
- **Branch:** a line of development, such as `main`
- **Remote:** a hosted copy of the repository, such as GitHub
- **Push:** upload local commits to a remote
- **Pull:** download and integrate remote commits

## One-Time Setup

Set the name and email attached to your commits:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

View the current configuration:

```bash
git config --list
```

## Create and Connect a Repository

Initialize Git in a project:

```bash
git init
git branch -M main
```

Connect it to GitHub:

```bash
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git remote -v
```

If `origin` already exists, update it instead:

```bash
git remote set-url origin https://github.com/USERNAME/REPOSITORY.git
```

## Everyday Workflow

Check what changed:

```bash
git status
git diff
```

Stage all intended changes:

```bash
git add .
```

Review staged changes:

```bash
git diff --staged
```

Create a commit:

```bash
git commit -m "Describe the change clearly"
```

Push commits to GitHub:

```bash
git push
```

For the first push of a new branch:

```bash
git push -u origin main
```

The complete normal workflow is:

```bash
git status
git add .
git diff --staged
git commit -m "Explain what changed"
git push
```

## Download Remote Changes

Inspect remote changes without modifying your branch:

```bash
git fetch origin
git log --oneline main..origin/main
```

Download and integrate the latest `main` branch:

```bash
git pull --rebase origin main
```

Use `pull --rebase` before pushing when another machine or contributor may have
already pushed changes.

## Branches

List branches:

```bash
git branch
git branch -a
```

Create and switch to a feature branch:

```bash
git switch -c feature/short-description
```

Switch branches:

```bash
git switch main
```

Merge a completed feature into `main`:

```bash
git switch main
git pull --rebase origin main
git merge feature/short-description
git push
```

Delete the local feature branch after merging:

```bash
git branch -d feature/short-description
```

## Review History

```bash
git log --oneline --decorate --graph --all
git show COMMIT_ID
git diff COMMIT_ID_1 COMMIT_ID_2
```

## Correct Common Mistakes

Unstage a file while keeping its changes:

```bash
git restore --staged path/to/file
```

Discard uncommitted changes in one file:

```bash
git restore path/to/file
```

Add forgotten changes to the latest local commit:

```bash
git add path/to/file
git commit --amend --no-edit
```

Create a new commit that safely reverses an older commit:

```bash
git revert COMMIT_ID
```

Avoid `git reset --hard` unless you fully understand that it permanently
discards local work.

## Authentication

GitHub does not accept account passwords for HTTPS Git operations. Use one of:

- A GitHub Personal Access Token when prompted for an HTTPS password
- GitHub CLI authentication with `gh auth login`
- An SSH key and an SSH remote URL

Never commit tokens, passwords, `.env` files, private keys, virtual
environments, or downloaded models.

## Common Errors

### `src refspec main does not match any`

The repository has no commit yet. Create one before pushing:

```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

### `remote origin already exists`

Do not add it again. Inspect or update it:

```bash
git remote -v
git remote set-url origin NEW_URL
```

### Push rejected because the remote contains work

Integrate the remote commits, then push again:

```bash
git pull --rebase origin main
git push
```

### Accidentally staged a secret

Unstage it, add it to `.gitignore`, and confirm it is no longer staged:

```bash
git restore --staged path/to/secret
git status
```

If a secret was already pushed, revoke or rotate it immediately. Removing it
from a later commit does not remove it from Git history.
