import json
import logging

logger = logging.getLogger(__name__)


def validate_metadata(metadata_fp, tokens, policy_id):
    # Load metadata
    with open(metadata_fp, 'r') as f:
        metadata = json.load(f)
        f.close()

    # Check '721'
    if len(metadata) != 1:
        raise Exception('Metadata file should only have 1 "type" attribute')

    if '721' not in metadata:
        raise Exception('Metadata should contain "721" key not found')

    # Check policy_id
    if len(metadata['721']) != 1:
        raise Exception('Metadata should contain only 1 policy ID')


    if policy_id not in metadata['721']:
        found_policy_id = list(metadata['721'].keys())[0]
        raise Exception(f'Metadata contains policy ID {found_policy_id} which does not match {policy_id}')

    # Check tokens
    if len(metadata['721'][policy_id]) != len(tokens):
        raise Exception('Metadata contains more/less tokens than the expected number')

    for token in metadata['721'][policy_id]:
        if token not in tokens:
            raise Exception(f'Unexpected token {token} in metadata found')

        if 'name' not in metadata['721'][policy_id][token]:
            raise Exception(f'"name" attribute not found in metadata for token {token}')

        if 'image' not in metadata['721'][policy_id][token]:
            raise Exception(f'"image" attribute not found in metadata for token {token}')

    return True
