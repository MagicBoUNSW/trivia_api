import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "example"
        self.database_path = 'postgresql://postgres:Welcome1@localhost:5432/example'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        resp = self.client().get('/questions')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_add_a_question(self):
        obj = {
            'question': 'this is a question',
            'answer': 'yes',
            'difficulty': 2,
            'category': 1
        }
        total_questions_1 = len(Question.query.all())
        resp = self.client().post('/questions', json=obj)
        data = json.loads(resp.data)
        total_questions_2 = len(Question.query.all())
        self.assertEqual(resp.status_code, 200)

    def test_delete_a_question(self):
        obj = Question(question='this is a question', answer='no', difficulty=3, category=4)
        obj.insert()
        que_id = obj.id
        resp = self.client().delete(f'/questions/{que_id}')
        data = json.loads(resp.data)
        obj = Question.query.filter(Question.id == obj.id).one_or_none()
        self.assertEqual(resp.status_code, 200) 

    def test_get_questions_not_found(self):
        resp = self.client().get('/questions?page=40')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
