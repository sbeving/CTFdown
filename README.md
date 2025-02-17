# CTFd Challenge Downloader

[![Python Version](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) <!-- Replace LICENSE with your actual license file name -->

A Python script to download challenges from a CTFd platform and generate well-organized Markdown files for offline CTF training and archiving.

## Description

**CTFd Challenge Downloader** is a command-line tool designed to automate the process of extracting Capture The Flag (CTF) challenges from platforms built using the CTFd framework. It fetches challenge data via the CTFd API and organizes it into a structured format for:

*   **Offline CTF Practice:** Study and solve challenges locally without constant platform access.
*   **CTF Team Training:** Create a local archive of past CTF challenges for team training and knowledge sharing.
*   **Challenge Archival:** Preserve challenges from CTFs that are paused or have ended for future reference.

The script generates Markdown (`.md`) files for each challenge, containing:

*   Challenge Name, ID, Value, and Category
*   Challenge Description (sanitized for Markdown)
*   Challenge Tags
*   Links to associated files (with optional local downloads)

Challenges are organized into a clear folder structure, categorized by challenge category, making it easy to navigate and find specific challenges.

## Features

*   **Comprehensive Challenge Data Extraction:** Retrieves all essential challenge information from the CTFd API.
*   **Clean Markdown Output:** Generates well-formatted `readme.md` files for each challenge, ready for reading and editing.
*   **Categorized and Organized Output:** Structures challenges into category and challenge-specific folders for easy browsing.
*   **Optional File Downloading:** Downloads challenge files hosted on the CTFd platform, creating local copies within challenge folders and updating `readme.md` with local file links. Supports skipping downloads for external file links (e.g., Google Drive).
*   **Flexible Command-Line Interface (CLI):** Configurable via `argparse` with options for:
    *   **Session Cookie (-S, --session_cookie):** Authenticate with the CTFd platform.
    *   **CTFd Domain (-D, --domain):** Specify the CTFd platform's domain.
    *   **Output Directory (-O, --output):** Customize the parent output directory.
    *   **Start/Stop Challenge IDs (--start_id, --stop_id):** Download a specific range of challenges.
    *   **No File Download (--no-download):** Generate Markdown only, without downloading files.
    *   **Verbosity Control (-v, --verbosity):** Adjust the level of output logging.
*   **Domain Agnostic:** Works with any CTFd platform instance.
*   **Robust Error Handling:** Gracefully handles API errors, network issues, and JSON parsing problems.

## Usage

### Prerequisites

*   **Python 3.7+** (recommended) or Python 3.x installed on your system.
*   **Python `requests` library:** Install using `pip install requests` or `pip3 install requests`.



### Installation 

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/0xsbeve/CTFdown
    cd CTFdown
    pip install -r requirements.txt 
    ```

2.  **Install Dependencies (Recommended):**

    ```bash
    pip install -r requirements.txt # Installs the 'requests' library
    ```

### Obtaining Your Session Cookie

To authenticate with the CTFd platform, you need to provide your session cookie.

1.  **Log in to the CTFd platform** (e.g., `https://ctf.example.com`) in your web browser.
2.  **Open Developer Tools:** (Usually `F12` or Right-Click -> "Inspect").
3.  **Navigate to the "Network" Tab.**
4.  **Refresh the Page** (`F5`) to capture network requests.
5.  **Select any Network Request** made to the CTFd platform's domain (e.g., to `/api/v1/challenges`).
6.  **Find the "Cookie" Request Header:** In the "Headers" tab of the selected request, look for the `Cookie` header under "Request Headers".
7.  **Copy the `session` Cookie Value:**  Copy the value associated with the `session` cookie. It will resemble: `session=long_alphanumeric_string`. **Only copy the part after `session=`**.

### Running the Script

Open your terminal, navigate to the script's directory (`app.py`), and execute it with `python app.py` followed by the required and optional arguments.

**Basic Usage (Minimum Arguments):**

```bash
python app.py -S "YOUR_SESSION_COOKIE" -D "ctf.example.com"
```

*   **`-S "YOUR_SESSION_COOKIE"`** or **`--session_cookie "YOUR_SESSION_COOKIE"`**:  **(Required)**. Replace `"YOUR_SESSION_COOKIE"` with the actual session cookie value you obtained. **Important:** Enclose your cookie in double quotes if it contains special characters.
*   **`-D "ctf.example.com"`** or **`--domain "ctf.example.com"`**: **(Required)**. Replace `"ctf.example.com"` with the domain name of the CTFd platform (e.g., `"ctf.example.com"`). **Important:** Enclose the domain in double quotes.

**Optional Arguments:**

*   **`-O output_directory`** or **`--output output_directory`**:  Customize the parent output directory where CTF challenge folders will be created. Defaults to `output`.
    ```bash
    python app.py -S "YOUR_SESSION_COOKIE" -D "ctf.example.com" -O "my_ctf_archive"
    ```

*   **`--start_id / -s START_CHALLENGE_ID`**:  Specify the challenge ID to begin downloading from. Defaults to `1`.
    ```bash
    python app.py -S "YOUR_SESSION_COOKIE" -D "ctf.example.com" --start_id 5
    ```

*   **`--stop_id / -e STOP_CHALLENGE_ID`**: Specify the challenge ID to stop downloading at (inclusive). If omitted, the script will continue until no more challenges are found.
    ```bash
    python app.py -S "YOUR_SESSION_COOKIE" -D "ctf.example.com" --stop_id 50
    ```

*   **`--no-download`**:  Disable automatic file downloading. Only Markdown `readme.md` files will be generated with links to files on the CTFd platform.
    ```bash
    python app.py -S "YOUR_SESSION_COOKIE" -D "ctf.example.com" --no-download
    ```

*   **`-v VERBOSITY_LEVEL`** or **`--verbosity VERBOSITY_LEVEL`**: Control the verbosity level of the script's output. Choose from:
    *   `0`: **Quiet** - Minimal output, primarily errors.
    *   `1`: **Normal** (Default) - Standard progress and status messages.
    *   `2`: **Verbose** - Detailed output, including HTTP status codes, download URLs, and debugging information.
    ```bash
    python app.py -S "YOUR_SESSION_COOKIE" -D "ctf.example.com" -v 2
    ```

**Example with All Options:**

```bash
python app.py -S "YOUR_SESSION_COOKIE" -D challenges.vulnhub.com -O "vulnhub_challenges" -s 1 -e 100 --no-download -v 1
```
> Added -s **startIndex** and -e **endIndex** to limit script map otherwise it will run endlessly.

### Output Folder Structure

Upon successful execution, the script will create a parent directory (default: `output`). Inside this directory, you'll find a folder named after the CTFd platform's domain (with `.` replaced by `_`, e.g., `ctf_example_com`). This CTF-specific folder will contain categorized challenge folders, each with a `readme.md` file and (optionally) downloaded files.

```
output/
└── ctf_example_com/           (Parent folder for the CTF, named after the domain)
    ├── Crypto/                (Challenge Category Folder)
    │   └── Challenge_Name_123/  (Challenge Folder - Sanitized Challenge Name + ID)
    │       ├── readme.md      (Markdown file containing challenge details)
    │       ├── challenge_file1.zip
    │       └── ...
    ├── Web_Exploitation/
    │   └── ...
    └── ...
```



## Disclaimer

**Use Responsibly and Ethically.** This script is provided for educational purposes and for archiving CTF challenges for legitimate personal or team training activities. **Always respect the rules, terms of service, and ethical guidelines of any CTF platform you interact with.**  Avoid using this tool in any way that could:

*   Disrupt or overload CTFd platforms.
*   Violate CTF rules or terms of service.
*   Infringe upon intellectual property rights.

The authors and contributors are not responsible for any misuse of this script.

---

