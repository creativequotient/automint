import argparse
import subprocess
import os


def get_files(dir_path, ext='.png'):
    relative_paths = os.listdir(dir_path)
    relative_paths = list(filter(lambda fp: ext in fp, relative_paths))
    return list(map(lambda rel_p: os.path.join(dir_path, rel_p), relative_paths))


def ipfs_add_local(file_path):
    'Returns CID'
    proc = subprocess.run(['ipfs', 'add', file_path], capture_output=True, text=True)
    stdout = proc.stdout
    try:
        return stdout.split()[1]
    except IndexError as e:
        print(e)
        print(stdout)
        return ""


def pin_with_pinata(cid, name):
    proc = subprocess.run(['ipfs', 'pin', 'remote', 'add', '--service=pinata', f'--name={name}', str(cid)], capture_output=True, text=True, timeout=20)
    print(f'Uploaded cid: {cid}')
    # print(proc.stdout)
    if proc.stderr != "":
        print(f'Error encountered when uploading to pinata for {name} with cid {cid}')
        print(proc.stderr)
        return False
    return True


def proc(fp):
    name = os.path.basename(fp)
    cid = ipfs_add_local(fp)
    if cid == "":
        print(f'{fp} failed to upload!')
        return ""
    while True:
        successfully_pinned = pin_with_pinata(cid, name)
        if successfully_pinned:
            break
    return cid


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch IPFS file uploading')
    parser.add_argument('-i', '--input', help='Path to directory containing media to upload', required=True)
    args = vars(parser.parse_args())

    files_to_upload = sorted(get_files(args['input']))

    info = {}

    for fp in files_to_upload:
        print(fp)
        cid = ipfs_add_local(fp)
        if cid == "":
            print(f'{fp} failed to upload!')
            continue
        name = os.path.basename(fp)
        info[name] = {'cid': cid}

        pin_with_pinata(cid, name)

    with open(f'{args["input"]}/result.csv', 'w') as f:
        for fn in sorted(info.keys()):
            cid = info[fn]['cid']
            f.write(f'{fn}, {cid}\n')

        f.close()
