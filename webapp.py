# python imports
import os
import create_video
EN_API_KEY = "Z5BUWFNXJP6NGXADB"
VID_HEMAN = "ZZ5LpwO-An4.flv"
VID_SENTINEL = "V1b7sDq0AkI.mp4"
VID_FLASH = "y9he--ojipI.flv"
VID = VID_HEMAN
import logging

logger = logging.getLogger('webapp')
ALLOWED_EXTENSIONS = ['.mp3']

# web stuff and markdown imports
import markdown
from flask import render_template, request, Flask, abort, Response
#from flask import make_response, jsonify, flash, url_for, redirect
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_object('settings')
app.debug = True

MARKDOWN_PARSER = markdown.Markdown(extensions=['fenced_code'], 
                                    output_format="html4", 
                                    safe_mode=True)

logging.basicConfig(level=logging.INFO)

def render_template_catch(*args, **kwargs):
    try:
        return render_template(*args, **kwargs)
    except Exception, e:
        print 'yo there be something wrong with:'
        print 'args %r' % args
        print 'kwargs %r' % kwargs
        print 'exception %r' % e
    abort(404)

@app.route("/")
def index():
    return render_template("main.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/vidify/", methods=["POST"])
def vidify():
    youtube_url = request.form['youtube_url']
    mp3_file = request.files['file']
    print 'youtube_url', youtube_url
    print 'mp3_file', mp3_file
    print 'filename', mp3_file.filename
    #if mp3_file and allowed_file(mp3_file.filename):
    filename = secure_filename(mp3_file.filename)
    print 'filename', filename
    mp3_file.save(os.path.join('/mnt/tdb/mp3s/', filename))
    fn = create_video.create_vid(os.path.join('/mnt/tdb/mp3s/', filename), youtube_url)
    return render_template("final.html", fn=fn)

@app.route("/style.css")
def render_font_style():
    t = render_template_catch("font_style.css",
                            font_name=app.config["FONT_NAME"])
    return Response(t, mimetype="text/css")

if __name__ == "__main__":
    # Listen on all interfaces
    app.run(host="0.0.0.0", port=5000)
