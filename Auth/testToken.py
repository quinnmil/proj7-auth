from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)

from flask import requests
import flask
import time

# initialization
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'

def generate_auth_token(expiration=600):
   # s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
   s = Serializer('test1234@#$', expires_in=expiration)
   # pass index of user
   return s.dumps({'id': 1})

def verify_auth_token(token):
    s = Serializer('test1234@#$')
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"

    
def token_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    message = None
    authHeader = request.headers.get("Authorization")
    if authHeader == None:
      message = "No HTTP"
    else:
      try:
        authMode, authString = authHeader.split(" ", 1)
      except ValueError:
        message = "Bad auth string"
    if message != None:
      return {"message":message}, 401
    userPass = b64decode(authString)
    try:
      theToken, password = userPass.decode().split(":", 1)
    except ValueError:
      message = "Bad auth string"
    if message != None:
      return flask.jsonify({"message":message}), 401

    if verify_auth_token(theToken):
      return f(*args, **kwargs)
    else:
      return {"message":"bad token"}, 401
  return decorated_function

# if __name__ == "__main__":
#     t = generate_auth_token(10)
#     for i in range(1, 20):
# 	print verify_auth_token(t)
#         time.sleep(1)
