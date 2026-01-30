import pandas as pd
import math
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ============== CONFIG =================
CSV_PATH = "2026.01.27-1028_1stopbedrooms_Prisync_Vertical_Report_price_change_stock_1769498911735.csv"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
# ======================================


def authenticate():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "oauth_credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    return sheets_service, drive_service


def create_spreadsheet(sheets_service, drive_service, title):
    spreadsheet = sheets_service.spreadsheets().create(
        body={"properties": {"title": title}},
        fields="spreadsheetId"
    ).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    
    # Share with edit permissions to anyone with link
    try:
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={
                "kind": "drive#permission",
                "type": "anyone",
                "role": "writer"
            },
            fields="id"
        ).execute()
        print(f"✓ Shared with edit access to anyone with link")
    except Exception as e:
        print(f"⚠ Warning: Could not set sharing permissions: {e}")
    
    return spreadsheet_id


def expand_sheet_grid(sheets_service, spreadsheet_id, num_rows, num_cols):
    """Expand the sheet grid to accommodate the data"""
    request = {
        "updateSheetProperties": {
            "properties": {
                "sheetId": 0,  # Sheet1 has ID 0
                "gridProperties": {
                    "rowCount": num_rows + 1,  # +1 for header
                    "columnCount": num_cols
                }
            },
            "fields": "gridProperties"
        }
    }
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()
    
    print(f"Expanded grid to {num_rows + 1} rows × {num_cols} columns")


def upload_chunk(sheets_service, spreadsheet_id, df_chunk, batch_size=100000):
    # Expand grid to fit all data
    num_rows = len(df_chunk)
    num_cols = len(df_chunk.columns)
    expand_sheet_grid(sheets_service, spreadsheet_id, num_rows, num_cols)
    
    # Clean data: convert NaN to empty string and handle types
    def clean_value(val):
        if pd.isna(val):
            return ""
        return str(val)
    
    # Combine header + all data into one list with cleaned values
    header = [df_chunk.columns.tolist()]
    data_rows = [[clean_value(val) for val in row] for row in df_chunk.values]
    all_values = header + data_rows
    
    # Write all data in batches (100K rows per batch for speed)
    total_rows = len(all_values)
    
    for i in range(0, total_rows, batch_size):
        batch = all_values[i:i + batch_size]
        start_row = i + 1
        range_name = f"Sheet1!A{start_row}"
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": batch}
        ).execute()
        
        end_row = min(i + batch_size, total_rows)
        print(f"Uploaded rows {i} → {end_row - 1}")



def process_csv():
    sheets_service, drive_service = authenticate()
    df = pd.read_csv(CSV_PATH, low_memory=False)

    total_rows, total_cols = df.shape
    
    # Google Sheets limit: 10 million cells per spreadsheet
    # We use 9.5M to be safe (includes header row)
    max_cells_per_sheet = 9_500_000
    max_rows_per_sheet = max_cells_per_sheet // total_cols - 1  # -1 for header

    print(f"CSV: {total_rows} rows × {total_cols} columns")
    print(f"Max rows per Google Sheet: {max_rows_per_sheet}")

    total_files = math.ceil(total_rows / max_rows_per_sheet)
    print(f"Total sheets needed: {total_files}")
    urls = []
    
    # Extract filename without extension
    base_filename = os.path.splitext(os.path.basename(CSV_PATH))[0]

    for i in range(total_files):
        start = i * max_rows_per_sheet
        end = start + max_rows_per_sheet
        chunk = df.iloc[start:end]

        title = f"{base_filename} - Part {i + 1}"
        print(f"\nCreating sheet {i + 1}/{total_files}: {len(chunk)} rows")
        spreadsheet_id = create_spreadsheet(sheets_service, drive_service, title)

        upload_chunk(sheets_service, spreadsheet_id, chunk)

        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        urls.append(url)
    
    # Save URLs to a text file
    output_filename = f"{base_filename}_sheet_urls.txt"
    with open(output_filename, "w") as f:
        for i, url in enumerate(urls, 1):
            f.write(f"Part {i}: {url}\n")
    
    print(f"\n✓ URLs saved to: {output_filename}")
    
    return urls


if __name__ == "__main__":
    urls = process_csv()
    for u in urls:
        print(u)
