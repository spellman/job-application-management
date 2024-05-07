# To Run (Mac Only)

1. Set up your environment as per the steps in https://developers.google.com/drive/api/quickstart/python#set_up_your_environment
2. Ensure [Python Poetry](https://python-poetry.org/) is installed: https://python-poetry.org/docs/#installation
3. Ensure [Firefox](https://www.mozilla.org/en-US/firefox/) is installed.
4. Ensure [fzf](https://github.com/junegunn/fzf) is installed and on the path as `fzf`.
5. Install dependencies: `poetry install`
6. Copy `example-config.json` to `config.json` and fill in the various values. You'll have to get the Google Drive folder IDs by listing the files of mimeType folder in your Google Drive and inspecting the result.
7. Ensure the virtual environment with the Python dependencies is activated: https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment
8. `python app.py <unique job-application name>`
    * Ex: `python app.py '2024-01-01 - Company - Position'`
    * Five things should happen:
        * A new resume, copied from the latest general resume, should be created with the given name in the resumes folder of Google Drive.
        * The new resume should be opened in the firefox web browser.
        * A subdirectory of the local resumes directory should be created with the given name.
        * A text file with the given name and a skeleton structure should be created in the new local subdirectory.
        * The text file should be opened with TextEdit.
9. Make changes the job-specific resume.
10. `./pdf` (or `sh ./pdf` if you don't want to make it executable)
11. Choose the job-specific application from the list. Use the arrow keys or type to fuzzy-match the name (uses fzf). Press enter.
    * Two things should happen:
        * The new resume should be downloaded as a PDF to the job-specific subdirectory.
        * The subdirectory should be opened in the finder.
