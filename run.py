from src.application.main import app

if __name__ == '__main__':
    # App is threaded=true due to slow loading times on localhost
    app.run(host='localhost', port=8888, threaded=True)
