import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def pagination(page, question_list):
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  question_list = [question.format() for question in question_list]
  limit_questions = question_list[start:end]
  return limit_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  

  # '''
  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  # '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  # '''
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  # '''
  @app.after_request
  def after_request(resp):
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return resp


  @app.route("/hello") 
  def get_greeting():
    return jsonify({'message':'Hello, World!'})
  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests 
  # for all available categories.
  # # '''

  @app.route('/categories')
  def get_categorie_list():
    categorie_list = Category.query.all()
    if len(categorie_list) == 0: abort(404)

    #convert array to object
    categories = {ct.id: ct.type for ct in categorie_list}
    return jsonify({  'categories': categories })



  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests for questions, 
  # including pagination (every 10 questions). 
  # This endpoint should return a list of questions, 
  # number of total questions, current category, categories. 

  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions. 
  # '''

  @app.route('/questions')
  def get_question_list():
    question_list = Question.query.all()
    page = request.args.get('page', 1, type=int)
    categorie_list = Category.query.all()

    if len(question_list) == 0: abort(404)
    if len(categorie_list) == 0: abort(404)

    questions_on_page = pagination(page, question_list)

    return jsonify({ 
      'questions': questions_on_page,
      'total_questions': len(question_list),
      'categories': {cate.id: cate.type for cate in categorie_list}
    })

  # '''
  # @TODO: 
  # Create an endpoint to DELETE question using a question ID. 

  @app.route("/questions/<question_id>", methods=['DELETE'])
  def delete_question_by_id(question_id):
    try:
      question_query = Question.query.get(question_id)
      question_query.delete()
      return jsonify({  'deleted': question_id })
    except:
      print(sys.exc_info())
      abort(422)

  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page. 
  # '''

  # '''
  # @TODO: 
  # Create an endpoint to POST a new question, 
  # which will require the question and answer text, 
  # category, and difficulty score.

  @app.route("/questions", methods=['POST'])
  def create_a_question():
    json = request.get_json()

    question = json.get('question')
    answer = json.get('answer')
    difficulty = json.get('difficulty')
    category = json.get('category')

    try:
      data = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      data.insert()
      return jsonify({ 'created': data.id })
    except: 
      print(sys.exc_info())
      abort(422)

  # TEST: When you submit a question on the "Add" tab, 
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.  
  # '''

  # '''
  # @TODO: 
  # Create a POST endpoint to get questions based on a search term. 
  # It should return any questions for whom the search term 
  # is a substring of the question. 

  @app.route('/questions/search', methods=['POST'])
  def questions_search():
    json = request.get_json()
    search_term = json.get('searchTerm', None)

    if search_term:
      question_list = Question.query.filter( Question.question.ilike(f'%{search_term}%')).all()

      return jsonify({
        'questions': [question.format() for question in question_list],
        'total_questions': len(question_list)
      })
    abort(404)

  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 
  # '''

  # '''
  # @TODO: 
  # Create a GET endpoint to get questions based on category. 

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):

    try:
      question_list = Question.query.filter(Question.category == str(category_id)).all() 
      return jsonify({ 
        'questions': [question.format() for question in question_list],
        'total_questions': len(question_list),
        'current_category': category_id
      })
    except:
      print(sys.exc_info())
      abort(404)

  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  # '''


  # '''
  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 


  @app.route('/quizzes', methods=['POST'])
  def random_question_play_quiz():
    try:
      json = request.get_json() 
      category = json.get('quiz_category')
      pre_question_list = json.get('previous_questions') 

      check = Question.id.notin_(pre_question_list) 
      question_list = Question.query.filter_by(category=category['id']).filter(check).all()

      new_question = None
      if len(question_list) > 0 :
        new_question = question_list[random.randrange(0, len(question_list))].format()

      print(new_question)
      return jsonify({  'question': new_question })
    except:
      print(sys.exc_info())
      abort(422)

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 
  # '''

  # '''
  # @TODO: 
  # Create error handlers for all expected errors 
  # including 404 and 422. 
  # '''

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
            "error": 404,
            "message": "notfound"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
            "error": 422,
            "message": "unprocessable"
      }), 422


  
  return app

    