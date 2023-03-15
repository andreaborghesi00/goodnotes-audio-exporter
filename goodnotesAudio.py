import os
import zipfile
from zipfile import ZipFile
from pathlib import Path

zip_dir = r'./tmp_zips'
audio_dir = r'./exports'
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
                if file.filename.__contains__("attachments/"):
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
                new_name = str.lower(root_name.replace(" ", "_"))+"_"+str(index)
                os.rename(os.path.join(folder, file), os.path.join(os.path.join(audio_dir, root_name), new_name))

                # change extension from none to .mp4
                p = Path(os.path.join(audio_dir, root_name, new_name))
                p.rename(p.with_suffix(".mp4"))
                index += 1

            # delete dir containing extensionless audio
            os.rmdir(folder)
        # delete zip
        os.remove(os.path.join(zip_dir, zip_file))
    except zipfile.BadZipfile:
        print(zip_file + " was not a zip file")
        continue

print("done")
