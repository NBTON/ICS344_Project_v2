import requests

# Register user 'testuser' with no password
url_register = 'http://localhost:5000/api/register'
data_register = {'username': 'testuser'}
response_register = requests.post(url_register, json=data_register)
print('Register response:', response_register.status_code, response_register.json())

# Login with 'testuser' with no password
url_login = 'http://localhost:5000/api/login'
data_login = {'username': 'testuser'}
response_login = requests.post(url_login, json=data_login)
print('Login response:', response_login.status_code, response_login.json())