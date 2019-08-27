import os
import tempfile
import urllib.request
from flask import Flask, flash, request, redirect, render_template, send_file
from werkzeug.utils import secure_filename
from subprocess import Popen

app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = '/tmp'

ALLOWED_EXTENSIONS = set(['pdf'])

ZINE_TEX_SINGLE_SIDED =r"""\documentclass[a4paper,landscape]{article}
\usepackage[margin=0pt]{geometry}
\usepackage{graphicx}
\begin{document}
\includegraphics[page=4,angle=180,width=.24\paperwidth]{pages.pdf}\hfill
\includegraphics[page=3,angle=180,width=.24\paperwidth]{pages.pdf}\hfill
\includegraphics[page=2,angle=180,width=.24\paperwidth]{pages.pdf}\hfill
\includegraphics[page=1,angle=180,width=.24\paperwidth]{pages.pdf}\\
\includegraphics[page=5,angle=0,width=.24\paperwidth]{pages.pdf}\hfill
\includegraphics[page=6,angle=0,width=.24\paperwidth]{pages.pdf}\hfill
\includegraphics[page=7,angle=0,width=.24\paperwidth]{pages.pdf}\hfill
\includegraphics[page=8,angle=0,width=.24\paperwidth]{pages.pdf}\hfill
%\newline
%\includegraphics[page=1,angle=90,width=1\paperwidth]{poster.pdf}\hfill
\end{document}"""

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
	return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			with tempfile.TemporaryDirectory() as tmpdirname:
				print('created temporary directory', tmpdirname)			
				upload_file_name = os.path.join(tmpdirname, 'pages.pdf')				
				tex_file_name = os.path.join(tmpdirname, 'zine.tex')
				zine_file_name = os.path.join(tmpdirname, 'zine.pdf')
				file.save(upload_file_name)
				flash('File successfully uploaded')

				with open(tex_file_name,'w+') as tex_file:
					tex_file.write(ZINE_TEX_SINGLE_SIDED)

				p = Popen(['xelatex',tex_file_name],cwd=tmpdirname)
				p.communicate()

				return send_file(zine_file_name, as_attachment=True, attachment_filename='zine.pdf')
		else:
			flash('Allowed pdf')
			return redirect(request.url)    


if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
