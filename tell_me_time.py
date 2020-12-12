from flask import Flask
import requests
import os,time

app = Flask(__name__)

@app.route('/')
def get_time():
 t = f"time is {time.time()}"
 return t

if __name__ == '__main__':
 app.run(debug=True,host='0.0.0.0',port=5001)
