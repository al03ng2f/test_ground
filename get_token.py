import requests
import json

def exchange_id_token_for_service_account_token(id_token, config_file_path):
    """
    Exchange the ID token for a service account token using Google's Workload Identity Federation.

    Args:
    - id_token (str): The ID token to be exchanged.
    - config_file_path (str): Path to the configuration file (which contains the URLs and audience).

    Returns:
    - str: The access token for the service account.
    """
    # Load the configuration from the file
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    
    # Extract the relevant data from the config file
    audience = config['audience']
    token_url = config['token_url']
    service_account_impersonation_url = config['service_account_impersonation_url']
    
    # Prepare the payload to exchange the ID token for a token
    payload = {
        "audience": audience,
        "subject_token": id_token,
        "subject_token_type": config["subject_token_type"]
    }
    
    headers = {
        "Content-Type": "application/json",
    }

    try:
        # Step 1: Exchange the ID token for a service account token
        response = requests.post(token_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Step 2: Extract the access token from the response
            response_json = response.json()
            access_token = response_json.get("access_token")
            if access_token:
                # Step 3: Use the access token to impersonate the service account
                service_account_payload = {
                    "delegates": [],
                    "scope": ["https://www.googleapis.com/auth/cloud-platform"],
                    "lifetime": "3600s"  # 1 hour lifetime for the token
                }
                
                # Generate the access token for the service account
                impersonation_response = requests.post(
                    service_account_impersonation_url,
                    json=service_account_payload,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if impersonation_response.status_code == 200:
                    impersonation_response_json = impersonation_response.json()
                    return impersonation_response_json.get("accessToken")
                else:
                    print(f"Error impersonating service account: {impersonation_response.status_code}")
                    print(impersonation_response.text)
                    return None
            else:
                print("Error: No access_token found in token exchange response.")
                return None
        else:
            print(f"Error: Unable to exchange token. Status code: {response.status_code}")
            print(response.text)
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed. {e}")
        return None


# Example usage
id_token = "your-id-token-here"
config_file_path = "test.json"  # Path to the JSON configuration file

access_token = exchange_id_token_for_service_account_token(id_token, config_file_path)

if access_token:
    print("Service Account Access Token:", access_token)
else:
    print("Failed to exchange token.")
