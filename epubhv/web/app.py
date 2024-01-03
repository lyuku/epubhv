import os
from flask import Flask, render_template, request, jsonify
from werkzeug import secure_filename
from pathlib import Path
from epubhv.converter import To_Horizontal_Converter, To_Vertical_Converter
from epubhv.epub_processer import Epub_Processer

TEMPLATES_AUTO_RELOAD = True

app = Flask(__name__)
app.config.from_object(__name__)
# 设置Flask jsonify返回中文不转码
app.config['JSON_AS_ASCII'] = False

PIC_FOLDER = os.path.join(app.root_path, 'upload_pic')


CONVERTER_MAP = {"toVertical":To_Vertical_Converter(), "toVertical": To_Horizontal_Converter()}
TMP_PATH = "/tmp/"
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/epub_process', methods=['POST'])
def epubhv():
    data = request.form
    file = request.files['file']
    actions_str = data['actions']
    result = {'actions': data['toVertical']}
    actions = []
    for str in actions_str:
        if str in CONVERTER_MAP:
            actions.append(CONVERTER_MAP[str])
    path = os.path.join(TMP_PATH, file.filename)
    file.save(path)
    processer : Epub_Processer = Epub_Processer(Path(path))
    processer.process(actions)
    out_path = processer.pack(TMP_PATH)

    return jsonify({
        "url": out_path
    })
