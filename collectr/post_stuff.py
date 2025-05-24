def post_card(card_id, base_url, user_id, collection_id, card_count, card_type, auth_token):
    import requests
    import json

    url = f"{base_url}{user_id}/products/{card_id}?collectionId={collection_id}"

    # gradeId needs to be null, not None

    post_body = {
        "gradeId": None,
        "quantity": card_count,
        "subType": card_type
    }

    # Header has Authorization token
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        'Authorization': f'{auth_token}',
        "Cache-Control": "no-cache",
        "Origin": "https://app.getcollectr.com",
        "Pragma": "no-cache",
        "Referer": "https://app.getcollectr.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    # Make the post request
    response = requests.post(url, headers=headers, json = post_body)

    # Check if the request was successful
    if response.status_code == 200:
        print("Card added successfully!")
        print("Response:", response.json())
    else:
        print("Failed to add card.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

    return response

def create_upload_list(original_df, updated_df, card_type_columns = ['Normal', 'Reverse Holofoil', 'Holofoil']):
    upload_list = []
    
    # Iterate through each row in the original dataframe
    for index, row in original_df.iterrows():
        card_id = row['product_id']

        # Get the updated counts for the card
        updated_row = updated_df[updated_df['product_id'] == card_id]
        
        if not updated_row.empty:
            # Compare counts for Normal, Reverse Holofoil, and Holofoil
            for card_type in card_type_columns:
                original_count = row[card_type]
                updated_count = updated_row.iloc[0][card_type]
                
                if original_count != updated_count:
                    upload_list.append({
                        'card_id': card_id,
                        'card_type': card_type,
                        'count': updated_count
                    })
    
    return upload_list

def create_upload_list_from_files(original_file, updated_file):
    import pandas as pd
    
    # Read the original and updated CSV files
    original_df = pd.read_csv(original_file)
    updated_df = pd.read_csv(updated_file)
    
    # Create the upload list
    upload_list = create_upload_list(original_df, updated_df)
    
    return upload_list

# Now we can iterate through the upload list and post each card
def post_upload_list(upload_list, base_url, user_id, collection_id, auth_token, time_between = 0.1):
    error_items = []
    for item in upload_list:
        card_id = item['card_id']
        card_type = item['card_type']
        card_count = int(float(item['count']))
        
        response = post_card(card_id, base_url, user_id, collection_id, card_count, card_type, auth_token)
        # If it fails, log the item to a file
        # Also log the error message
        if response.status_code != 200:
            with open('error_items.json', 'a') as f:
                item['error'] = response.text
                f.write(f"{item}\n")
            error_items.append(item)

        # Wait time_between requests to avoid hitting the API too hard
        import time
        time.sleep(time_between)

    if error_items:
        print(f"Some items failed to post. Check error_items.json for details.")

    return error_items