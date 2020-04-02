from zipfile import ZipFile
from os.path import join, dirname
from pathlib import Path
import os
import asyncio
from datetime import datetime
import sys

STARTED_AT = datetime.now().strftime('%d-%m-%Y %H-%M-%S')
DIRECTORIES = []
ARCHIVES = []

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


async def exclude_fonts_from_archive(archive_name):
    """Deletes fonts from ARCHIVES"""
    zin = ZipFile(join(application_path, f"{archive_name}"), "r")

    if any("font" in s for s in zin.namelist()):
        zout = ZipFile(join(application_path, "NO CUSTOM FONTS",
                            f"{archive_name[:-4]} (Edited at {STARTED_AT}).zip"), 'w')

        for item in zin.infolist():
            buffer = zin.read(item.filename)

            if ('font' not in item.filename):
                zout.writestr(item, buffer)

        zout.close()

    zin.close()


async def main():
    path = Path(join(application_path, "NO CUSTOM FONTS"))
    path.mkdir(parents=True, exist_ok=True)

    # Walks through all the files in current scripts folder
    # _ is root, d is dirs, f is files
    for _, d, f in os.walk("."):
        for dir_ in d:
            DIRECTORIES.append(dir_)

        for filename in f:
            if filename.endswith(".zip") or filename.endswith(".rar"):
                ARCHIVES.append(filename)

    for archive in ARCHIVES:
        asyncio.ensure_future(exclude_fonts_from_archive(archive))
        print(f"{archive} now being processed.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
