# Laptop Service
import flask
import csv
import json
from flask import Flask, Response, request
from flask_restful import Resource, Api, reqparse
import logging
import pymongo
from pymongo import MongoClient
from base64 import b64decode
from bson.objectid import ObjectId
from password import hash_password, verify_password
from testToken import generate_auth_token, verify_auth_token, token_required


# Instantiate the app
app = flask.Flask(__name__)
api = Api(app)


client = MongoClient('db', 27017)
db = client.tododb
collection = db.control


# Resources 
# ====================
class ListAll (Resource):
	@token_required
	def get(self,top = None):
		top = request.args.get('top', 0, type=int)
		if top is not 0:
			record = getAll(top,True,True)
		else:
			record = getAll(None,True,False)
		return flask.jsonify(result= record)


class ListOpenOnly (Resource):
	@token_required
	def get(self):

		top = request.args.get('top', 0, type=int)
		if top is not 0:
			record = getAll(top,True,False,sortField = "open_time")  
		else:
			record = getAll(None,True,False,sortField = "open_time")        
		return flask.jsonify(result= record)



class ListClosedOnly (Resource):
	@token_required
	def get(self):
		top = request.args.get('top', 0, type=int)

		if top is not 0:
			record = getAll(top,False,True,sortField = "close_time")
		else:
			record = getAll(None,False,True)
		return flask.jsonify(result= record)

class listAllcsv(Resource):
	@token_required
	def get(self):
		top = request.args.get('top', 0, type=int)
		if top is not 0:
			record = getAll(top,True,True)
		else:   
			record = getAll(None,True,True)
		json2csv(record,True,True)
		csvfile = open('data.csv', 'r')
		return Response(csvfile, mimetype='text/csv')


class listOpenOnlycsv(Resource):
	@token_required
	def get(self,):
		top = request.args.get('top', 0, type=int)

		if top is not 0:
			record = getAll(top,True,False,sortField = "open_time")
		else:
			record = getAll(None,True,False,sortField = "open_time")

		json2csv(record,True,False)
		csvfile = open('data.csv', 'r')
		return Response(csvfile, mimetype='text/csv')

class listCloseOnlycsv(Resource):
	@token_required
	def get(self,top = None):
		top = request.args.get('top', 0, type=int)

		if top is not 0:
			record = getAll(top,False,True,sortField = "close_time")
		else:
			record = getAll(None,False,True,sortField = "close_time")
		json2csv(record,False,True)
		csvfile = open('data.csv', 'r')
		return Response(csvfile, mimetype='text/csv')

# Authorization
#===================


class registerUser(Resource):
	def post(self):
		# Get fields
		parser = reqparse.RequestParser()
		parser.add_argument('username', required=True, help="username cannot be blank!")
		parser.add_argument('password', required=True, help="password cannot be blank")
		args = parser.parse_args()

		username = args['username']
		password = args['password']

		# Check for empty arguments
		if username == None or password == None:
			return {"client error":"bad request"}, 400

		# Check for duplicate username
		if collection.users.find_one({"username":username}) != None:
			return {"client error":"username already exists"}, 418
		# Hash password
		hashedpass = hash_password(password)
		# throw away password data
		password = None

		# Insert into database
		post_id = collection.users.insert_one({"username":username,"password":hashedpass})
		userId = str(post_id.inserted_id)

		# Success
		return {"success":"created","username":username,"location":userId}, 201

class getToken(Resource):
	def get(self):
		# Check for correct user fields
		authheader = request.headers.get("Authorization")
		if authheader == None:
			return {"Unauthorized":"No Authorization header found"}, 401

		# Get user credentials
		credentials = authheader.split(' ')
		decode_creds = b64decode(credentials[1]).decode()
		user = decode_creds.split(':')
		username = user[0]
		password = user[1]
		
		# Find user in database
		document = collection.users.find_one({"username":username})
		if document == None:
			return {"Unauthorized":"user not found"}, 401

		# Check password
		if not verify_password(password, document['password']):
			return {"Unauthorized":"wrong password"}, 401

		# Generate token
		token = generate_auth_token(expiration=1000)
		return {"token":token.decode(), "duration":1000}, 200



# Create routes
api.add_resource(ListAll,'/listAll','/listAll/json')
api.add_resource(ListOpenOnly, '/listOpenOnly','/listOpenOnly/json')
api.add_resource(ListClosedOnly, '/listCloseOnly','/listCLoseOnly/json')
api.add_resource(listAllcsv, '/listAll/csv')
api.add_resource(listOpenOnlycsv, '/listOpenOnly/csv')
api.add_resource(listCloseOnlycsv, '/listCloseOnly/csv')
api.add_resource(registerUser, '/api/register')
api.add_resource(getToken, '/api/token')


#  functions: 
# ===========================
def getAll(top,isOpen,isClose,sortField = None):
	limit = 20
	sortStr = "open_time"
	if top is not None:
		limit = top
	if sortField is not None:
		sortStr = sortField

	allTimes = collection.find().sort(sortStr, pymongo.ASCENDING).limit(int(limit))
	result = []
	for entry in allTimes:
		if isOpen and isClose:
			result.append({
				'open': entry['open_time'],
				'close': entry['close_time'],
				'km': entry['km']
				})
		elif isOpen:
			result.append({
				'open': entry['open_time'],
				'km': entry['km']
				})
		else:
			result.append({
				'close': entry['close_time'],
				'km': entry['km']
				})
	app.logger.debug(result)
	return result

def json2csv(jsonObj,ifOpen,ifClose):
	obj = jsonObj
	csvfile = open('data.csv', 'w')
	out = csv.writer(csvfile)

	if ifOpen and ifClose:
		out.writerow(['km','open','close'])
		for x in obj:
			out.writerow([x['km'],
					x['open'],
					x['close']])
	elif ifOpen:
		out.writerow(['km','open'])
		for x in obj:
			out.writerow([x['km'],
					x['open']])
	else:
		out.writerow(['km','close'])
		for x in obj:
			out.writerow([x['km'],
					x['close']])    

# Run the application
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)
