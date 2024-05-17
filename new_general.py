from datetime import date
import json
import subprocess

from googleapiclient.discovery import build

import auth


GENERAL_RESUME_BASE_FILE_NAME = "Cort Spellman Resume"

with open("config.json", "r") as f:
    config = json.load(f)

    GDRIVE_GENERAL_RESUME_FOLDER_ID = config["gdrive_general_resume_folder_id"]


def most_recent_general_resume(drive_client):
    results = (
        drive_client.files()
        .list(
            q=f"'{GDRIVE_GENERAL_RESUME_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.document' and trashed = false",
            pageSize=1,
            fields="nextPageToken, files(id, name)",
            orderBy="name desc",
        )
        .execute()
    )

    files = results.get("files")

    if files:
        return files[0]
    else:
        return None


def branch_off_most_recent_general_resume(drive_client, new_file_name):
    source = most_recent_general_resume(drive_client)

    if not source:
        raise Exception(
            f"No general resume found; can't make a copy to customize. Searched in {GDRIVE_GENERAL_RESUME_FOLDER_ID} folder of Google Drive."
        )

    copy = (
        drive_client.files()
        .copy(fileId=source["id"], body={"name": new_file_name}, fields="id,webViewLink")
        .execute()
    )

    return copy


def open_file_in_firefox(file):
    link = file["webViewLink"].removesuffix("?usp=drivesdk")
    subprocess.run(["open", "-a", "firefox", link])


def main(new_file_name):
    creds = auth.auth()
    drive_client = build("drive", "v3", credentials=creds)
    resume = branch_off_most_recent_general_resume(drive_client, new_file_name)
    open_file_in_firefox(resume)


def file_name():
    return f"{date.today()} {GENERAL_RESUME_BASE_FILE_NAME}"



if __name__ == "__main__":
    main(file_name())
