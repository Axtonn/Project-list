# Download file using using reuqests
# By: Zijin Wang SID: 500461859
# Date: 25/08/24
import requests


def download_file(url: str, filename=''):
    """
    Helper Function: Downloads file from URL at spesified location

    url: String of text for the URL of download file
    filename: Filepath for where the file is saved

    Returns: Filepath if successful, None if failed
    """
    try:
        if filename:
            pass
        else:
            return None

        with requests.get(url) as req:
            with open(filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filename
    except Exception as e:
        print(e)
        return None
