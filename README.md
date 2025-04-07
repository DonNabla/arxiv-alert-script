# 🧪 arXiv Daily Alert Script

This Python script checks the arXiv preprint server daily for new papers matching specific physics-related keywords, such as:

- Dark matter direct detection
- Neutrinoless double beta decay
- Neutrino physics
- Double weak decay

It filters papers by date and content, sends a summary via email, and avoids duplicates using a local record of seen entries.

---

## 🚀 Features

- ✅ Queries arXiv categories (`hep-ex`, `hep-ph`, `nucl-ex`)
- ✅ Filters papers from the **last 24 hours**
- ✅ Matches relevant papers by **keywords in title/abstract**
- ✅ Excludes papers by **undesired keywords or categories**
- ✅ Sends a daily summary email with title, abstract, and links
- ✅ Keeps track of already-sent papers using a local file

---

## ⚙️ Setup

### 1. Clone the repo and install dependencies

Use a Conda environment (recommended):

```bash
conda create -n arxiv-alert python=3.10
conda activate arxiv-alert
pip install feedparser python-dotenv python-dateutil
```

### 2. Clone the repo and install dependencies

Create a .env file in the same folder as the script:

```bash
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
TO_EMAIL=recipient_email@example.com
```
⚠️ For Gmail, you’ll need to generate an App Password and enable 2FA.

### 3. Run it manually (for testing)

```bash
python arxiv_alert.py
```
### 4. Schedule it as a daily cron job


To run every day at 9:00 AM:

```bash
crontab -e
```
Then add this line (adjust the paths for your machine):

```bash
0 9 * * * /opt/anaconda3/envs/arxiv-alert/bin/python /Users/youruser/Code/arxiv_alert/arxiv_alert.py >> /Users/youruser/Code/arxiv_alert/cron.log 2>&1
```

Check cron logs here:

```bash
cat /Users/youruser/Code/arxiv_alert/cron.log
```

### 🔍 Configuration

You can adjust filters directly in the script (arxiv_alert.py):

## ✅ Keywords to include:
```python
KEYWORDS = ["dark matter", "direct detection", "neutrino", "experiment"]
```
## ❌ Keywords to exclude:
```python
EXCLUDED_KEYWORDS = ["supernova", "sterile neutrino"]
```
## ❌ Categories to exclude (optional):
```python
CATEGORIES_EXCLUDED = ["astro-ph.CO", "astro-ph.GA"]
```

### 🧠 Credits
Created by Maxime (and ChatGPT 😄). Inspired by the need to stay current without refreshing arXiv all day, and offering more filtering option.
