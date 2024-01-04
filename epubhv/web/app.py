import os
from flask import Flask, render_template, request, jsonify
from werkzeug import secure_filename
from pathlib import Path
from epubhv.converter import Language_Converter, Ruby_Converter, To_Horizontal_Converter, To_Vertical_Converter
from epubhv.epub_processer import Epub_Processer

TEMPLATES_AUTO_RELOAD = True

app = Flask(__name__)
app.config.from_object(__name__)
# 设置Flask jsonify返回中文不转码
app.config['JSON_AS_ASCII'] = False

PIC_FOLDER = os.path.join(app.root_path, 'upload_pic')

TO_VERTICAL_CONVERTER = To_Vertical_Converter()
TO_HORIZONTAL_CONVERTER = To_Horizontal_Converter()
LANGUAGE_CONVERTER = Language_Converter()
RUBY_CONVERTER = Ruby_Converter()

TMP_PATH = "/tmp/"

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# TODO not tested
@app.route('/epub_process', methods=['POST'])
def epubhv():
    data = request.form
    file = request.files['file']
    actions_str = data['actions']
    to_lang = data['to_lang']
    actions = []
    need_ruby = False
    # need control process order
    if "toVertical" in actions_str:
        actions.append(TO_VERTICAL_CONVERTER)
    elif "toHorizontal" in actions_str:
        actions.append(TO_HORIZONTAL_CONVERTER)
    if to_lang:
        actions.append(LANGUAGE_CONVERTER)
    if "ruby" in actions_str:
        need_ruby = True
        actions.append(RUBY_CONVERTER)
    path = os.path.join(TMP_PATH, file.filename)
    file.save(path)
    processer : Epub_Processer = Epub_Processer(Path(path), to_lang, need_ruby = need_ruby)
    processer.process(actions)
    out_path = processer.pack()

    return jsonify({
        "download_path": out_path
    })
