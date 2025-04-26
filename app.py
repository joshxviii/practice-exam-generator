from google import genai
from flask import Flask, render_template, request, url_for, session, redirect
import re

app = Flask(__name__)
app.secret_key = "web-key"

try: 
    client = genai.Client(api_key="AIzaSyDsnJdjMVuuK8K6tFzZjvEARaUrcErCkBg")
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

@app.route("/", methods=["GET"])
def home():
    print("HELLO")

    # if request.method == "POST":
    #     return generate_prompt()
    questions = session.pop('questions', None)
    error = session.pop('error', None)
    message = session.pop('message', None)
    return render_template("index.html", questions=questions, error=error, message=message)



@app.route('/generate_prompt', methods=["POST"])
def generate_prompt():
    message = ""
    questions = ""
    error = None

    course = request.form.get("course", "").strip()
    topic = request.form.get("topic", "").strip()
    num_questions = request.form.get("num_questions", "10").strip()

    session["course"] = course
    session["topic"] = topic
    session["num_questions"] = num_questions
        
    if not course and not topic:
        error = "Please provide a course and a topic."
    try:
        num_questions = int(num_questions)
        if num_questions < 1 or num_questions > 20:
            error = "Number of questions must be between 1 and 20"
    except ValueError:
        error = "Please enter a valid number of questions"

    if not error and client:
        prompt = (
            f"Act as a tutor for {course}. Generate {num_questions} multiple-choice practice problems on {topic}. "
            "Format each problem as follows:"
            "Problem: [Question]"
            "a) [Option]"
            "b) [Option]"
            "c) [Option]"
            "d) [Option]."
            "answer: [A, B, C, or D]"
            "Use only UTF-8 characters. Separate problems with a blank line."
        )

        try:
            response = client.models.generate_content(model = "gemini-2.0-flash", contents = prompt)
            message = response.text
            questions = message
        except Exception as e:
            error = f"Error generating questions: {str(e)}"
    #print(parse_prompt(message))
    session['message'] = message
    session['error'] = error
    session['questions'] = questions

    return redirect(url_for("home"))


def parse_prompt(prompt):
    pattern = r'Problem:\s*(.*?)\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)(?=\s*Problem:|$)'
    matches = re.findall(pattern, prompt, re.DOTALL)

    problems = []
    for match in matches:
        problem = {
            'problem': match[0].strip(),
            'a': match[1].strip(),
            'b': match[2].strip(),
            'c': match[3].strip(),
            'd': match[4].strip()
        }
        problems.append(problem)
    return problems


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)