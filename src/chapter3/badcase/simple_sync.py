import hashlib
import os
import shutil
from pathlib import Path

BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)

    return hasher.hexdigest()


# source: 원본
# dest: 사본
def sync(source, dest):
    source_hashes = {}
    for folder, _, files in os.walk(source):
        for fn in files:
            source_hashes[hash_file(Path(folder) / fn)] = fn

    seen = set()

    for folder, _, files in os.walk(dest):
        for fn in files:
            dest_path = Path(folder) / fn
            dest_hash = hash_file(dest_path)
            seen.add(dest_hash)

            # 사본에 있지만 원본에 없는 파일을 찾으면 삭제한다.
            if dest_hash not in source_hashes:
                dest_path.remove()

            # 사본에 있는 파일이 원본과 같은 내용이지만 다른 이름이라면
            # 사본 이름을 원본 이름으로 바꾼다.
            elif dest_hash in source_hashes and fn != source_hashes[dest_hash]:
                shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

    # 원본에는 있지만 사본에 없는 모든 파일을 사본으로 복사한다.
    for src_hash, fn in source_hashes.items():
        if src_hash not in seen:
            shutil.copy(Path(source) / fn, Path(dest) / fn)
