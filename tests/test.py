import os, sys
import string
import random
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import tempfile
import unittest

from app import app



class FlaskTestCase(unittest.TestCase):
    #Some test cases depends upon the data stored in the database

    # Working Test Cases - 28
    
    #The index page test case
    def test_index_page(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type="html/text")
        self.assertIn(b'Corona Archive', response.data)

    
    # The login page test case
    def test_login_hospital_page(self):
        tester = app.test_client(self)
        response = tester.get('/Hospital', content_type="html/text")
        self.assertIn(b'Hospital', response.data)
    
    # The login page test case
    def test_login_visitor_page(self):
        tester = app.test_client(self)
        response = tester.get('/Visitor', content_type="html/text")
        self.assertIn(b'Visitor', response.data)
    
    # The login page test case
    def test_login_agent_page(self):
        tester = app.test_client(self)
        response = tester.get('/Agent', content_type="html/text")
        self.assertIn(b'Agent', response.data)
    
    # The login page test case
    def test_login_place_page(self):
        tester = app.test_client(self)
        response = tester.get('/Place', content_type="html/text")
        self.assertIn(b'Place Login', response.data)
    
    
    #The visitor registration page
    def test_visitor_registration_page(self):
        tester = app.test_client(self)
        response = tester.get('/register', content_type="html/text")
        self.assertIn(b'Register as Visitor', response.data)
    
    #The establishment owner registration page
    def test_place_registration_page(self):
        tester = app.test_client(self)
        response = tester.get('/pregister', content_type="html/text")
        self.assertIn(b'Register your place', response.data)
    
    

    
    #Test for logout page
    def test_logout_page(self):
        tester = app.test_client(self)
        response = tester.get('/logout', content_type="html/text", follow_redirects=True)
        self.assertIn(b'Corona Archive', response.data)



    #Test for visitor login redirection incase of portaling in without session
    def test_login_redirection_visitor_portal(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.get('/Visitor', content_type="html/text", follow_redirects = True)
        self.assertIn(b'Visitor', response.data)
    
    
    #Test for for visitor registration
    def test_visitor_registration(self):
        tester = app.test_client(self)
        response = tester.post('/register', data=dict( 
                    Vorname="qq",
                    email = str(random.randint(0,100))+'@'+str(0), 
                    password = "qq",
                    phone = "qq",
                    address = "qq"), follow_redirects=True)
        self.assertIn(b'You have registered successfully.', response.data)
    

    #Test for place owner registration
    def test__place_registration(self):
        tester = app.test_client(self)
        response = tester.post('/pregister', data=dict( 
                    place_name="qq",
                    email = str(random.randint(0,100))+'@'+str(0), 
                    password = "qq",
                    number = "qq",
                    address = "qq"), follow_redirects=True)
        self.assertIn(b'Corona Archive', response.data)
    
    
    
    #Test for establishment owner login redirection incase of portaling in without session
    def test_login_redirection_place_portal(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.get('/Place', content_type="html/text", follow_redirects=True)
        self.assertIn(b'Place', response.data)
    
    #Test for agent login redirection incase of portaling in without session
    def test_login_redirection_agent_portal(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.get('/Agent', content_type="html/text")
        self.assertIn(b'AGENCY', response.data)
    
    #Test for hospital login redirection incase of portaling in without session
    def test_login_redirection_hospital_portal(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.get('/Hospital', content_type="html/text")
        self.assertIn(b'Hospital', response.data)
    

    #Test for successful login. Here please change the username and password by the avaliable data in the database.
    def test_visitor_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Visitor', data=dict(email="lanji", password="1000"), follow_redirects=True)
        self.assertIn(b'Scan', response.data)

    #test to see if the failures if not given access
    def test_place_login_failure(self):
        testingClient = app.test_client(self)
        response = testingClient.get(
            '/loginPlace', content_type="html/text")
    
    #Test for agent login
    def test_agent_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Agent', data=dict(username="ZERO", password="12345"), follow_redirects=True)
        self.assertIn(b'Agent portal', response.data)

    #Test for hospital login
    def test_hospital_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Hospital', data=dict(id = 100, username="wang", password="what"), follow_redirects=True)
        self.assertIn(b'Hospital portal', response.data)
    
    #Test for place login
    def test_place_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Place', data=dict(email="q", password="q"), follow_redirects=True)
        self.assertIn(b'Place portal', response.data)
    
    #Test for invalid credential login for place
    def test_place_invalid_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Place', data=dict(email="wrong", password="wrong"), follow_redirects=True)
        self.assertIn(b'INVALID CREDENTIALS', response.data)
    
    #Test for invalid credential login for agent
    def test_agent_invalid_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Agent', data=dict(username="wrong", password="wrong"), follow_redirects=True)
        self.assertIn(b'INVALID CREDENTIALS', response.data)
    
    #Test for invalid credential login for hospital
    def test_hospital_invalid_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Hospital', data=dict(id= 100, username="wrong", password="wrong"), follow_redirects=True)
        self.assertIn(b'INVALID CREDENTIALS', response.data)

    #Test for invalid credential login for visitor
    def test_visitor_invalid_login(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/Visitor', data=dict(email="wrong", password="wrong"), follow_redirects=True)
        self.assertIn(b'INVALID CREDENTIALS', response.data)

    #Test for contact tracing
    def test_contact_tracing(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        tester.post('/Agent', data=dict(username="ZERO", password="12345"), follow_redirects=True)
        response = tester.get('/contact-tracing', content_type="html/text")
        self.assertIn(b'All currently positive visitors', response.data)
    
    #test to get the list of all users
    def test_list_of_all_users(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        tester.post('/Agent', data=dict(username="ZERO", password="12345"), follow_redirects=True)
        response = tester.get('/allusers', content_type="html/text")
        self.assertIn(b'List of all Users', response.data)

    #test to get the list of all places
    def test_list_of_all_places(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        tester.post('/Agent', data=dict(username="ZERO", password="12345"), follow_redirects=True)
        response = tester.get('/allplaces', content_type="html/text")
        self.assertIn(b'List of all Places', response.data)
    
    #test to get the list of all hospitals
    def test_list_of_all_hospitals(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        tester.post('/Agent', data=dict(username="ZERO", password="12345"), follow_redirects=True)
        response = tester.get('/allhospitals', content_type="html/text")
        self.assertIn(b'List of all hospitals', response.data)

    #test to see if the hospital can the accept/reject request or not 
    def hospital_request(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        response = tester.post('/HospitalRegister', data=dict(id = "10", username=str(random.randint(0,10000)), password="q"), follow_redirects=True)
        self.assertIn(b'Corona Archive', response.data)

    #test for showing requests for agent
    def test_agent_request_showing(self):
        tester = app.test_client(self)
        tester.get('/logout', content_type="html/text")
        id_a = str(random.randint(0,10000))
        tester.post('/HospitalRegister', data=dict(id = id_a, username= 'q', password="q"), follow_redirects=True)
        tester.get('/logout', content_type="html/text")
        tester.post('/Agent', data=dict(username="ZERO", password="12345"), follow_redirects=True)
        response = tester.get('/hospital_request', content_type="html/text")
        self.assertIn(bytes(id_a, 'utf-8'), response.data)
    
    
    
if __name__=='__main__':
   unittest.main()