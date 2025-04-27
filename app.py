from google import genai
from flask import Flask, render_template, request, session, redirect, url_for, send_file
import re
import json
import os
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "web-key"
client = None

def get_api_key():
    with open('api_key.txt', 'r') as file:
        api_key = file.readline().strip().split('=')[1]
        return api_key



""" Home Page Logic """
@app.route("/", methods=["GET"])
def home():
    print("practice-exam-generator START")
    return render_template("index.html")



""" Practice Exam Page Logic """
@app.route('/practice_exam', methods=["POST", "GET"])
def generate_exam():
    message = ""
    error = None
    problems = []

    # Extract user input data from html page
    course = request.form.get("course", "").strip()
    topic = request.form.get("topic", "").strip()
    num_questions = request.form.get("num_questions", "10").strip()
    #if url has 'is_from_import' argument then get question from json file
    is_from_import = request.args.get("is_from_import")
    if (is_from_import): problems = session['problems']
        
    if (not error and client) and not is_from_import:

        if not course or not topic:
            return 'Please provide a course and a topic.', 400
        try:
            num_questions = int(num_questions)
            if num_questions < 1 or num_questions > 20:
                 return 'Number of questions must be between 1 and 20', 400
        except ValueError:
            return 'Please enter a valid number of questions', 400

        prompt = (
            f"Act as a tutor for {course}. Generate {num_questions} multiple-choice practice problems on {topic}. "
            "Format each problem as follows:"
            "problem: [Question]"
            "a) [Option]"
            "b) [Option]"
            "c) [Option]"
            "d) [Option]."
            "answer: [a | b | c | d]"
            "Use only UTF-8 characters. Separate problems with a blank line."
        )

        try:
            response = client.models.generate_content(model = "gemini-2.0-flash", contents = prompt)
            message = response.text
            problems = parse_prompt(message)
            print(problems)
        except Exception as e:
            error = f"Error generating questions: {str(e)}"
            print(error)

    # Ensure the number of questions matches the user's input
    if len(problems) != num_questions:
        return f"Expected {num_questions} questions, but got {len(problems)}. Please try again.", 400

    # Store the problems in the session
    session['questions'] = problems

    """ Generate a html template for each problem from the prompt """
    html = '<form action="/submit_quiz" method="POST">\n'
    for idx, p in enumerate(problems):
        html += f'  <div class="problem-block">\n'
        html += f'    <p><strong>Question {idx+1}:</strong> {p["problem"]}</p>\n'
        
        for letter in ['a', 'b', 'c', 'd']:# create radio button selection for each problem option
            html += (
                f'    <label class="choice-label">\n'
                f'      <input type="radio" name="q{idx}" value="{letter}" required>\n'
                f'      ({letter}) {p[letter]}\n'
                f'    </label><br>\n'
            )

        html += '  </div>\n  <br>\n'
       
    html += '<input type="submit" class="submit-button" value="Submit">\n'
    html += '</form>'

    #Go to new page with generated problems
    return render_template("exam.html", exam_problems_html=html, course=course)



""" Parse the prompt output for the Exam Page into a map with the relavent information """
def parse_prompt(prompt):
    pattern = r'problem:\s*(.*?)\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*answer:\s*(\w)'
    matches = re.findall(pattern, prompt, re.DOTALL)

    problems = []
    for match in matches:
        problem = {
            'problem': match[0].strip(),
            'a': match[1].strip(),
            'b': match[2].strip(),
            'c': match[3].strip(),
            'd': match[4].strip(),
            'answer': match[5].strip()
        }
        problems.append(problem)
    return problems



""" Answers Page Logic """
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    score = 0
    total = 0
    wrong_questions = []
    wrong_answers = []
    html = '<form action="/submit_quiz" method="POST">\n'
    problems = session.get("questions", [])  # Retrieve questions from the correct session key

    """ Similar to html generation as the Exam Page, but this time for the Answers Page """
    for idx, p in enumerate(problems):
        html += f'  <div class="problem-block">\n'
        html += f'    <p><strong>Question {idx+1}:</strong> {p["problem"]}</p>\n'
        correct_answer = p['answer']
        user_answer = request.form.get(f'q{idx}')
        total += 1
        response = ""
        if user_answer == correct_answer:
            score += 1
        else:
            prompt = f"The question was {p['problem']}. The correct answer was {p[correct_answer]}. I got {p[user_answer]}. Walk me through what I did wrong in 1 sentence. Use only UTF-8 characters when responding and use no special characters."
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text
            wrong_questions.append(p["problem"])
            wrong_answers.append(user_answer)
        for letter in ['a', 'b', 'c', 'd']:
            html += (   # Mark correct answers in green and incorrect answers in red.
                f'      <label class="{("green" if (letter == correct_answer) else "")} {("red" if (letter == user_answer and correct_answer != user_answer) else "")}">\n'
                f'          <input type="radio" name="q{idx}" value="{letter}" disabled>\n'
                f'          ({letter}) {p[letter]}\n'
                f'      </label><br>\n'
            )
        if user_answer != correct_answer:
            html += f"<p>What went wrong: {response}</p>"
        html += '  </div>\n  <br>\n'
    html += '</form>'

    # Generate feedback
    input = ""
    for a, q in zip(wrong_answers, wrong_questions):
        input += f"The question was {q}. The answer I incorrectly got was {a}. "
    input += "Given all the mistakes I made on this practice test, give me the main subjects that I should work on to improve my skills in this topic in 1 sentence."
    if len(wrong_answers) > 0:
        feedback = client.models.generate_content(model="gemini-2.0-flash", contents=input).text
        html += f'<br><p>Tips for the future: {feedback}</p>'

    return render_template("answer.html", answers_html=html, score=score, total=total)  



""" function to import saved exams from a json file"""
@app.route("/file", methods=["POST"])
def import_questions():
    file = request.files['import']

    try:
        data = json.load(file.stream)
    except json.JSONDecodeError:
        return 'Invalid JSON file', 400
            
    session['problems'] = data
    return redirect(url_for('generate_exam', is_from_import=True))



""" Generate PDF Logic """
@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    # Correctly handle the structure of questions stored in the session
    if 'questions' not in session or not session['questions']:
        return "No questions available to generate PDF", 400

    questions = session['questions']

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add all questions to the same page
    for idx, question in enumerate(questions, start=1):
        pdf.multi_cell(0, 10, f"Q{idx}: {question['problem']}")
        for option in ['a', 'b', 'c', 'd']:
            pdf.multi_cell(0, 10, f"   {option}) {question[option]}")

    # Add an answer key on a separate page
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Answer Key", ln=True, align="C")
    pdf.ln(10)  # Add some space

    for idx, question in enumerate(questions, start=1):
        pdf.cell(0, 10, f"Q{idx}: {question['answer']}", ln=True)

    pdf_output_path = os.path.join('static', 'practice_exam.pdf')
    pdf.output(pdf_output_path)

    return send_file(pdf_output_path, as_attachment=True)



"""Main"""
if __name__ == '__main__':

    try: client = genai.Client(api_key=get_api_key())
    except Exception as e: print(f"Error initializing Gemini client: {e}")

    app.run(host="0.0.0.0", port=5000, debug=True)