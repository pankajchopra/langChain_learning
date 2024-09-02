from google.oauth2 import service_account

GOOGLE_JSON_PATH = "./gen-lang-client-0922515850-122f4c31e605.json"


def get_google_credentials(json_path):
    if json_path is None:
        credentials = service_account.Credentials.from_service_account_file(GOOGLE_JSON_PATH)
    else:
        """Load Google Cloud credentials from a JSON key file."""
        credentials = service_account.Credentials.from_service_account_file(json_path)
    return credentials
