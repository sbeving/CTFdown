import requests
import os
import re  # Import the re module
import urllib.parse # Import urllib.parse for URL joining
import argparse
import json # Import json for potential JSONDecodeError handling

def get_challenge_data(challenge_id, session_cookie, domain, verbosity):
    """Fetches challenge data from the API."""
    url = f"https://{domain}/api/v1/challenges/{challenge_id}"
    headers = {
        "Cookie": f"session={session_cookie}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8,fr;q=0.7",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Priority": "u=0, i",
        "Sec-Ch-UA": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "Sec-Ch-UA-Mobile": "?0",
        "Sec-Ch-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        if verbosity >= 2: # Verbose level 2 for detailed output
            print(f"Verbose: Response status code for challenge {challenge_id}: {response.status_code}")
        try:
            return response.json() # Try to parse as JSON
        except json.JSONDecodeError: # Catch JSON parsing errors
            print(f"Error: Could not decode JSON response for challenge {challenge_id}. Raw response content:\n{response.text}")
            return None # Return None if JSON parsing fails

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            if verbosity >= 1: # Verbose level 1 for normal output
                print(f"Challenge {challenge_id} not found.")
            return None  # Challenge not found
        else:
            print(f"HTTP Error for challenge {challenge_id}: {e}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request Error for challenge {challenge_id}: {e}")
        return None

def create_markdown_file(challenge_data, output_dir, domain, session_cookie, verbosity): # Added verbosity argument
    """Creates a Markdown file for a challenge in category/challenge folders and downloads files."""

    category_name = challenge_data['data']['category']
    challenge_name = challenge_data['data']['name']
    challenge_id = challenge_data['data']['id']

    # Sanitize category and challenge names for folder names (replace spaces and special chars with _)
    safe_category_name = re.sub(r'[^a-zA-Z0-9_]+', '_', category_name)
    safe_challenge_name = re.sub(r'[^a-zA-Z0-9_]+', '_', challenge_name)
    challenge_folder_name = f"{safe_challenge_name}_{challenge_id}"

    category_dir = os.path.join(output_dir, safe_category_name) # output_dir is now "output/ctf_name"
    challenge_dir = os.path.join(category_dir, challenge_folder_name)

    os.makedirs(challenge_dir, exist_ok=True) # Create category and challenge folders if they don't exist

    file_name = "readme.md" # readme.md inside challenge folder
    file_path = os.path.join(challenge_dir, file_name)

    markdown_file_content = f"# {challenge_name}\n\n" # Start building markdown content
    markdown_file_content += f"**ID:** {challenge_id}\n"
    markdown_file_content += f"**Value:** {challenge_data['data']['value']} points\n"
    markdown_file_content += f"**Category:** {category_name}\n"
    markdown_file_content += "**Tags:** "
    if challenge_data['data']['tags']:
        markdown_file_content += ", ".join([tag for tag in challenge_data['data']['tags']]) + "\n"
    else:
        markdown_file_content += "None\n"
    markdown_file_content += "\n"

    # Sanitize description to handle potential HTML and format for Markdown
    description_md = challenge_data['data']['description']
    description_md = re.sub(r'<[^>]*>', '', description_md) # Remove HTML tags
    markdown_file_content += f"## Description\n{description_md}\n\n"

    if challenge_data['data']['files']:
        markdown_file_content += "## Files\n"
        local_files_links = [] # List to store local file links for readme.md
        for file_url_path in challenge_data['data']['files']: # file_url_path is just the path from API
            full_file_url = urllib.parse.urljoin(f"https://{domain}", file_url_path) # Create full URL using domain argument
            parsed_url = urllib.parse.urlparse(full_file_url)

            if parsed_url.netloc == domain: # Check if domain matches the provided domain
                filename_start_index = file_url_path.rfind('/') + 1
                filename_end_index = file_url_path.rfind('?')
                if filename_end_index != -1 and filename_start_index < filename_end_index:
                    filename = file_url_path[filename_start_index:filename_end_index] # use path to extract filename
                else:
                    filename = file_url_path[filename_start_index:] # use path to extract filename

                download_path = os.path.join(challenge_dir, filename) # Local download path

                if verbosity >= 1: # Verbose level 1 for normal output
                    print(f"Downloading file: {full_file_url} to {download_path}")
                if verbosity >= 2: # Verbose level 2 for detailed output
                    print(f"Verbose: Downloading from URL: {full_file_url}")

                try:
                    with requests.get(full_file_url, stream=True, headers={"Cookie": f"session={session_cookie}"}) as response: # Include cookie for download
                        response.raise_for_status()
                        with open(download_path, 'wb') as file_handle:
                            for chunk in response.iter_content(chunk_size=8192):
                                file_handle.write(chunk)
                    local_files_links.append(f"- [{filename}](./{filename})") # Local link for readme
                except requests.exceptions.RequestException as e:
                    print(f"Download error for {full_file_url}: {e}")
                    markdown_file_content += f"- [Download {filename} from CTF platform]({full_file_url}) (Download failed, check console output)\n" # Link to CTF platform if download fails
                    continue # Skip to next file if download fails

            else: # If not the CTF platform domain, just create external link
                filename_start_index = full_file_url.rfind('/') + 1
                filename_end_index = full_file_url.rfind('?')
                if filename_end_index != -1 and filename_start_index < filename_end_index:
                    filename = file_url_path[filename_start_index:filename_end_index] # use path to extract filename
                else:
                    filename = file_url_path[filename_start_index:] # use path to extract filename
                markdown_file_content += f"- [{filename}]({full_file_url})\n" # External link

        if local_files_links: # Add local file links to readme if downloads were successful
            markdown_file_content += "\n**Local Files:**\n" + "\n".join(local_files_links) + "\n"
        else:
            markdown_file_content += "\nNo files downloaded.\n" # Indicate if no files were downloaded

    else:
        markdown_file_content += "## Files\nNo files provided.\n"

    markdown_file_content += "\n---\n*Extracted from [{domain} CTF](https://{domain})*\n".format(domain=domain) # Use domain argument in footer

    with open(file_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_file_content) # Write the complete markdown content

    if verbosity >= 1: # Verbose level 1 for normal output
        print(f"Markdown file created for challenge {challenge_id}: {file_path}")
    if verbosity >= 2: # Verbose level 2 for detailed output
        print(f"Verbose: Markdown content written to: {file_path}")


# add argument parser
parser = argparse.ArgumentParser(description="Download challenges from a CTFd platform and create Markdown files.") # More descriptive description
parser.add_argument("-S", "--session_cookie", required=True, help="Session cookie from the browser. Required.") # Make session_cookie required and add help
parser.add_argument("-D", "--domain", required=True, help="Domain of the CTFd platform (example: dh.securinets.tn)") # Add default and help for domain
parser.add_argument("-O", "--output", default="output", help="Parent output directory for CTF challenge folders (default: output)") # Changed default output to "output" and updated help
parser.add_argument("--start_id", type=int, default=1, help="Starting challenge ID (default: 1)") # Add start_id argument with default and help
parser.add_argument("--stop_id", type=int, help="Stopping challenge ID (optional, script will stop at this ID)") # Add stop_id argument
parser.add_argument("--no-download", action="store_true", help="Disable file downloading") # Add --no-download flag
parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2], help="Verbosity level (0: quiet, 1: normal, 2: verbose, default: 1)") # Add verbosity argument

