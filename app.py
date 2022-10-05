from flask import Flask, request, redirect, Response
import pymysql.cursors
import json
import os
from flask_swagger_ui import get_swaggerui_blueprint
import time
import atexit
from prometheus_flask_exporter import PrometheusMetrics
# import random
# import requests


# AVAILABLE_PATHS = [
#   "/api/v1/book",
#   f"/api/v1/book/{random.randint(0, 9999)}",
#     "/api/v1/book/title",
#     "/api/v1/book/author",
#     "/api/v1/swagger/"
# ]

app = Flask(__name__)
metrics = PrometheusMetrics(app)


metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

### swagger specific ###
SWAGGER_URL = '/api/v1/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Niclas-REST-API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT)
### end swagger specific ###

#added because of too many connections error
connected = False
while connected == False:
  try:

    db_connection = pymysql.connect(
        host=os.environ.get("DBHOST"),
        user=os.environ.get("DBUSERNAME"),
        password=os.environ.get("DBPASSWORD"),
        db=os.environ.get("DBNAME"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
  except pymysql.err.OperationalError as e:
    print(e)
    print("Retrying to connect in 30 seconds")
    time.sleep(30)
    continue
  connected = True
  print("Connection Successful")


if connected:
  # initializes the DB cursor
  db_cursor = db_connection.cursor()

  def exit_handler():
    db_cursor.close()
    db_connection.close()
    print("DB Connection Closed")

  def db_get(sql: str) -> list:
    db_connection.ping(reconnect=True)
    db_cursor.execute(sql)
    return db_cursor.fetchall()

  # Executes an SQL query with values and commits the transaction

  def db_post(sql: str, values: str) -> list:
    db_connection.ping(reconnect=True)
    db_cursor.execute(sql, values)
    db_connection.commit()
    return db_cursor.fetchall()

  # Executes an SQL query and commits the transaction

  def db_delete(sql: str) -> list:
    db_connection.ping(reconnect=True)
    db_cursor.execute(sql)
    db_connection.commit()
    return db_cursor.fetchall()

  @app.route('/', methods=['GET'])
  @metrics.do_not_track()
  def start():
    return redirect(request.base_url + '/api/v1/swagger')

  @app.route('/health', methods=['GET'])
  @metrics.do_not_track()
  def health_check() -> json:
    # baseUrl = request.base_url[:-7]
    # randChoice = random.choice(AVAILABLE_PATHS)
    # response = requests.get(baseUrl + randChoice)
    # status_code = response.status_code
    # if status_code == 200:
    #   return Response(status=200, response=json.dumps({"message": "OK - healthy"}))
    db_connection.ping(reconnect=True)
    if db_connection.open:
      return Response(status=200, response=json.dumps({"message": "OK - healthy"}))
    return Response(status=500, response=json.dumps({"message": "ERROR - unhealthy"}))
  
  @app.route('/metrics', methods=['GET'])
  @metrics.do_not_track()
  def metrics() -> json:
    return Response(status=200, response=json.dumps({"message": "OK - metrics"}))

  @app.route('/api/v1/book/', methods=['GET', 'POST'])
  def get_books() -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = 'SELECT * FROM books'
      db_content = db_get(sql)

    if request.method == 'POST':
      body = request.json
      sql = 'INSERT INTO books (title, year_written, author) VALUES (%s, %s, %s)'
      db_content = db_post(
          sql, (body['title'], body['year_written'], body['author']))
    response["db_content"] = db_content
    return json.dumps(response)

  @app.route('/api/v1/book/<int:book_ID>/', methods=['GET', 'DELETE'])
  def get_book_by_id(book_ID: int) -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = f'SELECT * FROM books WHERE id = {book_ID}'
      db_content = db_get(sql)

    if request.method == 'DELETE':
      sql = f'DELETE FROM books WHERE id = {book_ID}'
      db_content = db_delete(sql)

    if db_content != ():
      response["db_content"] = db_content
    else:
      response["message"] = f"Unfortunately there is no book with the id {book_ID}"
    return json.dumps(response)

  @app.route('/api/v1/book/year/<int:year>/', methods=['GET'])
  def get_books_by_year(year: int) -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = f'SELECT * FROM books WHERE year_written = {year}'
      db_content = db_get(sql)

    if db_content != ():
      response["db_content"] = db_content
    else:
      response["message"] = f"Unfortunately we have no book from {year} in our database"
    return json.dumps(response)

  @app.route('/api/v1/book/author', methods=['GET'])
  def get_authors() -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = 'SELECT author FROM books'
      db_content = db_get(sql)
      response["db_content"] = db_content
    return json.dumps(response)

  @app.route('/api/v1/book/title', methods=['GET'])
  def get_titles() -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = 'SELECT title FROM books'
      db_content = db_get(sql)
      response["db_content"] = db_content
    return json.dumps(response)

  @app.route('/api/v1/book/author/<string:author_name>', methods=['GET'])
  def get_books_by_author(author_name: str) -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = f'SELECT * FROM books WHERE author = "{author_name}"'
      db_content = db_get(sql)

    if db_content != ():
      response["db_content"] = db_content
    else:
      response["message"] = f"Unfortunately we have no author called {author_name} in our database"
    return json.dumps(response)

  @app.route('/api/v1/book/title/<string:book_title>', methods=['GET'])
  def get_book_by_title(book_title: str) -> json:
    response = {
        "status_code": 200,
        "message": "Request was successful"
    }
    if request.method == 'GET':
      sql = f'SELECT * FROM books WHERE title = "{book_title}"'
      db_content = db_get(sql)

    if db_content != ():
      response["db_content"] = db_content
    else:
      response["message"] = f"Unfortunately we have no book called {book_title} in our database"
    return json.dumps(response)


  @app.errorhandler(404)
  def page_not_found(error: str):
      response = {
          "status_code": 404,
          "message": "This endpoint does not exist"
      }
      return json.dumps(response), 404

  @app.errorhandler(405)
  def method_not_allowed(error: str) -> json:
    response = {
        "status_code": 405,
        "message": "Method Not Allowed, try another one"
    }
    return json.dumps(response), 405


if __name__ == "__main__":
    atexit.register(exit_handler)
    port = 8080
    #port = int(os.environ.get("PORT", 8080))

    # using waitress for WSGI Server ( designed to handle many requests concurrently
    # and better compatibility with different web server )
    #from waitress import serve
    #serve(app, host='0.0.0.0', port=port)

    app.run(host='0.0.0.0', port=port)
