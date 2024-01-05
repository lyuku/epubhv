import os
from flask import Flask, render_template, request, send_file
# from werkzeug import secure_filename
from pathlib import Path
from epubhv.converter import Language_Converter, Ruby_Converter, To_Horizontal_Converter, To_Vertical_Converter
from epubhv.epub_processer import Epub_Processer

TEMPLATES_AUTO_RELOAD = True

app = Flask(__name__, static_folder='templates')
app.config.from_object(__name__)
# 设置Flask jsonify返回中文不转码
app.config['JSON_AS_ASCII'] = False

if __name__ == '__main__':
    app.run()

# PIC_FOLDER = os.path.join(app.root_path, 'upload_pic')

TO_VERTICAL_CONVERTER = To_Vertical_Converter()
TO_HORIZONTAL_CONVERTER = To_Horizontal_Converter()
LANGUAGE_CONVERTER = Language_Converter()
RUBY_CONVERTER = Ruby_Converter()

TMP_PATH = "/tmp/"

@app.route("/")
def index():
    return render_template('index.html')


@app.route('/file_download', methods=['GET'])
def file_download():
    data = request.args
    if 'filename' in data:
        filename = data.get('filename')
        grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        return send_file(grandparent_dir + os.path.sep + filename, as_attachment=True)
    else:
        return 'error'
        


@app.route('/epub_process', methods=['POST'])
def epubhv():
    print("process start")
    data = request.form
    print(data)
    file = request.files['file']
    print(file.filename)
    need_ruby = False
    actions = []

    # need control process order
    if 'direction' in data:
        if "toVertical" == data['direction']:
            actions.append(TO_VERTICAL_CONVERTER)
        if "toHorizontal" == data['direction']:
            actions.append(TO_HORIZONTAL_CONVERTER)
    if 'ruby' in data:
        if True == data['ruby']:
            need_ruby = True
            actions.append(RUBY_CONVERTER)
    to_lang = None
    if 'convertTo' in data:
        to_lang = data['convertTo']
        actions.append(LANGUAGE_CONVERTER)
        
    path = os.path.join(TMP_PATH, file.filename)
    file.save(path)
    processer : Epub_Processer = Epub_Processer(Path(path), to_lang, need_ruby = need_ruby)
    processer.process(actions)
    out_path = processer.pack()
    print("process finished")

    return {
        "downloadPath": out_path
    }
