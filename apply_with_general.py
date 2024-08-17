from datetime import date
import sys

from googleapiclient.discovery import build

import app
import auth
import pdf


def main(file_name):
    creds = auth.auth()
    drive_client = build("drive", "v3", credentials=creds)

    app.branch_off_most_recent_general_resume(drive_client, file_name)
    text_file = app.create_local_file(file_name)
    app.open_file_in_text_edit(text_file)

    pdf.main(file_name)


def prefix_with_date_if_undated(file_name: str):
    """If the file_name starts with a date segment, then return the file_name as
    is. Otherwise, prefix it with today's date and ` - `."""
    try:
        date.fromisoformat(file_name.split(" - ")[0])
        return file_name
    except ValueError:
        return f"{date.today()} - {file_name}"



if __name__ == "__main__":
    file_name = sys.argv[1:][0]
    main(prefix_with_date_if_undated(file_name))
