import io
import json
import pathlib
import subprocess
import sys

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import auth


with open("config.json", "r") as f:
    config = json.load(f)

    LOCAL_RESUME_DIR_PATH = pathlib.Path(config["local_resume_dir_path"])
    GDRIVE_RESUME_FOLDER_ID = config["gdrive_resume_folder_id"]
    RESUME_PDF_FILE_NAME = config["resume_pdf_file_name"]


def get_document_by_name(drive_client, file_name):
    results = (
        drive_client.files()
        .list(
            q=f"'{GDRIVE_RESUME_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.document' and name contains '{file_name}' and trashed = false",
            fields="nextPageToken, files(id, name)",
        )
        .execute()
    )

    files = results.get("files")

    if len(files) == 0:
        raise Exception(f"No file found containing the given name: {file_name}")
    if len(files) == 1:
        return files[0]
    else:
        raise Exception(f"Multiple files found containing the given name:\n{'\n'.join(files)}")


def download_pdf(drive_client, file_id):
    request = drive_client.files().export_media(
        fileId=file_id, mimeType="application/pdf"
    )
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Downloading: {int(status.progress() * 100)}% complete")

    return file.getvalue()


def write_pdf_to_disk(pdf_bytes, destination_path):
    with open(destination_path, "wb") as f:
        f.write(pdf_bytes)


def open_finder_to_dir(path):
    subprocess.run(["open", "-a", "finder", path])


def main(file_name):
    creds = auth.auth()
    drive_client = build("drive", "v3", credentials=creds)
    resume = get_document_by_name(drive_client, file_name)
    pdf_bytes = download_pdf(drive_client, resume["id"])
    local_application_dir = LOCAL_RESUME_DIR_PATH / file_name
    write_pdf_to_disk(pdf_bytes, local_application_dir / f"{RESUME_PDF_FILE_NAME}.pdf")
    open_finder_to_dir(local_application_dir)


if __name__ == "__main__":
    file_name = sys.argv[1:][0]
    main(file_name)



# file_name = "2024-05-06 - Company - Position"
#
# creds = auth.auth()
# drive_client = build("drive", "v3", credentials=creds)
#
# results = (
#     drive_client.files()
#     .list(
#         q=f"'{GDRIVE_RESUME_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.document' and name contains '{file_name}' and trashed = false",
#         fields="nextPageToken, files(id, name)",
#     )
#     .execute()
# )
#
# files = results.get("files")
# files
# resume = files[0]
#
# request = drive_client.files().export_media(
#     fileId=resume["id"], mimeType="application/pdf"
# )
# file = io.BytesIO()
# downloader = MediaIoBaseDownload(file, request)
#
# done = False
# while done is False:
#     status, done = downloader.next_chunk()
#     print(f"Downloading: {int(status.progress() * 100)}% complete")
#
# pdf_bytes = file.getvalue()
#
# local_application_dir = LOCAL_RESUME_DIR_PATH / file_name
# pdf_path = local_application_dir / f"{RESUME_PDF_FILE_NAME}.pdf"
# pdf_path
#
# with open(pdf_path, "wb") as f:
#     f.write(pdf_bytes)
#
# subprocess.run(["open", "-a", "finder", local_application_dir])
