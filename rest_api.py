import json
import bottle
from bottle import route, run, request, abort, install
from pymongo import Connection
import bottle_mysql


connection = Connection('localhost',27017)
mongo = connection.shirts
@route('/')
def hello():
    return "Please specify a specific route!"

#mongoDB
@route('/shirt/:shirtId')
def singleShirt(shirtId):
	entity = mongo['shirts'].find_one({'shirtId':shirtId})

	if not entity:
		abort(404, 'No shirt with id %s' % shirtId)
	entity.pop('_id', None)
	return entity

@route('/shirts', method = 'PUT')
def updateShirt():
	data = request.body.read()
	if not data:
		abort(400, 'No data received')

	entity = json.loads(data)
	if not entity.has_key('shirtId'):
		abort(400, 'No shirtId specified')
	
	existed = mongo['shirts'].find_one({'shirtId':entity.get('shirtId')})
	if not existed:
		abort(404, 'This doesn\'t exists')

	mongo['shirts'].update({'shirtId':entity.get('shirtId')},{"$set": entity},upsert=False)
	return entity


@route('/shirts', method = 'POST')
def addShirt():
	data = request.body.read()
	if not data:
		abort(400, 'No data received')

	entity = json.loads(data)
	if not entity.has_key('shirtId'):
		abort(400, 'No shirtId specified')

	existed = mongo['shirts'].find_one({'shirtId':entity.get('shirtId')})
	if existed:
		abort(409, 'This shirt exists')

	mongo['shirts'].save(entity)
	return data


@route('/shirts', method = 'DELETE')
def deleteShirt():
	data = request.body.read()
	if not data:
		abort(400, 'No data received')

	entity = json.loads(data)
	if not entity.has_key('shirtId'):
		abort(400, 'No shirtId specified')

	existed = mongo['shirts'].find_one({'shirtId':entity.get('shirtId')})
	if not existed:
		abort(404, 'This shirt doesn\'t exist')

	mongo['shirts'].remove({'shirtId':entity.get('shirtId')})


#Mysql database
plugin = bottle_mysql.Plugin(dbuser='root', dbpass='mysql', dbname='assignment3')
install(plugin)
@route('/shoe/:shoeId')
def singleShoe(shoeId,db):
	db.execute('SELECT * FROM shoes WHERE shoe_id="%s"', (int(shoeId),))
	row = db.fetchone()
	if not row:
		abort(404, 'No shoe found !')
	return row


@route('/shoes', method = 'PUT')
def updateShoe(db):
	data = request.body.read()
	if not data:
		abort(400, 'No data received')

	entity = json.loads(data)
	if not entity.has_key('shoeId'):
		abort(400, 'No shoeId specified')

	db.execute('SELECT * FROM shoes WHERE shoe_id="%s"', (int(entity.get('shoeId')),))
	row = db.fetchone()
	if not row:
		abort(404, 'No shoe found!')

	db.execute('UPDATE shoes SET shoe_name=%s, shoe_quantity=%s, created_by=%s WHERE shoe_id=%s', (entity.get('shoeName'),int(entity.get('shoeQuantity')),entity.get('createdBy'),int(entity.get('shoeId'))),)

	return data;
@route('/shoes', method = 'POST')
def addShoe(db):
	data = request.body.read()
	if not data:
		abort(400, 'No data received')

	entity = json.loads(data)
	if not entity.has_key('shoeId'):
		abort(400, 'No shoeId specified')

	db.execute('SELECT * FROM shoes WHERE shoe_id="%s"', (int(entity.get('shoeId')),))
	row = db.fetchone()
	if row:
		abort(409, 'This shoe already exists')

	db.execute("INSERT INTO shoes(shoe_id, shoe_name, shoe_quantity, created_by) VALUES (%s, %s, %s, %s)",(int(entity.get('shoeId')),entity.get('shoeName'),int(entity.get('shoeQuantity')),entity.get('createdBy')))
	return data;

@route('/shoes', method = 'DELETE')
def deleteShoe(db):
	data = request.body.read()
	if not data:
		abort(400, 'No data received')

	entity = json.loads(data)
	if not entity.has_key('shoeId'):
		abort(400, 'No shoeId specified, Please specify one')

	db.execute('SELECT * FROM shoes WHERE shoe_id="%s"', (int(entity.get('shoeId')),))
	row = db.fetchone()
	if not row:
		abort(404, 'No shoe is found')
	db.execute('DELETE FROM shoes WHERE shoe_id="%s"',(int(entity.get('shoeId')),))


run(server='cherrypy', host='0.0.0.0', port=8080)
