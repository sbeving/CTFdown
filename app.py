import requests
import os
import re
import urllib.parse # Import urllib.parse for URL joining
import argparse
import json # Import json for potential JSONDecodeError handling

def get_all_challenge_ids(session_cookie, domain, verbosity, csrf_token=None):
    """Fetches all available challenge IDs from the CTF platform."""
    url = f"https://{domain}/api/v1/challenges"
    headers = {
        "Cookie": f"session={session_cookie}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Content-Type": "application/json",
        "Priority": "u=1, i",
        "Referer": f"https://{domain}/challenges",
        "Sec-Ch-UA": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "Sec-Ch-UA-Mobile": "?0",
        "Sec-Ch-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    # Add CSRF token if provided
    if csrf_token:
        headers["csrf-token"] = csrf_token
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        if verbosity >= 2:
            print(f"Verbose: Response status code for challenge list: {response.status_code}")
        
        try:
            data = response.json()
            if data.get('success') and 'data' in data:
                challenge_ids = [challenge['id'] for challenge in data['data'] if challenge.get('type') != 'hidden']
                if verbosity >= 1:
                    print(f"Found {len(challenge_ids)} available challenges: {sorted(challenge_ids)}")
                return sorted(challenge_ids)
            else:
                if verbosity >= 1:
                    print("Error: API response indicates failure or missing data.")
                return []
        except json.JSONDecodeError:
            if verbosity >= 1:
                print("Error: Could not decode JSON response for challenge list.")
                if verbosity >= 2:
                    print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
                    print(f"Raw response content (first 1000 chars):\n{response.text[:1000]}")
            return []

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching challenge list: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Request Error fetching challenge list: {e}")
        return []

def get_challenge_data(challenge_id, session_cookie, domain, verbosity, csrf_token=None):
    """Fetches challenge data from the API."""
    url = f"https://{domain}/api/v1/challenges/{challenge_id}"
    headers = {
        "Cookie": f"session={session_cookie}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Content-Type": "application/json",
        "Priority": "u=1, i",
        "Referer": f"https://{domain}/challenges",
        "Sec-Ch-UA": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "Sec-Ch-UA-Mobile": "?0",
        "Sec-Ch-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    # Add CSRF token if provided
    if csrf_token:
        headers["csrf-token"] = csrf_token
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        if verbosity >= 2: # Verbose level 2 for detailed output
            print(f"Verbose: Response status code for challenge {challenge_id}: {response.status_code}")
        try:
            return response.json() # Try to parse as JSON
        except json.JSONDecodeError: # Catch JSON parsing errors
            if verbosity >= 1:
                print(f"Error: Could not decode JSON response for challenge {challenge_id}.")
                if verbosity >= 2:
                    print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
                    print(f"Response status: {response.status_code}")
                    print(f"Raw response content (first 1000 chars):\n{response.text[:1000]}")
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

    # Add connection info if available
    if challenge_data['data'].get('connection_info'):
        markdown_file_content += f"## Connection\n```\n{challenge_data['data']['connection_info']}\n```\n\n"

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
parser.add_argument("--start_id", type=int, help="Starting challenge ID (enables manual mode instead of auto-fetch)") # Make optional
parser.add_argument("--stop_id", type=int, help="Stopping challenge ID (only used with --start_id in manual mode)") # Add stop_id argument
parser.add_argument("--no-download", action="store_true", help="Disable file downloading") # Add --no-download flag
parser.add_argument("--max-failures", type=int, default=10, help="Maximum consecutive failures before stopping (default: 10, only used in manual mode)")
parser.add_argument("--csrf-token", help="CSRF token for API requests (optional)")
parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2], help="Verbosity level (0: quiet, 1: normal, 2: verbose, default: 1)") # Add verbosity argument

args = parser.parse_args()

if __name__ == "__main__":
    session_cookie = args.session_cookie
    domain = args.domain
    output_parent_directory = args.output
    start_challenge_id = args.start_id
    stop_challenge_id = args.stop_id
    enable_download = not args.no_download
    max_consecutive_failures = args.max_failures
    csrf_token = args.csrf_token
    verbosity_level = args.verbosity

    ctf_output_dir = os.path.join(output_parent_directory, domain.replace(".","_"))
    if not os.path.exists(ctf_output_dir):
        os.makedirs(ctf_output_dir)

    # Determine mode: auto-fetch (default) or manual (when start_id is specified)
    if start_challenge_id is not None:
        # Manual mode: iterate through ID range
        if verbosity_level >= 1:
            range_info = f"from {start_challenge_id}"
            if stop_challenge_id:
                range_info += f" to {stop_challenge_id}"
            else:
                range_info += " onwards"
            print(f"Manual mode: fetching challenges {range_info}...")
        
        challenge_id = start_challenge_id
        consecutive_failures = 0
        
        while True:
            if stop_challenge_id and challenge_id > stop_challenge_id:
                if verbosity_level >= 1:
                    print(f"Stopping challenge download at challenge ID {stop_challenge_id} as requested.")
                break

            if verbosity_level >= 1:
                print(f"Fetching challenge {challenge_id} from {domain}...")
            
            challenge_json = get_challenge_data(challenge_id, session_cookie, domain, verbosity_level, csrf_token)
            if challenge_json and challenge_json.get('success'):
                create_markdown_file(challenge_json, ctf_output_dir, domain, session_cookie, verbosity_level)
                consecutive_failures = 0  # Reset failure counter on success
            else:
                consecutive_failures += 1
                if verbosity_level >= 1:
                    print(f"Challenge {challenge_id} not found or error encountered on {domain}. Skipping.")
                
                # Stop if too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    if verbosity_level >= 1:
                        print(f"Stopping after {max_consecutive_failures} consecutive failures. No more challenges found.")
                    break
            
            challenge_id += 1  # Always increment to continue to next challenge
    
    else:
        # Auto-fetch mode (default): get all challenge IDs from API
        if verbosity_level >= 1:
            print(f"Auto-fetching challenge IDs from {domain}...")
        
        challenge_ids = get_all_challenge_ids(session_cookie, domain, verbosity_level, csrf_token)
        
        if not challenge_ids:
            print("Error: Could not fetch challenge IDs. Please check your session cookie and domain.")
            exit(1)
        
        # Process each challenge
        for challenge_id in challenge_ids:
            if verbosity_level >= 1:
                print(f"Processing challenge {challenge_id}...")
            
            challenge_json = get_challenge_data(challenge_id, session_cookie, domain, verbosity_level, csrf_token)
            if challenge_json and challenge_json.get('success'):
                create_markdown_file(challenge_json, ctf_output_dir, domain, session_cookie, verbosity_level)
            else:
                if verbosity_level >= 1:
                    print(f"Skipping challenge {challenge_id} due to error.")

    if verbosity_level >= 1:
        print(f"\nChallenge Markdown files saved in '{ctf_output_dir}' directory.")