from flask import Flask, request, jsonify, render_template,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from dotenv import load_dotenv
import os

app = Flask(__name__)

APP_ROOT = os.path.dirname(__file__)   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

app.config.from_object(os.getenv('APP_SETTINGS'))
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Question

@app.route("/", methods=['GET'])
def get():
  return "<h1>Team Tomato welcome you</h1>"

# Handles Large File Size Error
@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File size should not exceed 2MB', 413

@app.route("/api/v1/question/add", methods=['POST'])
def add_question():

  # Location of the Question paper
  qp_path = APP_ROOT + "/public/"

  # Details of the Question paper
  subjectName = request.form['subjectName']
  shortForm = request.form['shortForm']
  staff = request.form['staff']
  year = int(request.form['year'])


  # Question paper upload
  nf = request.files['file']
  nf.save(qp_path + nf.filename)

  url =qp_path + nf.filename

  try:
    question=Question(
        subjectName = subjectName,
        shortForm = shortForm,
        staff = staff,
        year = year,
        url = url
    )
    db.session.add(question)
    db.session.commit()
    res = {
      'id': question.id,
      'subjectName': question.subjectName,
      'shortForm': question.shortForm,
      'staff': question.staff,
      'year': question.year,
      'url': question.url
    }
    return jsonify(res)
  except Exception as e:
    return str(e)

@app.route("/api/v1/question", methods=['GET'])
def get_all_questions():
    try:
      questions = Question.query.all()
      return  jsonify([e.serialize() for e in questions])
    except Exception as e:
	    return(str(e))

@app.route("/api/v1/question/<id_>", methods=['GET'])
def get_question_by_id(id_):
    try:
      question = Question.query.filter_by(id=id_).first()
      return jsonify(question.serialize())
    except Exception as e:
	    return(str(e))

@app.route("/api/v1/question/search", methods=['GET'])
def search_question():
    try:
      search_str = "%"+request.args.get('search_str')+"%"
      questions = Question.query.filter(or_(Question.subjectName.ilike(search_str), Question.staff.ilike(search_str), Question.shortForm.ilike(search_str)))
      print(questions)
      return  jsonify([e.serialize() for e in questions])
    except Exception as e:
	    return(str(e))

@app.route('/download/<int:id_>')
def get_question_by_id(id_):
  try:
    file=Question.query.filter_by(id=id_).first()
    return send_file(file.url,attachment_filename='qp.pdf',as_attachment=True)
  except Exception as e:
    return str(e)

if __name__ == '__main__':
    app.run()