args = parser.parse_args()

if __name__ == "__main__":
    session_cookie = args.session_cookie # Get session cookie from arguments
    domain = args.domain # Get domain from arguments
    output_parent_directory = args.output # Get parent output directory from arguments, renamed to be more clear
    start_challenge_id = args.start_id # Get start_id from arguments
    stop_challenge_id = args.stop_id # Get stop_id from arguments
    enable_download = not args.no_download # Determine if download is enabled
    verbosity_level = args.verbosity # Get verbosity level from arguments

    ctf_output_dir = os.path.join(output_parent_directory, domain.replace(".","_")) # Create CTF-specific output folder inside "output"
    if not os.path.exists(ctf_output_dir):
        os.makedirs(ctf_output_dir)

    challenge_id = start_challenge_id
    while True:
        if stop_challenge_id and challenge_id > stop_challenge_id: # Check stop_id condition
            if verbosity_level >= 1:
                print(f"Stopping challenge download at challenge ID {stop_challenge_id} as requested.")
            break

        if verbosity_level >= 1: # Verbose level 1 for normal output
            print(f"Fetching challenge {challenge_id} from {domain}...") # More informative fetching message
        challenge_json = get_challenge_data(challenge_id, session_cookie, domain, verbosity_level) # Pass verbosity level
        if challenge_json and challenge_json['success']:
            create_markdown_file(challenge_json, ctf_output_dir, domain, session_cookie, verbosity_level) # Pass verbosity level and ctf_output_dir
            challenge_id += 1
        else:
            if verbosity_level >= 1: # Verbose level 1 for normal output
                print(f"Challenge {challenge_id} not found or error encountered on {domain}. Stopping.") # More informative error message
                challenge_id += 1 # Increment challenge_id even if error occurs to avoid infinite loop
            pass # Stop on error for better control

    if verbosity_level >= 1: # Verbose level 1 for normal output
        print(f"\nChallenge Markdown files saved in '{ctf_output_dir}' directory.")