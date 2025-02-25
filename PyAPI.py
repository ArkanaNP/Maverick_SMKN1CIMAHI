from flask import Flask
app = Flask(__name__)

@app.route('/')
def entry_point():
    return 'Hello API!'

if __name__=='__main__':
    app.run(debug=True)
