# CSV to Google Sheets Uploader - Complete Setup & Usage Guide

## Overview
This script automatically uploads large CSV files to Google Sheets, splitting them into multiple sheets if they exceed Google's 10 million cell limit per spreadsheet.

**Features:**
- Handles large CSV files (467K+ rows)
- Automatically splits data into multiple sheets
- Fast batch uploads (10K rows at a time)
- Cleans NaN values and special characters
- Generates a text file with all sheet URLs
- Uses your CSV filename for sheet titles
- **Auto-shares sheets with Edit access to anyone with the link** (no explicit permission needed)

---

## Prerequisites

### System Requirements
- Python 3.10+ (preferably 3.11 or higher)
- Linux/Mac/Windows with terminal access
- Internet connection
- Google account with Google Sheets access

### Required Python Libraries
```bash
pip install --break-system-packages google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas
```

Or install from requirements:
```bash
pip install --break-system-packages google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas
```

---

## Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project:
   - Click **"Select a Project"** at the top
   - Click **"NEW PROJECT"**
   - Enter project name (e.g., "CSV to Sheets")
   - Click **"CREATE"**

### Step 2: Enable APIs

1. In Google Cloud Console, search for **"Google Sheets API"**
2. Click on it and press **"ENABLE"**
3. Search for **"Google Drive API"**
4. Click on it and press **"ENABLE"**

### Step 3: Create OAuth Credentials

1. In Google Cloud Console, go to **"Credentials"** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. If prompted, click **"CONFIGURE CONSENT SCREEN"**:
   - Choose **"External"** for User Type
   - Fill in:
     - **App name:** "CSV to Sheets"
     - **User support email:** Your email
     - **Developer contact:** Your email
   - Click **"SAVE AND CONTINUE"**
   - Skip the optional scopes, click **"SAVE AND CONTINUE"**
   - Click **"BACK TO DASHBOARD"**

5. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"** again
6. For **Application type**, select **"Desktop application"**
7. Click **"CREATE"**
8. Click the **download icon** (⬇️) to download the JSON file
9. Rename the downloaded file to **`oauth_credentials.json`** and save it in your script directory

### Step 4: Prepare Your Script

1. Download `script.py` to your working directory
2. Place your CSV file in the **same directory** as the script
3. Update the `CSV_PATH` in the script:

```python
# Line 10 in script.py
CSV_PATH = "your_filename.csv"  # Replace with your actual CSV filename
```

---

## File Structure

Your working directory should look like:
```
csv_to_sheet/
├── script.py                              # The main script
├── oauth_credentials.json                 # Google OAuth credentials (created after first run)
├── token.json                             # Generated after authentication (auto-created)
├── your_filename.csv                      # Your CSV file
└── your_filename_sheet_urls.txt           # Generated URLs (created after upload)
```

---

## How to Use

### Step 1: First Time Run (Authentication)

1. Open terminal and navigate to your script directory:
```bash
cd ~/Desktop/csv_to_sheet
```

2. Run the script:
```bash
python3 script.py
```

3. A browser window will open asking for Google account permission
4. Click **"Allow"** to grant access to Google Sheets and Drive
5. The browser will show "The authentication flow has completed"
6. Close the browser and return to terminal

### Step 2: Script Execution

Once authenticated, the script will:

1. **Read CSV file** and calculate how many sheets are needed
2. **Create Google Sheets** with your filename + part number
   - Example: `my_data - Part 1`, `my_data - Part 2`, etc.
3. **Upload data in batches** (100K rows at a time for speed)
4. **Generate URLs text file** with links to all created sheets
5. **Print completion message** to terminal

### Step 3: Check Results

After the script completes:

1. **Check the URLs file:**
```bash
cat your_filename_sheet_urls.txt
```

Example output:
```
Part 1: https://docs.google.com/spreadsheets/d/1Gtqxa0R8af54dk...
Part 2: https://docs.google.com/spreadsheets/d/2FGHLmn0pqr5st...
```

2. **Click the links** to view your data in Google Sheets
3. Sheets are automatically organized with:
   - Header row at the top
   - Data rows below
   - Proper column widths

---

## Example Output

### Terminal Output:
```
CSV: 467843 rows × 25 columns
Max rows per Google Sheet: 380000
Total sheets needed: 2

Creating sheet 1/2: 380000 rows
Expanded grid to 380001 rows × 25 columns
Uploaded rows 0 → 99999
Uploaded rows 100000 → 199999
Uploaded rows 200000 → 299999
Uploaded rows 300000 → 379999

Creating sheet 2/2: 87843 rows
Expanded grid to 87844 rows × 25 columns
Uploaded rows 0 → 87843

✓ URLs saved to: 2026.01.27-1028_1stopbedrooms_Prisync_Vertical_Report_price_change_stock_1769498911735_sheet_urls.txt
```

### Generated URLs File (`your_filename_sheet_urls.txt`):
```
Part 1: https://docs.google.com/spreadsheets/d/1abc123def456ghi789
Part 2: https://docs.google.com/spreadsheets/d/2jkl234mno567pqr890
```

---

## Script Configuration

### CSV_PATH (Line 10)
```python
CSV_PATH = "your_filename.csv"
```
- Change this to your actual CSV filename
- Must be in the same directory as the script

