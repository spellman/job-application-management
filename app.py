from datetime import date
import json
import pathlib
import subprocess
import sys

from googleapiclient.discovery import build

import auth


with open("config.json", "r") as f:
    config = json.load(f)

    LOCAL_RESUME_DIR_PATH = pathlib.Path(config["local_resume_dir_path"])
    GDRIVE_RESUME_FOLDER_ID = config["gdrive_resume_folder_id"]
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
        .copy(fileId=source["id"], body={"name": new_file_name}, fields="id,parents")
        .execute()
    )

    initial_parents_of_copy = ",".join(copy["parents"])

    moved_copy = (
        drive_client.files()
        .update(
            fileId=copy["id"],
            addParents=GDRIVE_RESUME_FOLDER_ID,
            removeParents=initial_parents_of_copy,
            fields="id,name,webViewLink",
        )
        .execute()
    )

    return moved_copy


def open_file_in_firefox(file):
    link = file["webViewLink"].removesuffix("?usp=drivesdk")
    subprocess.run(["open", "-a", "firefox", link])


def create_local_file(new_file_name):
    company_dir_path = LOCAL_RESUME_DIR_PATH / new_file_name
    company_dir_path.mkdir(exist_ok=False)

    company_file = company_dir_path / f"{new_file_name}.txt"
    company_file.touch(exist_ok=False)
    skeleton_text = f"""{new_file_name}

Job Listing


Found Via


Submitted Application: {date.today()}

"""

    with open(company_file, "w") as f:
        f.write(skeleton_text)

    return company_file


def open_file_in_text_edit(file):
    subprocess.run(["open", "-a", "textedit", file])


def main(new_file_name):
    creds = auth.auth()
    drive_client = build("drive", "v3", credentials=creds)
    resume = branch_off_most_recent_general_resume(drive_client, new_file_name)
    text_file = create_local_file(new_file_name)
    open_file_in_text_edit(text_file)
    open_file_in_firefox(resume)


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



# new_name = "2024-05-06 - Company - Position"
#
# creds = auth.auth()
#
# drive_client = build("drive", "v3", credentials=creds)
#
# source = most_recent_general_resume(drive_client)
# source
#
# copy = (
#     drive_client.files()
#     .copy(
#         fileId=source["id"],
#         body={"name": new_name},
#         fields="id,parents",
#     )
#     .execute()
# )
# copy
#
# initial_parents_of_copy = ",".join(copy["parents"])
# initial_parents_of_copy
#
# moved_copy = (
#     drive_client.files()
#     .update(
#         fileId=copy["id"],
#         addParents=GDRIVE_RESUME_FOLDER_ID,
#         removeParents=initial_parents_of_copy,
#         fields="id,name,webViewLink",
#     )
#     .execute()
# )
# moved_copy
#
# link = moved_copy["webViewLink"].removesuffix("?usp=drivesdk")
# link # 'https://docs.google.com/document/d/126ulXRAbemObRv-v3pOnajzs1njRAc_n4rGf1SNqSs8/edit'
#
# subprocess.run(["open", "-a", "firefox", link])
#
# local_path = LOCAL_RESUME_DIR_PATH / new_name
# local_path
# local_path.mkdir()
#
# company_file = local_path / f"{new_name}.txt"
# company_file.touch(exist_ok=False)
# file_contents = f"""{new_name}
#
# Job Listing
#
#
# Found Via
#
#
# Submitted Application: {date.today()}
#
# """
#
# with open(company_file, "w") as f:
#     f.write(file_contents)
#
# subprocess.run(["open", "-a", "textedit", company_file])
