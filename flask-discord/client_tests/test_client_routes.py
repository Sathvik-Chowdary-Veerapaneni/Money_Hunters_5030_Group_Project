from cgi import test
import sqlite3
import unittest
from urllib import response
import pytest
from flaskd.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash


def test_home_route_fail(app):
        #can't access home page before authentication need to return false 302 
        with app.test_client() as test_client:
                response = test_client.get('/')
                assert response.status_code == 302
                
def test_auth_login_page(app):
        #need to access auth/login page 
        with app.test_client() as test_client:
                response=test_client.get('/auth/login')
                assert response.status_code==200

def test_user_logout_page(app):
        #user can't use logout page before login need to return false code 302
        with app.test_client() as test_client:
                response=test_client.get('/logout')
                assert response.status_code==302