### Batch Size (Optional Tuning)
```python
# In upload_chunk function - Line 78
def upload_chunk(sheets_service, spreadsheet_id, df_chunk, batch_size=10000):
```
- **100,000** = Default (fast)
- **50,000** = If you encounter timeout errors
- **200,000** = If you want ultra-fast upload (but uses more memory)

### Max Cells Per Sheet (Advanced)
```python
# In process_csv function - Line 118
max_cells_per_sheet = 9_500_000
```
- Google's hard limit is 10,000,000 cells
- 9,500,000 is safe (leaves buffer)
- Don't change unless you know what you're doing

---

## Troubleshooting

### Issue: "oauth_credentials.json not found"
**Solution:** Make sure you downloaded the OAuth credentials file and placed it in the correct directory with the exact filename.

### Issue: "Range exceeds grid limits"
**Solution:** This is already fixed in the script. The `expand_sheet_grid()` function automatically expands sheet size before uploading.

### Issue: "Invalid JSON payload received"
**Solution:** The script now handles NaN values and special characters automatically. If you still get this error:
- Make sure you're using the latest version of the script
- Check that your CSV file isn't corrupted

### Issue: "Timeout error" or "Connection error"
**Solution:** 
1. Reduce batch size to 5,000:
```python
def upload_chunk(sheets_service, spreadsheet_id, df_chunk, batch_size=5000):
```
2. Try running the script again - it's often a temporary network issue

### Issue: "Rate limit exceeded"
**Solution:** Google has API rate limits. Wait 1-2 minutes and run the script again. The script will continue from where it left off.

### Issue: "Permission denied" or "Access denied"
**Solution:**
1. Delete `token.json` from your directory
2. Run the script again and re-authenticate
3. Make sure you click "Allow" when prompted

---

## Performance Notes

### Upload Speed
- **Fast:** ~10K rows per minute (typical internet speed)
- **Factors affecting speed:**
  - Internet connection quality
  - CSV file size and complexity
  - Your Google account rate limits
  - Number of columns

### File Size Limits
- **CSV file size:** No hard limit (limited only by your disk)
- **Google Sheets per sheet:** 10 million cells
- **Google Drive storage:** Depends on your account (usually 15GB free)

### For Your Data:
- **467,843 rows × 25 columns** = ~11.7M cells
- **Automatically splits into:** 2 sheets
- **Expected upload time:** 10-20 minutes

---

## Sharing & Permissions

### Auto-Sharing
When the script creates each Google Sheet, it **automatically sets edit permissions to anyone with the link**. This means:

✅ **Anyone with the link can:**
- View the spreadsheet
- Edit the data
- Add comments
- Make changes in real-time

✅ **No need to:**
- Manually change sharing settings
- Grant permissions to individual users
- Set up complex access controls

### How It Works
The script uses Google Drive API to automatically apply this permission:
```python
drive_service.permissions().create(
    fileId=spreadsheet_id,
    body={
        "type": "anyone",
        "role": "writer"
    }
)
```

### Change Sharing Settings (Optional)
If you want to change permissions **after** the script runs:

1. Open the Google Sheet
2. Click **"Share"** (top right)
3. Modify permissions:
   - **"Viewer"** = Read-only access
   - **"Commenter"** = Can add comments
   - **"Editor"** = Full edit access
   - **"Restricted"** = Only specific people

---

## Advanced: Re-running the Script

### To upload the same CSV again:
```bash
python3 script.py
```
- Creates NEW sheets (doesn't overwrite)
- Generates a NEW URLs file with timestamp option

### To modify the script for a different CSV:
1. Update the `CSV_PATH` variable
2. Run the script as normal

### To use a different Google account:
1. Delete `token.json`:
```bash
rm token.json
```
2. Run the script - it will ask for authentication again

---

## Security Notes

- **oauth_credentials.json** contains your credentials - keep it private
- **token.json** is created after authentication - also keep private
- Never commit these files to public repositories
- If credentials are exposed, regenerate them in Google Cloud Console

---

## Support & Debugging

### Enable Debug Mode (for troubleshooting):
Add this at the top of the script to see more detailed error messages:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Get the full error traceback:
Run the script with Python's verbose flag:
```bash
python3 -v script.py
```

### Check your API quota:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "Quotas & System Limits"
3. Check "Sheets API" usage

---

## FAQ

**Q: Can I upload multiple CSVs at once?**
A: Currently, the script handles one CSV at a time. Run it separately for each file.

**Q: Will it overwrite existing sheets?**
A: No. Each run creates new sheets with unique IDs.

**Q: How can I download the data back as CSV?**
A: Open each Google Sheet → File → Download → CSV (.csv)

**Q: Can I edit the data in Google Sheets after upload?**
A: Yes! The sheets are fully editable. Make any changes you want.

**Q: What if the upload gets interrupted?**
A: You'll need to re-run the script. It will create new sheets (doesn't resume from the middle).

**Q: Is there a file size limit?**
A: Your CSV can be as large as your disk allows. Google Sheets limits are per-sheet (10M cells).

**Q: Can I schedule this script to run automatically?**
A: Yes, use Linux cron jobs or Windows Task Scheduler. (Advanced topic)

---

## Contact & Updates

- Keep your Google API libraries updated:
```bash
pip install --break-system-packages --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

- Check for Python updates:
```bash
python3 --version
```

---

**You're all set! Happy uploading!** 🚀
