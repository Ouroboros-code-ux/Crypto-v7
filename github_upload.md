# How to Upload Your Code to GitHub

> [!IMPORTANT]
> **Why only the README is visible:** Currently, only your README file has been "tracked" and pushed. All your other project files (like `backend`, `index.html`) are "untracked," so Git hasn't uploaded them yet.

## 1. Move to the Correct Folder
Open your terminal and run this exact command:
```powershell
cd "c:\Users\shrey\OneDrive\Documents\Crypto-v7"
```

## 2. Add and Upload Your Files
Once you are in that folder, run these three commands one by one:

```bash
# 1. Add all untracked files to Git
git add .

# 2. Save the changes locally
git commit -m "Upload all project files"

# 3. Push the files to GitHub
git push origin main
```

```bash
# 1. Add all files to the staging area
git add .

# 2. Commit the changes with a message
git commit -m "Add project files and Render configuration"
```

## 2. Push to GitHub
Once committed, upload them to your repository:

```bash
# 3. Push the files to the main branch on GitHub
git push origin main
```

## 3. Verify on GitHub
1. Go to your repository link: [https://github.com/Ouroboros-code-ux/Crypto-v7](https://github.com/Ouroboros-code-ux/Crypto-v7)
2. Refresh the page. You should now see all your files (including the `backend` folder, `render.yaml`, etc.).

---

### Important Notes:
- **.gitignore**: I've verified your `.gitignore` file. It will automatically prevent sensitive files like `.env` and `.db` from being uploaded to GitHub.
- **Large Files**: You have a large video file (`bg3-video.mp4.mp4`). If your push fails due to file size, you may need to add it to `.gitignore` or use Git LFS.
- **Render Link**: Once the code is on GitHub, you can proceed with the Render deployment steps I provided earlier.
