# Deploying Crypto-v7 to Render

Follow these steps to deploy your project using GitHub and Render.

## 1. Prepare your GitHub Repository
> [!IMPORTANT]
> Ensure your terminal is in `c:\Users\shrey\OneDrive\Documents\Crypto-v7` before running these commands.

1. Go to [GitHub](https://github.com) and create a new repository (e.g., `CryptoShield-AI`).
2. In your local terminal, run the following commands:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

## 2. Deploy to Render
1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub account and select the repository you just pushed.
4. Render will automatically detect the `render.yaml` file.
5. Review the service details and click **Apply**.

## 3. Configuration (Environment Variables)
After the initial deployment starts, you'll need to add your API keys:
1. Go to your **Web Service** settings in Render.
2. Select **Environment**.
3. Add the following keys (if not already prompted):
   - `GEMINI_API_KEY`: Your Google AI API key.
   - `ETHERSCAN_API_KEY`: Your Etherscan API key.
   - `SMTP_USER`: Your email for notifications.
   - `SMTP_PASSWORD`: Your email app password.
4. Click **Save Changes**. Render will automatically redeploy.

## 4. Database Warning
> [!WARNING]
> This project currently uses SQLite. Each time Render restarts or redeploys, your database will be reset to its initial state.
> - For persistent data, consider using **Render PostgreSQL** (paid) or attaching a **Persistent Disk** to this web service.
