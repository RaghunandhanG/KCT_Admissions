from flask import Flask, request, jsonify
from flask_cors import CORS
import main

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'}), 200


@app.route('/process', methods=['POST'])
def process_files():
    print("Entered")
    if 'files' not in request.files or 'keys' not in request.form :
        print('Files here')
        resp =  jsonify({'error': 'No files found in request'})
        resp.status_code = 400
        print("not found")
        return resp
    files = request.files.getlist('files')  
    keys = request.form.getlist('keys')  

    print(type(keys))

    print(files, keys)
    try:
        output = main.start_processing(files, keys)  
        return jsonify({'output': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
