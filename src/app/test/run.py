from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/runcode', methods=['GET'])
def runcode():
    try:
        # Execute the app.py script
        result = subprocess.run(['python', 'app.py'], capture_output=True, text=True)
        return f"Output: {result.stdout}\nError: {result.stderr}", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
