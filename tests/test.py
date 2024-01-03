import os
from pathlib import Path
import pytest
from epubhv.epub_processer import Epub_Processer
from epubhv.converter import To_Vertical_Converter
import time

from epubhv.epubhv import (
    EPUBHV,
    Punctuation,
    list_all_epub_in_dir,
    make_epub_files_dict,
)


def test_ruby() -> None:
    start = time.time()*1000
    lemo_output = Path("animal_farm_output.epub")
    lemo_output.unlink(True)
    # f: EPUBHV = EPUBHV(Path("tests/test_epub/animal_farm.epub"))
    # f.run()
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/animal_farm.epub"))
    processer.process([To_Vertical_Converter()])
    processer.pack()
    print(f"total time:{time.time()*1000 - start}")
    assert lemo_output.exists()
    lemo_output.unlink(True)

