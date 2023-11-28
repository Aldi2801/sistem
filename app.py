
from app import app
#ssl_context='adhoc'
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=4000)