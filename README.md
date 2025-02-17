# CTFd Challenge Downloader

A Python script to download challenges from a CTFd platform and generate well-organized Markdown files for offline CTF training and archiving.

## Description

This script automates the process of extracting challenges from a CTFd (Capture The Flag platform framework) instance. It fetches challenge data from the CTFd API and creates a structured output of Markdown files, organized by category and challenge name.  Optionally, it can also download challenge files hosted on the CTFd platform itself.

This tool is designed to help CTF teams:

*   **Archive CTF Challenges:**  Create a local copy of CTF challenges for future reference and training, especially for paused or finished CTFs.
*   **Offline Training:**  Study challenges offline in a well-organized format, without needing to be actively logged into the CTF platform.
*   **Community Sharing:**  Easily share challenge information and local files with team members for collaborative learning.

## Features

*   **Downloads Challenge Information:** Extracts challenge name, ID, value, category, description, tags, and file links from the CTFd API.
*   **Markdown Output:** Generates a `readme.md` file for each challenge, neatly formatted with challenge details, description, and file links.
*   **Organized Folders:** Creates a structured output directory:
    ```
    output/
    └── ctf_domain_com/       (Parent folder named after the CTF domain)
        ├── Category_Name/      (Category folders)
        │   └── Challenge_Name_ID/ (Challenge folders)
        │       ├── readme.md    (Markdown file with challenge info)
        │       └── [files...]     (Downloaded challenge files - if any)
        └── ...
    └── ...
    ```
*   **File Downloading:** Downloads files linked from challenges (only from the CTFd platform's domain).
    *   Creates local links in `readme.md` to downloaded files.
    *   Provides direct links to the CTF platform for files hosted externally or if download fails.
*   **Command-Line Interface (CLI):** Uses `argparse` for easy configuration via command-line arguments.
*   **Verbosity Control:** Offers different verbosity levels (`-v`) to control the script's output (quiet, normal, verbose).
*   **Domain Agnostic:** Works with any CTFd platform by specifying the `-D` or `--domain` argument.
*   **Start ID Option:** Allows you to specify a starting challenge ID (`--start_id`) to begin fetching from a specific challenge.
*   **No-Download Option:**  `--no-download` flag to skip file downloading and only generate Markdown files.

## Usage

### Prerequisites

*   **Python 3.x** installed on your system.
*   **Python `requests` library:** Install using `pip install requests` (or `pip3 install requests`).

### Installation (Optional)

While installation isn't strictly necessary to run the script, you can clone the repository from GitHub if you plan to contribute or track changes.

```bash
git clone [YOUR_GITHUB_REPOSITORY_URL]
cd CTFd-Challenge-Downloader # Or your repository folder name
```

### Getting Your Session Cookie

The script requires a session cookie to authenticate with the CTFd platform and access challenge data. Here's how to obtain it from your browser:

1.  **Log in to the CTFd platform** in your web browser (e.g., `https://dh.securinets.tn`).
2.  **Open your browser's Developer Tools** (usually by pressing `F12`).
3.  Go to the **"Network"** tab.
4.  **Refresh the page** (`F5`) to capture network requests.
5.  Select **any request** made to the CTFd platform's domain (e.g., a request to `/api/v1/challenges`).
6.  In the "Request Headers" section of the selected request, look for the **`Cookie`** header.
7.  **Copy the value of the `session` cookie.** It will look something like: `session=long_alphanumeric_string.more_alphanumeric_string` (only copy the part after `session=`).

### Running the Script

Open your terminal, navigate to the directory where you saved `app.py`, and run the script using `python app.py` followed by the arguments.

**Basic Usage (Minimum Required Arguments):**

```bash
python app.py -S YOUR_SESSION_COOKIE -D ctf.example.com
```

*   **`-S YOUR_SESSION_COOKIE`** or **`--session_cookie YOUR_SESSION_COOKIE`**: **Required**. Replace `YOUR_SESSION_COOKIE` with the session cookie you copied from your browser.
*   **`-D ctf.example.com`** or **`--domain ctf.example.com`**: **Required**. Replace `ctf.example.com` with the domain of the CTFd platform you are targeting (e.g., `dh.securinets.tn`).

**Optional Arguments:**

*   **`-O output_directory`** or **`--output output_directory`**:  Specify a parent output directory for the CTF challenge folders. Defaults to `output`.
    ```bash
    python app.py -S YOUR_SESSION_COOKIE -D ctf.example.com -O my_ctf_data
    ```

*   **`--start_id START_CHALLENGE_ID`**: Specify the challenge ID to start downloading from. Defaults to `1`.
    ```bash
    python app.py -S YOUR_SESSION_COOKIE -D ctf.example.com --start_id 10
    ```

*   **`--no-download`**:  Disable file downloading. Only Markdown files will be generated.
    ```bash
    python app.py -S YOUR_SESSION_COOKIE -D ctf.example.com --no-download
    ```

*   **`-v VERBOSITY_LEVEL`** or **`--verbosity VERBOSITY_LEVEL`**: Control the verbosity level of the output:
    *   `0`: Quiet mode (minimal output, only errors).
    *   `1`: Normal mode (default) - standard output messages.
    *   `2`: Verbose mode - detailed output for debugging (includes response codes, raw content, etc.).
    ```bash
    python app.py -S YOUR_SESSION_COOKIE -D ctf.example.com -v 2
    ```

**Example with all options:**

```bash
python app.py -S YOUR_SESSION_COOKIE -D challenges.vulnhub.com -O vulnhub_ctf --start_id 5 --no-download -v 1
```

### Output Folder Structure

After running the script, you will find a parent folder (default: `output`) containing a folder named after the CTF domain (e.g., `ctf_example_com`). Inside this CTF folder, challenges are organized into category folders, and each challenge has its own folder containing `readme.md` and downloaded files.

```
output/
└── ctf_example_com/
    ├── Web_Exploitation/
    │   └── Challenge_Name_123/
    │       ├── readme.md
    │       ├── file1.zip
    │       └── ...
    └── ...
```

## License

[Specify your License here, e.g., MIT License]

## Contributing

[Optional: Add information about how others can contribute to the project, e.g., pull requests, bug reports, feature requests]

## Disclaimer

This script is intended for educational purposes and for archiving CTF challenges for personal or team training.  **Always respect the rules and terms of service of any CTF platform.**  Do not use this script in a way that could disrupt or harm CTF platforms or violate their terms of service. Use responsibly and ethically.

---

**This `README.md` provides a good starting point for your GitHub project.** You can customize it further with your specific project details, contribution guidelines, license information, and any other relevant information you want to include. Good luck with your project!