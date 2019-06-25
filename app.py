import os
import acronym as _acronym
from flask import Flask, request, jsonify, json
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_cors_headers(response):
   response.headers['Access-Control-Allow-Origin'] = '*'
   if request.method == 'OPTIONS':
      response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
      headers = request.headers.get('Access-Control-Request-Headers')
      if headers:
         response.headers['Access-Control-Allow-Headers'] = headers
   return response
    
app.after_request(add_cors_headers)

def uploadFile(fileType):
   if fileType not in request.files:
      return None
   file = request.files[fileType]

   if file.filename == '':
      return None

   if file and allowed_file(file.filename):
      print("file type is allowed")
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return filename
   else:
      return None


def sendResponse(data, msg, status):
   return jsonify(data = data, msg = msg, status = status)


@app.route('/api/corpus',methods = ['POST'])
def createCorpus():
   if request.method == 'POST':
     uploadedFile = uploadFile('text-file')
     if(uploadedFile != None):
        data = _acronym.accroymFinder(uploadedFile)
        return sendResponse(data, "Created Corpus", "success")
     else:
        return sendResponse(None, "Error Creating Corpus", "error")


@app.route('/api/acronyms',methods = ['POST'])
def postAcronyms():
   if request.method == 'POST':
     uploadedFile = uploadFile('resume-file')
     if(uploadedFile != None):
        data = _acronym.getAccroyms(uploadedFile)
        return sendResponse(data, "fetched acronyms", "success")
     else:
        return sendResponse(None, "Error getting acronyms", "error")


@app.route('/api/acronyms',methods = ['GET'])
def getAcronyms():
   if request.method == 'GET':
      data = _acronym.getAllAcronyms()
      return sendResponse(data, "", "")

@app.route('/api/acronymFullForm/<acronym>',methods = ['GET'])
def getAcronymFullForm(acronym):
   if request.method == 'GET':
      data = _acronym.getAcronymFullForm(acronym)
      return sendResponse(data, "fetched full form", "success")


if __name__ == '__main__':
    app.run(debug=True)
    