# **Practice Exam Generator**

### **Features**
- **Generate Practice Exams**: Create exams for any subject, with questions covering a wide variety of topics.
- **Answer Questions**: Answer multiple-choice questions and receive a score at the end of the exam.
- **Feedback**: Get feedback based on your answers to help improve your understanding of the material.
- **Import Exams**: Import pre-made exams from a json file in case you want to share a particularly good exam.

### **How To Use**
1. **Input Information**:  
   - Enter your **Course** (e.g., "Math", "Music Theory", etc.).
   - Select your **Topic** (e.g., "Algebra", "Scales", etc.).
   - Specify the **Amount of Questions** you want to include in the exam.
   
2. **Generate Exam**:  
   Click the **Generate Exam** button to create the exam based on your inputs.

3. **Answer Questions**:  
   Each question will have a set of multiple-choice options. Choose the option you believe is correct for each question.

4. **Submit Exam**:  
   After completing all the questions, hit the **Submit** button to receive your score and detailed feedback based on your answers.

### **Technical Information**

- **Built with Python and Flask**:  
  This web application is powered by **Python** using the **Flask framework**, which makes it lightweight and easy to scale.

- **Frontend**:  
  The frontend is built using **HTML** and **CSS**
  
- **Backend**:  
  The backend processes the exam generation, user inputs, and scoring. It dynamically generates questions and answers using Python, and serves them to the user via Flask routes.

- **Data Parsing**:  
  The exam questions and answers are parsed from pre-defined datasets using **regular expressions (regex)** to extract the necessary components (question, choices, and correct answers). These are dynamically rendered with HTML.

### **How to Run Locally**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/joshxviii/practice-exam-generator.git
   cd practice-exam-generator
   ```

2. **Install Dependencies**:  
   First, make sure you have **Python 3** installed. Then, install the necessary dependencies using **pip**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   To start the server locally, run the following command:
   ```bash
   python app.py
   ```

4. **Visit the Application**:
   Open your web browser and go to `http://127.0.0.1:5000/` to see the Practice Exam Generator in action.

5. **Usage**:  
   From there, you can fill out the form to generate your practice exam, answer the questions, and get your score.

### **Project Structure**

```
practice-exam-generator/
│
├── app.py                   # Main Flask app
├── templates/               # HTML templates
│   ├── index.html           # Main page layout
│   └── exam.html            # Results page with score and feedback
│   └── answer.html          # Score page for displaying feedback on your performance.
├── static/                  # Static files (CSS, images, JS)
│   ├── home_style.css       # Custom CSS styles
│   ├── ...
├── requirements.txt         # List of Python dependencies
└── README.md                # Project documentation
```

### **Dependencies**
- **Flask**: A lightweight WSGI web application framework for Python.
- **Google-Genai**: Used for creating prompts that are parsed into exams.

To install the dependencies, run the following:
```bash
pip install -r requirements.txt
```

