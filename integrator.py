from google.cloud import storage

import os
import time
import text2voice
import subprocess
import pipes

from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

####

from flask import Flask, session
from flask_session import Session

from flask import send_file, send_from_directory, safe_join, abort

HOST = 'rjcaste_stanford_gmail_com@34.82.17.115'

UPLOAD_FOLDER = "/Users/rodrigo.castellon/Desktop/pdfFolder"
#W_UPLOAD_FOLDER = "/Users/rodrigo.castellon/Desktop/wavFolder"
P_ALLOWED_EXTENSIONS = ['pdf']
M_ALLOWED_EXTENSIONS = ['wav']
FILENAME = ""
W_FILENAME = ""


app = Flask(__name__)
# Check Configuration section for more details
SESSION_TYPE = 'redis'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config.from_object(__name__)

import secrets
seckey = secrets.token_urlsafe(16)
app.config['SECRET_KEY'] = seckey
Session(app)


@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

####


#app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename, type):
    if type == 'pdf':
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in P_ALLOWED_EXTENSIONS
    elif type == "wav":
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in M_ALLOWED_EXTENSIONS



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # clear the buckets out before we start
    os.system('gsutil rm gs://txts/*')
    os.system('gsutil rm gs://wavs_5/*')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'pdffile' not in request.files and 'wavfile' not in request.files:
            return redirect(request.url)
        pfile = request.files['pdffile']
        wfile = request.files['wavfile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if pfile.filename == '' and wfile.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if pfile and allowed_file(pfile.filename,'pdf'):
            filename = secure_filename(pfile.filename)
            pfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            global FILENAME
            FILENAME = filename
            FILEPATH = "{}/{}".format(UPLOAD_FOLDER, FILENAME)
            command = "gsutil cp {} gs://original_pdfs_5/".format(FILEPATH)
            os.system(command)
            input = "gs://original_pdfs_5/%s" % FILENAME
            output = "gs://pdf2text_5/%s" % FILENAME[0:-3]
            cool = text2voice.pdftovoice(input, output)
            with open('input.txt', 'w') as f:
                f.write(cool)
            #createTxt(cool,FILENAME)


            #nombre = "input.txt"


            command1_5 = "gsutil cp {} gs://txts/".format("/Users/rodrigo.castellon/Desktop/misc/text2anime/input.txt")
            os.system(command1_5)
            #resetTxt(nombre)
            outputmp3path = "/Users/rodrigo.castellon/Desktop/misc/text2anime/output.mp3"
            command2 = "gsutil cp {} gs://mp3s_5/".format(outputmp3path)
            os.system(command2)
        if wfile and allowed_file(wfile.filename,'wav'):
            filename = secure_filename(wfile.filename)
            wfile.save(os.path.join(app.config['UPLOAD_FOLDER'], "input.wav")) # used to be filename
            global W_FILENAME
            W_FILENAME = filename


            path = "{}/{}".format(UPLOAD_FOLDER, "input.wav")


            wcommand = "gsutil cp {} gs://wavs_5/".format(path)
            os.system(wcommand)

        time.sleep(10)
        outPutReturn()

        os.system('gsutil rm gs://txts/*')
        os.system('gsutil rm gs://wavs_5/*')



            #return redirect(url_for('uploaded_file', filename=filename))

    return '''
    <!doctype html>
    <head>
    <link rel="stylesheet" href="styles.css" type="text/css">
    <style>.center {margin: auto; width: 40%; padding: 10px;} </style>
    </head>
    <body>
    <div class="everything">
    <div class="center" id="outer">
    <div style="float: left">
      <img src="https://imgur.com/5AyVYk5.png" style="width:100px;height:100px;" class="center">
      </div>
    <h1 class="center">EduVoicer</h1>

    <div class="center">
    <form method=post enctype=multipart/form-data><br>
      <label for="pdf">PDF file: </label>
      <input type=file name=pdffile id=pdf><br><br>
      <label for="wav">WAV file: </label>
      <input type=file name=wavfile id=wav><br><br>
      <input type=submit value=Upload>
    </form>
    </div>
    </div>
    </div>
    </body>
    

    '''
app.config["OUPUT"] = "/Users/rodrigo.castellon/Desktop/outputs/"
@app.route("/get-wav/<wav_name>")
def get_wav(wav_name):
    print("ASDFASDFASDFASDFASDF")
    print(wav_name)
    try:
        return send_from_directory(app.config["OUTPUT"], filename=wav_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)

def outPutReturn():
    while(True):
        # check whether output.wav is at its designated location in VM
        global HOST
        if exists_remote(HOST, '/home/rjcaste_stanford_gmail_com/Real-Time-Voice-Cloning/output.wav'):
            break

    print('SCP-ing output.wav from remote machine to local machine')
    google2local('/home/rjcaste_stanford_gmail_com/Real-Time-Voice-Cloning/output.wav', "/Users/rodrigo.castellon/Desktop/outputs/output.wav")

def delete_in_bucket(name):
    '''
    Deletes everything in bucket `name`
    '''
    os.system('gsutil rm gs://{}/*'.format(name))

def google2local(remote_path, local_path):
    '''
    Fetch a file at `remote_path` on the remote VM and
    place at `local_path` in the local machine.
    '''
    cmd = 'scp rjcaste_stanford_gmail_com@34.82.17.115:{} {}'.format(remote_path, local_path)
    os.system(cmd)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )

def exists_remote(host, path):
    """Test if a file exists at path on a host accessible with SSH."""
    status = subprocess.call(
        ['ssh', host, 'test -f {}'.format(pipes.quote(path))])
    if status == 0:
        return True
    if status == 1:
        return False
    raise Exception('SSH failed')

def contains_file(name):
    '''
    Checks bucket `name` and returns True if the bucket has something
    and False if the bucket has nothing
    '''
    cmd = 'gsutil ls -l gs://{}'.format(name)
    try:
        out = subprocess.check_output(cmd.split(' '))
    except:
        print('invalid file')
    else:
        return out != 0


def resetTxt(nombre):
    open(nombre, 'w').close()
    os.rename(nombre,"container.txt")

def createTxt(text,name):
    file1 = open("container.txt", "a")
    file1.write(text)
    os.rename("container.txt","input.txt")

print("REEEEE    &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
print(FILENAME)
from flask import send_from_directory

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     a = send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)
#     return a


def runboi():

    app.run(debug=True)
    #return FILENAME

#runboi()



# print("LOOKH HERE")
# print(file)
# a.append(file)
# print('definitely should not happen twice')


runboi()












# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     """Uploads a file to the bucket."""
#     # bucket_name = "your-bucket-name"
#     # source_file_name = "local/path/to/file"
#     # destination_blob_name = "storage-object-name"
#
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
#
#     blob.upload_from_filename(source_file_name)
#
#     print(
#         "File {} uploaded to {}.".format(
#             source_file_name, destination_blob_name
#         )
#     )
#
# #main
# print(file)
# print(FILEPATH)
# upload_blob("gs://original_pdfs_5", FILEPATH, file)
