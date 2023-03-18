import os
import sys
import ffmpeg
import zipfile
import shutil
from zipfile import ZipFile
from pathlib import Path
from pprint import pprint
from datetime import datetime


def parse_prefix(line, fmt):
    try:
        t = datetime.strptime(line, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            line = line[:-(len(v.args[0]) - 26)]
            t = datetime.strptime(line, fmt)
        else:
            raise
    return t.strftime('%m-%d_%H-%M')


zip_dir = r'.\tmp_zips'
audio_dir = r'.\exports'
SIZE_LBOUND = 200000

# change extension to .goodnotes exports
for file in os.listdir(zip_dir):
    p = Path(os.path.join(zip_dir, file))
    if p.suffix == ".goodnotes":
        p.rename(p.with_suffix('.zip'))

for zip_file in os.listdir(zip_dir):
    # try open zip
    try:
        with ZipFile(os.path.join(zip_dir, zip_file), 'r') as zObject:
            # make output dir
            p = Path(zObject.filename)
            root_name = p.name.removesuffix(".zip")
            os.mkdir(os.path.join(audio_dir, root_name))

            # unzip audio to output dir
            for file in zObject.filelist:
                if "attachments/" in file.filename:
                    zObject.extract(file, os.path.join(audio_dir, root_name))
            zObject.close()

            index = 1
            folder = os.path.join(audio_dir, root_name, "attachments")
            for file in os.listdir(folder):
                # skip small files (likely not to be an audio or simply a useful one)
                if os.path.getsize(os.path.join(folder, file)) < SIZE_LBOUND:
                    print("removing: " + os.path.join(folder, file))
                    os.remove(os.path.join(folder, file))
                    continue

                # move audio out of useless dir
                # os.rename(file, file+".mp4")
                p = Path(file)
                os.rename(os.path.join(folder,file), os.path.join(folder,file+".mp4"))
                try:
                    creation_date = parse_prefix(ffmpeg.probe(os.path.join(folder,file+".mp4"))["format"]["tags"]["creation_time"], '%Y-%m-%dT%H:%M:%S')
                except ffmpeg._run.Error as e:
                    print(e)
                    continue

                new_name = str.lower(root_name.replace(" ", "_"))+"_"+creation_date+".mp4"
                new_path = os.path.join(audio_dir, root_name, new_name)

                    # index = 1
                    # while new_path in os.listdir(folder):
                    #
                # try:
                os.rename(os.path.join(folder, file+".mp4"), new_path)
                # except:
                #     os.rename(os.path.join(folder, file+".mp4"), os.path.join(audio_dir, root_name, str.lower(root_name.replace(" ", "_"))+"_"+creation_date+"_pt2.mp4"))
                index += 1
            # delete emptied dir containing extensionless
            os.rmdir(folder)

        # delete zip - DESTRUCTIVE
        # os.remove(os.path.join(zip_dir, zip_file))
    except zipfile.BadZipfile:
        print(zip_file + " was not a zip file")
        continue

print("done")

