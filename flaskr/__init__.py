import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from database.models import *
from auth.auth import requires_auth
import error_handlers


MAX_RESULTS_PER_PAGE = 10

def paginate_results(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * MAX_RESULTS_PER_PAGE
    end = start + MAX_RESULTS_PER_PAGE
    
    results = [model.format_short() for model in selection]
    current_results = results[start:end]
    
    return current_results

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    app.register_blueprint(error_handlers.blueprint)
    CORS(app)
    
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    

    """
    %%%%%%% ---------- ROUTES ---------- %%%%%%%
    """
    @app.route('/checkifworking')
    #
    def get_greeting():
        return "Application is up and running!"

    '''
    ROUTES:Articles ---------------
    '''
    @app.route('/articles', methods=["GET"])
    # @requires_auth('get:all')
    def get_articles():
        articles = paginate_results(request, Article.query.all())
        
        if not len(articles):
            abort(404)
        
        return jsonify({
            "success": True,
            "articles": articles
        })

    
    @app.route('/articles/<int:article_id>', methods=["GET"])
    def get_article_details(article_id):
        article = Article.query.filter(Article.id == article_id).one_or_none()
        
        if not article:
            abort(404)
            
        return jsonify({
            "success": True,
            "article": article.format()
        })
    
    @app.route('/articles', methods=["POST"])
    @requires_auth('post:articles')
    def create_article(payload):
        body = request.get_json(force=True)
        print(",".join(body.get("tags")))
        try:
            new_article = Article(
                title=body.get("title"),
                publisher_id=body.get("publisher_id"),
                author_id=body.get("author_id"),
                tags=",".join(body.get("tags")),
                article_link=body.get("article_link")
            )
            
            new_article.insert()
            
            return jsonify({
                "success": True,
                "article": new_article.format()
            })
            
        except Exception as e:
            print(e.args)
            abort(422)
            
    
    @app.route('/articles/<int:article_id>', methods=["PATCH"])
    @requires_auth('patch:articles')
    def edit_article(payload,article_id):
        article_to_update = Article.query\
            .filter(Article.id == article_id).one_or_none()

        if not article_to_update:
            abort(404)
        
        body = request.get_json(force=True)
        
        try:   
            article_to_update.title=body.get("title"),
            article_to_update.publisher_id=body.get("publisher_id"),
            article_to_update.author_id=body.get("author_id"),
            article_to_update.tags=",".join(body.get("tags"))
            
            article_to_update.update()
            
            return jsonify({
                "success": True,
                "article": article_to_update.format()
            })
        except:
            abort(422)
            
    @app.route('/articles/<int:article_id>', methods=["DELETE"])
    @requires_auth('delete:articles')
    def delete_article(payload, article_id):
        abort_code = 422
        article_to_delete = Article.query.filter(Article.id == article_id).one_or_none()
        
        if not article_to_delete:
            abort_code = 404
            abort()
        
        try:
            article_to_delete.delete()
            
            return jsonify({
                "success": True,
                "delete": article_id
            })
        
        except:
            abort(abort_code)
        

    '''
    ROUTES:Authors ---------------
    '''
    @app.route('/authors', methods=["GET"])
    def get_authors():
        authors = paginate_results(request, Author.query.all())
        
        if not len(authors):
            abort(404)
        
        return jsonify({
            "success": True,
            "authors": authors
        })
        
    @app.route('/authors/<int:author_id>', methods=["GET"])
    def get_author_details(author_id):
        author = Author.query.filter(Author.id == author_id).one_or_none()
        
        if not author:
            abort(404)

        return jsonify({
            "success": True,
            "author": author.format()
        })
    
    @app.route('/authors', methods=["POST"])
    @requires_auth('post:authors')
    def add_new_author(payload):
        body = request.get_json(force=True)
        
        try:
            new_author = Author(names=body.get("names"),
                                lastname=body.get("lastname"))
            new_author.insert()
            return jsonify({
                "success": True,
                "author": new_author.format()
            })
        except:
            abort(422)
    
    @app.route('/authors/<int:author_id>', methods=["PATCH"])
    @requires_auth('patch:authors')
    def edit_author_details(payload, author_id):
        author_to_update = Author.query.filter(Author.id == author_id).one_or_none()
        if not author_to_update:
            abort(404)
            
        body = request.get_json(force=True)
        if not body:
            abort(422)
        try:
            author_to_update.names = body.get("names")
            author_to_update.lastname = body.get("lastname")
            
            if body.get("article_ids"):
                articles_for_update = [Article.query.filter(Article.id) for id in body.get("article_ids")]
                author_to_update.articles = articles_for_update        
                    
            author_to_update.update()
            
            return jsonify({
                "success": True,
                "author": author_to_update.format()
            })
            
        except:
            abort(422)
    
    @app.route('/authors/<int:author_id>', methods=["DELETE"])
    @requires_auth('delete:authors')
    def delete_author(payload,author_id):
        abort_code = 422
        author_to_delete = Author.query.filter(Author.id == author_id).one_or_none()
        
        if not author_to_delete:
            abort_code = 404
            abort(404)
        
        try:
            author_to_delete.delete()
            
            return jsonify({
                "success": True,
                "delete": author_id
            })
        
        except:
            abort(abort_code)
    
    '''
    ROUTES:Publisher ---------------
    '''
    @app.route('/publishers', methods=["GET"])
    def get_publishers():
        publishers =  paginate_results(request,Publisher.query.all())

        if not len(publishers):
            abort(404)
        
        return jsonify({
            "success": True,
            "publishers": publishers
        })
    
    @app.route('/publishers/<int:publisher_id>', methods=["GET"])
    def get_publisher_details(publisher_id):
        publisher = Publisher.query.filter(Publisher.id == publisher_id).one_or_none()
        
        if not publisher:
            abort(404)
        
        return jsonify({
            "success": True,
            "publisher": publisher.format()
        })

    
    @app.route('/publishers', methods=["POST"])
    @requires_auth('post:publishers')
    def add_new_publisher(payload):
        body = request.get_json(force=True)
        try:
            new_publisher = Publisher(name=body.get("name"),
                                    company_link=body.get("company_link"))
            new_publisher.insert()
            return jsonify({
                "success": True,
                "publisher": new_publisher.format()
            })
            
        except Exception as e:
            print(e.args)
            abort(422)
        
    
    @app.route('/publishers/<int:publisher_id>', methods=["PATCH"])
    @requires_auth('patch:publishers')
    def edit_publisher_details(payload, publisher_id):
        publisher_to_update = Publisher.query.filter(Publisher.id == publisher_id).one_or_none()
        
        if not publisher_to_update:
            abort(404)
        body = request.get_json(force=True)
        
        try:
            publisher_to_update.name = body.get("name")
            publisher_to_update.company_link = body.get("company_link")
            
            if body.get("article_ids"):
                articles_for_update = [Article.query.filter(Article.id) for id in body.get("article_ids")]
                publisher_to_update.articles = articles_for_update        
                    
            publisher_to_update.update()
            
            return jsonify({
                "success": True,
                "publisher": publisher_to_update.format()
            })
            
        except:
            abort(422)
            
    @app.route('/publishers/<int:publisher_id>', methods=["DELETE"])
    @requires_auth('delete:publishers')
    def delete_publisher(payload, publisher_id):
        # abort_code = 422
        publisher_to_delete = Publisher.query.filter(Publisher.id == publisher_id).one_or_none()
        
        if not publisher_to_delete:
            # abort_code = 404
            abort(404)
        
        try:
            publisher_to_delete.delete()
            
            return jsonify({
                "success": True,
                "delete": publisher_id
            })
        
        except:
            abort(422)
 
    """
    %%%%%%% ---------- END ---------- %%%%%%%
    """
    return app

app = create_app()
