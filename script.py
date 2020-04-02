from os.path import join, dirname
from datetime import datetime
from zipfile import ZipFile
from pathlib import Path

import platform
import ctypes
import locale
import os
import asyncio
import sys

STARTED_AT = datetime.now().strftime('%d-%m-%Y %H-%M-%S')
DIRECTORIES = []
ARCHIVES = []

WINDLL = ctypes.windll.kernel32 \
    if platform.system() == "Windows" else None

LOCALE = locale.windows_locale[WINDLL.GetUserDefaultUILanguage()] \
    if WINDLL is not None else "en_US"


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


async def exclude_fonts_from_archive(archive_path, archive_name):
    """Deletes fonts from ARCHIVES"""
    zin = ZipFile(join(archive_path), "r")

    if any("font" in s for s in zin.namelist()):
        zout = ZipFile(join(application_path, "NO CUSTOM FONTS",
                            f"{archive_name[:-4]} - NO CUSTOM FONTS (Edited at {STARTED_AT}).zip"), 'w')

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
    # d is root, dirs is dirs, files is files
    for d, dirs, files in os.walk("."):

        for dir_ in dirs:
            DIRECTORIES.append(dir_)

        for filename in files:
            path = join(d, filename)

            if (filename.endswith(".zip") or filename.endswith(".rar")) \
                    and "NO CUSTOM FONTS" not in str(path) \
                    and "NO CUSTOM FONTS" not in filename:
                ARCHIVES.append((filename, path))

    if len(ARCHIVES) <= 0:
        return print(
            "Файлов для обработки не найдено." if LOCALE in ("ru_RU", "uk_UA")
            else "Nothing will get processed, since no packs were found"
        )

    print(
        "Файлы, которые будут подвергнуты обработке:" if LOCALE in ("ru_RU", "uk_UA")
        else "Files that will be processed:"
    )

    for archive, _ in ARCHIVES:
        print(f"- {archive}")

    IS_USER_SURE = input(
        "\nВы уверены, что хотите обработать выше указанные файлы? (да / нет): " if LOCALE in ("ru_RU", "uk_UA")
        else "\nAre you sure that you want to process these files? (yes / no): "
    )

    print("")

    if IS_USER_SURE.lower() not in ("yes", "y", "да"):
        return

    for archive, archive_path in ARCHIVES:
        asyncio.ensure_future(
            exclude_fonts_from_archive(archive_path, archive)
        )

        print(
            f"* {archive} обрабатывается..." if LOCALE in ("ru_RU", "uk_UA")
            else f"* {archive} being processed..."
        )


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
