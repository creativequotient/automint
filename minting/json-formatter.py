import json
import copy
import csv


def get_token_info(token_csv_path):
    token_data = {}

    with open(token_csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            #assume columns are: name, edition, info_name, ipfs_url
            token_name, rarity, info_name, ipfs_url, maximum_supply, attributes_str  = row[0], row[1], row[2], row[3], int(row[4]), row[5]
            token = {"name": token_name,
                     "rarity": rarity,
                     "info_name": info_name,
                     "ipfs_url": ipfs_url,
                     "max_supply": maximum_supply,
                     "attributes_str": attributes_str}
            token_data[token_name] = token

        csv_file.close()

    return token_data


def format_trait_list(attributes_str, edition, max_supply, rarity, max_rarity):
    attributes_str = attributes_str.replace('rarity', f'Rarity {rarity}')
    attributes_str = attributes_str.replace('edition', f'Edition {edition}')
    attributes = attributes_str.split('-')
    return attributes


def make_token_json(metadata_code, policy, max_rarity, collection_name, token_info):
    output = {
        metadata_code: {
            policy: {

            }
        }
    }

    pointer = output[metadata_code][policy]

    for i in range(1,token_info['max_supply'] + 1):

        #jleveille1337 - get NAME, INFO_IMAGE, INFO_NAME from the CSV file
        token_name = token_info['name'] + '%02d' % i
        info_name = token_info['info_name']
        ipfs_url = token_info['ipfs_url']
        attributes = format_trait_list(token_info['attributes_str'], i, token_info['max_supply'], token_info['rarity'], max_rarity)

        nft = {"image": ipfs_url, "name": info_name, "collection": collection_name, "attributes": attributes}

        pointer.update({token_name: nft})

    return output


if __name__ == '__main__':
    METADATA_CODE = "721"
    POLICY = "270235444667eaa14939b0b9d0c4cb16d1304fe1e401adb57a8b33d0"
    COLLECTION_NAME = "Non-Fungible Waveforms Collection 0"

    token_data  = get_token_info('token_input.csv')

    COLLECTION_SIZE = len(token_data) # this controls the y value in "Rarity x/y"

    for token in token_data:
        mint_info = make_token_json(METADATA_CODE, POLICY, COLLECTION_SIZE, COLLECTION_NAME, token_data[token])

        #jleveille - changed output file name to match the collection
        with open(token + ".json", "w") as outfile:
            json.dump(mint_info, outfile, indent=4)
