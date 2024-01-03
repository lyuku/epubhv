
import logging
import os
import shutil
import zipfile
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional


from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, PageElement, ResultSet, Tag
from cssutils import CSSParser
from cssutils.css import CSSStyleSheet




WRITING_KEY_LIST: List[str] = [
    "writing-mode",
    "-webkit-writing-mode",
    "-epub-writing-mode",
]
V_ITEM_TO_ADD_IN_MANIFEST: str = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)
V_STYLE_LINE: str = (
    '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
)
V_STYLE_LINE_IN_OPF: str = '<meta content="vertical-rl" name="primary-writing-mode"/>'

class Converter:
  
    def process_css(self):
        # do nothing
        print('convert_css')

    def process_content(self):
        # do nothing
        print('process_spine')

    def process_opf(self):
        # do nothing
        print('process_opf')
    
    def no_css(self):
        # do nothing
        print('generate_css')


class To_Vertical_Converter(Converter):
    
    def __init__(self) -> None:
        super().__init__()
        self._need_update_manifest = False
  
    def process_css(self, css_string):
        parser: CSSParser = CSSParser()
        css_sheet: CSSStyleSheet = parser.parseString(css_string)
        has_html_or_body: bool = False
        for s in css_sheet.cssRules.rulesOfType(1):  # type: ignore
            if s.selectorText == "html":  # type: ignore
                has_html_or_body = True
                for w in WRITING_KEY_LIST:
                    if w not in s.style.keys():  # type: ignore
                        # set it to vertical
                        s.style[w] = "vertical-rl"  # type: ignore
        if not has_html_or_body:
            css_sheet.add(  # type: ignore
                """
                html {
                    -epub-writing-mode: vertical-rl;
                    writing-mode: vertical-rl;
                    -webkit-writing-mode: vertical-rl;
                }
                """
            )
        return css_sheet.cssText.decode('utf-8')

    def process_opf(self, soup):
        spine: Optional[Tag | NavigableString] = soup.find("spine")
        assert spine is not None
        if spine.attrs.get("page-progression-direction", "") != "rtl":  # type: ignore
            spine.attrs["page-progression-direction"] = "rtl"  # type: ignore
        meta_list: ResultSet[Tag] = soup.find_all("meta")
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                m.attrs["content"] = "vertical-rl"
        else:
            meta_list.append(bs(V_STYLE_LINE_IN_OPF, "xml").contents[0])  # type: ignore
        if self._need_update_manifest == True:
            # add css item to manifest items
            soup.find_all("manifest")[0].append(
                bs(V_ITEM_TO_ADD_IN_MANIFEST, "xml").contents[0]
            )
        return str(soup)

    def no_css(self, opf_dir):
        print("no_css")
        # if we have no css file in the epub than we create one.
        style_path: Path = Path(opf_dir) / Path("Style")
        if not style_path.exists():
            os.mkdir(style_path)
        new_css_file: Path = style_path / Path("style.css")
        with open(new_css_file, "w", encoding="utf-8", errors="ignore") as file:
            file.write(
                """
@charset "utf-8";
html {
-epub-writing-mode: vertical-rl;
writing-mode: vertical-rl;
-webkit-writing-mode: vertical-rl;
}
                    """
            )
        self._need_update_manifest = True
    
    def _add_stylesheet_to_html(self, soup: bs):
        # Find the head section or create if not present
        head: Optional[Tag | NavigableString] = soup.find("head")
        if not head or type(head) is NavigableString:
            head = soup.new_tag("head")  # type: ignore
            soup.html.insert(0, head)  # type: ignore
        # Add the stylesheet line inside the head section
        head.append(bs(V_STYLE_LINE, "html.parser").contents[0])
    
    def process_content(self, content):
        if self._need_update_manifest == False:
            return content
        soup: bs = bs(content, "html.parser")
        self._add_stylesheet_to_html(self, soup)
        return str(soup)
    
    

class To_Horizontal_Converter:
  
    def process_css(self):
        print('convert_css')

    def process_opf(self):
        print('process_opf')

    def process_html(self):
        print('process_html')

