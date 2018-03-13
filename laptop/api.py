# Laptop Service
import flask
import csv
import json
from flask import Flask, Response, request
from flask_restful import Resource, Api
import logging
import pymongo
from pymongo import MongoClient
from base64 import b64decode
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



# Create routes
api.add_resource(ListAll,'/listAll','/listAll/json')
api.add_resource(ListOpenOnly, '/listOpenOnly','/listOpenOnly/json')
api.add_resource(ListClosedOnly, '/listCloseOnly','/listCLoseOnly/json')
api.add_resource(listAllcsv, '/listAll/csv')
api.add_resource(listOpenOnlycsv, '/listOpenOnly/csv')
api.add_resource(listCloseOnlycsv, '/listCloseOnly/csv')


# Authorization
#===================

@app.route("/api/register", methods = ["POST"])
def Register():
	username = request.form.get("user_name")
	unhashedpass = request.form.get("password")
	if username == None or unhashedpass == None:
		return flask.jsonify({"message":"bad request"}), 400
	if db.users.find_one({"user_name":username}) != None:
		return flask.jsonify({"message":"Username already exists"})
	hashedpass = hash_password(unhashedpass)
	result = db.users.insert_one({"user_name":username,"password":hashedpass})
	if result.acknowledged != True:
		return flask.jsonify({"message":"Database error"}), 400
	return flask.jsonify({"message":"created","username":username}), 201,
	{"Location":"/api/users/" + str(username)}

@app.route("/api/token")
def getToken():
	message = None
	authHeader = request.headers.get("Authorization")
	if authHeader == None:
		message = "No http auth header field"
	else:
		try:
			authMode, authString = authHeader.split(" ", 1)
		except ValueError:
			message = "bad auth string"

	if message != None:
		return flask.jsonify({"message":message}), 401

	userPass = b64decode(authString)
	try:
		user, password = userPass.decode().split(":", 1)
	except ValueError:
		message = "bad auth string"

	if message != None:
		return flask.jsonify({"message":message}), 401

	app.logger.debug("Looking up " + str(user))

	DBUser = db.users.find_one({"user_name":user})
	if DBUser == None:
		return flask.jsonify({"message":"User is not registered"}), 401

	if not verify_password(password, DBUser['password']):
		return flask.jsonify({"message":"Wrong password"}), 401
	
	newToken = generate_auth_token(expiration=1000)
	return flask.jsonify({"token":newToken.decode(), "duration":1000}), 200

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
