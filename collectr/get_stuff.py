from collectr.auth import get_token

def get_cards_in_set(base_url, offset, limit, auth_token, groupid, filters = "cards"):
    # Should look like this: https://api-2.getcollectr.com/catalog?offset=30&limit=30&filters=cards&groupId=24073
    import requests
    import json

    url = f"{base_url}?offset={offset}&limit={limit}&filters={filters}&groupId={groupid}"

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

    # Make the get request
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        print("Cards retrieved successfully!")
        # print("Response:", response.json())
    else:
        print("Failed to retrieve cards.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

    return response.json()

def get_my_collection_info(base_url, user_id, collection_id, auth_token, cards):
    # cards is a vector of ids
    import requests
    import json
    url = f"{base_url}{user_id}/products?collectionId={collection_id}&productIds="
    # Convert the list of ids to a comma separated string
    product_ids = ','.join(map(str, cards))
    # Add the product ids to the url
    url += product_ids

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

    # Make the get request
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        print("Cards retrieved successfully!")
        # print("Response:", response.json())
    else:
        print("Failed to retrieve cards.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

    return response.json()

def get_ids(cards):
    ids = []
    for card in cards['data']:
        ids.append(card['product_id'])
    return ids

def create_base_df(cards):
    # If a card doesn't have a product_sub_type put a - in the cell
    import pandas as pd
    import csv
    # Find out the unique product_sub_types
    # They are contained in cards['data'][element]['unique_sub_type_groups'][element]['product_sub_type']
    # Create a list of the unique product_sub_types
    all_sub_types = []
    for card in cards['data']:
        for sub_type in card['unique_sub_type_groups']:
            if sub_type['product_sub_type'] not in all_sub_types:
                all_sub_types.append(sub_type['product_sub_type'])

    # Create a dataframe with the columns
    columns = ['product_id', 'product_name', 'card_number', 'set', 'set_id', 'rarity'] + all_sub_types
    df = pd.DataFrame(columns=columns)
    # Create a dictionary with the columns
    data = {}
    for column in columns:
        data[column] = []
    # Loop through the cards and add the data to the dictionary
    for card in cards['data']:
        data['product_id'].append(card['product_id'])
        data['product_name'].append(card['product_name'])
        data['card_number'].append(card['card_number'])
        data['set'].append(card['catalog_group'])
        data['set_id'].append(card['catalog_group_id'])
        data['rarity'].append(card['rarity'])
        # Extract sub types
        card_sub_types = []
        for sub_type in card['unique_sub_type_groups']:
            card_sub_types.append(sub_type['product_sub_type'])
        # Loop through the unique_sub_type_groups and add the quantities to the dictionary
        
        for sub_type in all_sub_types:
            if sub_type in card_sub_types:
                data[sub_type].append(0)
            else:
                data[sub_type].append('X')

    # Add the data to the dataframe
    for column in columns:
        df[column] = data[column]

    return df

def add_quantities_to_csv(my_info, filename = 'cards.csv'):
    import pandas as pd
    # Read the csv file
    df = pd.read_csv(filename)
    # Loop through the my_info and add the quantities to the dataframe
    for card in my_info['data']:
        # Get the product_id
        product_id = card['product_id']
        # Get the product_sub_type
        product_sub_type = card['product_sub_type']
        # Get the quantity
        quantity = card['quantity']
        # Find the row in the dataframe with the product_id
        row = df[df['product_id'] == product_id]
        # If the row exists, add the quantity to the column with the product_sub_type
        if not row.empty:
            df.loc[row.index[0], product_sub_type] = quantity

    # # Write the dataframe to a csv file
    # df.to_csv(filename, index=False)
    return df

def get_card_info_from_product_id(base_url, product_id, collection_id, auth_token):
    # Endpoint looks like this:    
    import requests
    import json
    url = f"{base_url}{collection_id}/products/{product_id}?collectionId={collection_id}&currency=USD&details=false"

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

    # Make the get request
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        print("Cards retrieved successfully!")
        # print("Response:", response.json())
    else:
        print("Failed to retrieve cards.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

    return response.json()

def get_card_counts_from_card_info(card_info):
    card_count = {}
    for sub_type in card_info['data']['ungraded_sub_types']:
        sub_type_name = sub_type['product_sub_type']
        card_count[sub_type_name] = sub_type['quantity']
    return card_count

def get_card_counts_from_product_ids(base_url, product_ids, collection_id, auth_token, sleep_time = 0.1):
    import time
    # Create a dictionary to hold the counts
    counts = {}
    # Loop through the product_ids and get the count for each one
    for product_id in product_ids:
        # Initialize the dictionary for this product_id
        counts[product_id] = {}
        card_info = get_card_info_from_product_id(base_url, product_id, collection_id, auth_token)
        # Count is in ['data']['ungraded_sub_types'][element]['quantity']
        # Get card count from card_info
        card_count = get_card_counts_from_card_info(card_info)
        # Add the counts to the dictionary
        for sub_type, count in card_count.items():
            counts[product_id][sub_type] = count
        # Sleep for sleep_time seconds to avoid hitting the API too hard
        time.sleep(sleep_time)

    # Return the counts
    return counts

def create_base_csv_for_group(groupid, filename = None):
    # Get the cards in the set
    cards = get_cards_in_set("https://api-2.getcollectr.com/catalog", offset = 0, limit = 3000, groupid = groupid, auth_token = get_token())
    # If no filename is provided, get the group name from the cards and use it as the filename
    if filename is None:
        # Get the group name from the first card
        group_name = cards['data'][0]['catalog_group']
        # Replace spaces with underscores and convert to lowercase
        filename = f"{group_name.lower().replace(' ', '_')}_cards.csv"
        print(f"No filename provided. Using {filename} as the default filename.")
    # Create the base csv, only if it doesn't already exist
    import os
    if os.path.exists(filename):
        print(f"{filename} already exists. Not creating a new file.")
        return filename
    
    df = create_base_df(cards)
    # Save the dataframe to a csv file
    df.to_csv(filename, index=False)
    print(f"Base CSV created: {filename}")
    return filename

def get_my_card_count_for_file(filename, userid, collectionid, auth_token):
    import pandas as pd
    # Read the csv file
    df = pd.read_csv(filename)
    # Get the product_ids from the product_id column
    product_ids = df['product_id'].tolist()

    collection_info = get_my_collection_info("https://api-2.getcollectr.com/collections/", userid, collectionid, auth_token, product_ids)
    # Get the ids from the collection_info
    my_ids = get_ids(collection_info)
    my_card_counts = get_card_counts_from_product_ids("https://api-2.getcollectr.com/collections/", my_ids, collectionid, get_token())

    df = pd.DataFrame(my_card_counts).T
    # Change index to product_id
    df.index.name = 'product_id'

    return df

def merge_card_counts_with_base_csv(base_csv, card_counts_df):
    import pandas as pd
    # Read the base csv
    base_df = pd.read_csv(base_csv)
    # Replace the values in the base_df with the values from card_counts_df
    card_counts_df_copy = card_counts_df.copy()

    # Ensure product_id is of type str for both dataframes to avoid alignment issues
    base_df['product_id'] = base_df['product_id'].astype(str)
    # card_counts_df_copy['product_id'] = card_counts_df_copy['product_id'].astype(str)

    # Set index to product_id for easy alignment
    df_left_indexed = base_df.set_index('product_id')
    card_counts_df_copy.index = card_counts_df_copy.index.astype(str)  # Ensure index is of type str
    # card_counts_df_copy = card_counts_df_copy.set_index('product_id')

    df_left_indexed.update(card_counts_df_copy)

    # Reset index if needed
    df_merged = df_left_indexed.reset_index()
    
    return df_merged
    
def main():
    pass

if __name__ == "__main__":
    main()