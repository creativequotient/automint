import argparse
import subprocess
import os
import pandas as pd

def get_files(dir_path, ext='.png'):
    relative_paths = os.listdir(dir_path)
    relative_paths = list(filter(lambda fp: ext in fp, relative_paths))
    return list(map(lambda rel_p: os.path.join(dir_path, rel_p), relative_paths))

def ipfs_add_local(file_path):
    'Returns CID'
    proc = subprocess.run(['ipfs', 'add', file_path], capture_output=True, text=True)
    stdout = proc.stdout
    return stdout.split()[1]

def pin_with_pinata(cid, name):
    proc = subprocess.run(['ipfs', 'pin', 'remote', 'add', '--service=pinata', f'--name={name}', str(cid)], capture_output=True, text=True)
    print(f'Uploaded cid: {cid}')
    # print(proc.stdout)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch IPFS file uploading')
    parser.add_argument('-i', '--input', help='Path to directory containing media to upload', required=True)
    args = vars(parser.parse_args())

    files_to_upload = get_files(args['input'])

    info = {}

    for fp in files_to_upload:
        print(fp)
        cid = ipfs_add_local(fp)
        name = os.path.basename(fp)
        info[name] = {'cid': cid}

        pin_with_pinata(cid, name)

    with open(f'{args["input"]}/result.csv', 'w') as f:
        for fn in sorted(info.keys()):
            cid = info[fn]['cid']
            f.write(f'{fn}, {cid}\n')

        f.close()
