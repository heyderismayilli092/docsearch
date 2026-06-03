#!/usr/bin/env python3

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "docsearch.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/docsearch.mo"]))
    return mo


changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = "0.0.1"
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
    ("/usr/bin", ["docsearch"]),

    ("/usr/share/applications",
     ["opensf90.docsearch.desktop"]),

    ("/usr/share/docsearch/ui",
     ["ui/MainWindow.glade"]),

    ("/usr/share/docsearch/src",
     ["src/main.py",
      "src/docsearch_function.py",
      "src/docsearch.py",
      "src/docextract.py",
      "src/docdatabase.py"]),

    ("/usr/share/icons/hicolor/scalable/apps/",
     ["docsearch.png"])
] + create_mo_files()

setup(
    name="docsearch",
    version=version,
    packages=find_packages(),
    scripts=["docsearch"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Heydar Ismayilli",
    author_email="heyderismayilli092@gmail.com",
    description="A search application that provides quick access to the documents and text files you want on your computer by searching their contents",
    license="GPLv3",
    keywords="docsearch, documents, files, pdf, txt, docx, word",
    url="https://github.com/heyderismayilli092/docsearch",
)

