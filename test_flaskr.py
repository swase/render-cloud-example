import copy
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from flaskr import create_app
from database.models import *

class CapstoneTestCase(unittest.TestCase):
    """This class represents the Capstone Project test case"""
    
    """
    Utility methods to be used to make testing easier
    """
    def print_test_data_ids(self):
        print("Test Author id: {}".format(self.test_author_id))
        print("Test Publisher id: {}".format(self.test_publisher_id))
        print("Test Article id: {}".format(self.test_article_id))
    
    def create_test_author(self):
        new_author = Author(names=self.test_author.get("names"),
                            lastname=self.test_author.get("lastname"))
        new_author.insert()
        self.test_author_id = new_author.id
            
    
    def create_test_publisher(self):
        new_publisher = Publisher(name=self.test_publisher.get("name"),
                                company_link=self.test_publisher.get("company_link"))
        new_publisher.insert()
        self.test_publisher_id = new_publisher.id
        
        
    def create_test_article(self):
        new_article = Article(
                title=self.test_article.get("title"),
                publisher_id=self.test_publisher_id,
                author_id=self.test_author_id,
                tags=",".join(self.test_article.get("tags")),
                article_link=self.test_article.get("article_link")
            )
            
        new_article.insert()
        self.test_article_id = new_article.id
        
    def init_test_data(self):
        self.create_test_author()
        self.create_test_publisher()
        self.create_test_article()
        
    def set_authorisation_header(self, token):
        self.headers.update({"Authorization":  f'Bearer {token}'})
        
    """Test Data"""
    #
    valid_tokens ={}
    valid_tokens["team_lead"]=os.environ.get('TEAM_LEAD_TOKEN')
    valid_tokens["team_member"]=os.environ.get('TEAM_MEMBER_TOKEN')
    # self.test_author = { "names": "Joseph", "lastname": "Addison"}
    test_author = { "names": "Firstname 2ndName", "lastname": "TestLastName"}

    # self.test_publisher = { "name": "Penguin Books", "company_link": "www.penguin-books.com"}
    test_publisher = { "name": "Test Company", "company_link": "www.test-company.com"}

    test_article = {
        "title": "Test Article Title",
        "article_link": "www.test-link-to-article.com",
        "tags": ["poem", "top-rated", "popular"],
        # "publisher_id": 1,
        # "author_id": 1
    }
    
    
    """
    Set up Tear down
    """
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.app_context().push()
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}
        
        user = os.environ.get('DB_USER_TEST')
        password = os.environ.get('DB_PASSWORD_TEST')
        self.database_name = os.environ.get('TABLE_NAME_TEST')
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            user, password, "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)
        self.init_test_data()
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()    
    
    def tearDown(self):
        #check for any created dummy data and delete
        db.session.remove() # Throws errors for ephemeral objects if not used
        created_authors = Author.query.filter(
            Author.names== self.test_author.get("names")).all()
        if len(created_authors) > 0:
            for author in created_authors:
                author.delete()
        
        created_publishers = Publisher.query.filter(
            Publisher.name == self.test_publisher.get("name")).all()
        if len(created_publishers) > 0:
            for publisher in created_publishers:
                publisher.delete()
                
        created_articles = Article.query.filter(
            Article.title == self.test_article.get("title")).all()
        if len(created_articles) > 0:
            for article in created_articles:
                article.delete()
                
    '''
    Tests Start - Author tests
    '''
        
    def test_get_authors(self):
        result = self.client.get("/authors")
        data = json.loads(result.data)
        
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["authors"]))
    
    def test_404_paginated_articles_OOB(self):
        result = self.client.get("/articles?page=9999")
        data = json.loads(result.data)
        
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["message"], "resource not found")
        self.assertEqual(data["error"], 404)
                   
    
    def test_delete_author_valid_token_team_lead(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.delete("/authors/{}".format(self.test_author_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(Author.query.filter(
            Author.id == self.test_author_id).one_or_none())
        
    def test_delete_author_valid_token_team_member_not_enough_permissions(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_member"))
        result = self.client.delete("/authors/{}".format(self.test_author_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 403)
        self.assertEqual(data["message"]["description"], "Permission not in JWT")
        self.assertEqual(data["message"]["code"], "invalid_claims")
        
    def test_delete_author_no_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("")
        result = self.client.delete("/authors/{}".format(self.test_author_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Token not found.")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_delete_author_invalid_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("token")
        result = self.client.delete("/authors/{}".format(self.test_author_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Authorization header must be bearer token. Incorrect token format")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_patch_author_valid_token_team_lead(self):
        # Insert dummy data incase
        # # self.init_test_data()
        copy_of_test_author = copy.deepcopy(self.test_author)
        copy_of_test_author["lastname"] = "test change in name"
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.patch("/authors/{}".format(self.test_author_id),
                                    headers=self.headers,
                                    json=copy_of_test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 200)
        self.assertIsNotNone(Author.query.filter(
            Author.id == self.test_author_id).one_or_none())
        self.assertEqual((Author.query.filter(
            Author.id == self.test_author_id).one_or_none()).lastname, "test change in name")
        
    def test_patch_author_valid_token_invalid_request_body(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.patch("/authors/{}".format(self.test_author_id),
                                    headers=self.headers,
                                    json={"something": "incorrect"})
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")
        
        
        
    def test_patch_author_no_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("")
        result = self.client.delete("/authors/{}".format(self.test_author_id),
                                    headers=self.headers,
                                    json=self.test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Token not found.")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_patch_author_invalid_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("token")
        result = self.client.delete("/authors/{}".format(self.test_author_id),
                                    headers=self.headers,
                                    json=self.test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Authorization header must be bearer token. Incorrect token format")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    '''
    Tests for Publisher
    '''
        
        
    def test_get_publishers(self):
        result = self.client.get("/publishers")
        data = json.loads(result.data)
        
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["publishers"]))
        
    def test_get_publishers_404(self):
        result = self.client.get("/publishers?page=999")
        data = json.loads(result.data)
        
        self.assertEqual(result.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")
                   
    
    def test_delete_publisher_valid_token_team_lead(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.delete("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(Publisher.query.filter(
            Publisher.id == self.test_publisher_id).one_or_none())
        
    def test_delete_publisher_valid_token_team_member_not_enough_permissions(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_member"))
        result = self.client.delete("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 403)
        self.assertEqual(data["message"]["description"], "Permission not in JWT")
        self.assertEqual(data["message"]["code"], "invalid_claims")
        
    def test_delete_publisher_no_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("")
        result = self.client.delete("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Token not found.")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_delete_author_invalid_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("token")
        result = self.client.delete("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Authorization header must be bearer token. Incorrect token format")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_patch_publisher_valid_token_team_lead(self):
        # Insert dummy data incase
        # # self.init_test_data()
        copy_of_test_publisher = copy.deepcopy(self.test_publisher)
        copy_of_test_publisher["name"] = "test change in name"
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.patch("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers,
                                    json=copy_of_test_publisher)
        data = json.loads(result.data)
        # print(data)
        # print(f'Test publisher id: {self.test_publisher_id}')
        self.assertEqual(result.status_code, 200)
        self.assertIsNotNone(Publisher.query.filter(
            Publisher.id == self.test_publisher_id).one_or_none())
        self.assertEqual((Publisher.query.filter(
            Publisher.id == self.test_publisher_id).one_or_none()).name, "test change in name")
        
    def test_patch_publisher_valid_token_invalid_request_body(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.patch("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers,
                                    json={"something": "incorrect"})
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")
        
        
        
    def test_patch_publisher_no_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("")
        result = self.client.delete("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers,
                                    json=self.test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Token not found.")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_patch_publisher_invalid_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("token")
        result = self.client.delete("/publishers/{}".format(self.test_publisher_id),
                                    headers=self.headers,
                                    json=self.test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Authorization header must be bearer token. Incorrect token format")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    '''
    Tests for Articles
    '''
    
    def test_get_paginated_articles(self):
        result = self.client.get("/articles")
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["articles"]))
        
    def test_404_paginated_articles_OOB(self):
        result = self.client.get("/articles?page=9999")
        data = json.loads(result.data)
        
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["message"], "resource not found")
        self.assertEqual(data["error"], 404)
        
    def test_delete_article_valid_token_team_lead(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.delete("/articles/{}".format(self.test_article_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(Article.query.filter(
            Article.id == self.test_article_id).one_or_none())
        
    def test_delete_article_valid_token_team_member_not_enough_permissions(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_member"))
        result = self.client.delete("/articles/{}".format(self.test_article_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 403)
        self.assertEqual(data["message"]["description"], "Permission not in JWT")
        self.assertEqual(data["message"]["code"], "invalid_claims")
        
    def test_delete_article_no_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("")
        result = self.client.delete("/articles/{}".format(self.test_article_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Token not found.")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_delete_article_invalid_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("token")
        result = self.client.delete("/articles/{}".format(self.test_article_id),
                                    headers=self.headers)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Authorization header must be bearer token. Incorrect token format")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_patch_article_valid_token_team_lead(self):
        # Insert dummy data incase
        # # self.init_test_data()
        copy_of_test_article = copy.deepcopy(self.test_article)
        copy_of_test_article["title"] = "test change in title"
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.patch("/articles/{}".format(self.test_article_id),
                                    headers=self.headers,
                                    json=copy_of_test_article)
        data = json.loads(result.data)
        # print(data)
        # print(f'Test publisher id: {self.test_publisher_id}')
        self.assertEqual(result.status_code, 200)
        self.assertIsNotNone(Article.query.filter(
            Article.id == self.test_article_id).one_or_none())
        self.assertEqual((Article.query.filter(
            Article.id == self.test_article_id).one_or_none()).title, "test change in title")
        
    def test_patch_article_valid_token_team_member(self):
        # Insert dummy data incase
        # # self.init_test_data()
        copy_of_test_article = copy.deepcopy(self.test_article)
        copy_of_test_article["title"] = "test change in title"
        self.set_authorisation_header(self.valid_tokens.get("team_member"))
        result = self.client.patch("/articles/{}".format(self.test_article_id),
                                    headers=self.headers,
                                    json=copy_of_test_article)
        data = json.loads(result.data)
        # print(data)
        # print(f'Test publisher id: {self.test_publisher_id}')
        self.assertEqual(result.status_code, 200)
        self.assertIsNotNone(Article.query.filter(
            Article.id == self.test_article_id).one_or_none())
        self.assertEqual((Article.query.filter(
            Article.id == self.test_article_id).one_or_none()).title, "test change in title")
        
    def test_patch_article_valid_token_invalid_request_body(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header(self.valid_tokens.get("team_lead"))
        result = self.client.patch("/articles/{}".format(self.test_article_id),
                                    headers=self.headers,
                                    json={"something": "incorrect"})
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")
        
        
        
        
        
    def test_patch_article_no_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("")
        result = self.client.delete("/articles/{}".format(self.test_article_id),
                                    headers=self.headers,
                                    json=self.test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Token not found.")
        self.assertEqual(data["message"]["code"], "invalid_header")
        
    def test_patch_article_invalid_auth_token(self):
        # Insert dummy data incase
        # # self.init_test_data()
        self.set_authorisation_header("token")
        result = self.client.delete("/articles/{}".format(self.test_article_id),
                                    headers=self.headers,
                                    json=self.test_author)
        data = json.loads(result.data)
        # print(data)
        
        self.assertEqual(result.status_code, 401)
        self.assertEqual(data["message"]["description"], "Authorization header must be bearer token. Incorrect token format")
        self.assertEqual(data["message"]["code"], "invalid_header")
    
    """ End Of Tests """
        
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()