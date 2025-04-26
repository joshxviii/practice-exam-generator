from google import genai
from flask import Flask, render_template

app = Flask(__name__)

client = genai.Client(api_key="AIzaSyDsnJdjMVuuK8K6tFzZjvEARaUrcErCkBg")

@app.route("/")

def home(): 
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Explain how AI works in a few words",
    )
    message = response.text
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
