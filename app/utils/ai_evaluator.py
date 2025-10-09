# backend/app/utils/ai_evaluator.py
import os
import openai
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def evaluate_open_ended_question(question_text: str, sample_answer: str, student_response: str) -> dict:
    """
    Evaluates a student's open-ended response against a sample answer using OpenAI's GPT model.

    Args:
        question_text (str): The text of the question.
        sample_answer (str): The provided sample/correct answer.
        student_response (str): The student's answer.

    Returns:
        dict: A dictionary containing 'score' (0-100), 'feedback' (textual), and 'is_correct' (boolean or None).
    """
    if not openai.api_key:
        print("OPENAI_API_KEY is not set. AI evaluation skipped.")
        return {"score": 0, "feedback": "AI evaluation skipped: API key not set.", "is_correct": False}

    if not student_response or student_response.strip() == "":
        return {"score": 0, "feedback": "Student response is empty.", "is_correct": False}
    
    if not sample_answer or sample_answer.strip() == "":
        return {"score": 0, "feedback": "AI evaluation skipped: Sample answer is empty for reference.", "is_correct": False}


    prompt = f"""
    You are an AI assistant designed to evaluate student answers for open-ended questions in an exam setting.
    You will be given a question, a sample (correct) answer, and the student's response.
    
    Your task is to:
    1.  **Assess Accuracy:** Compare the student's response against the sample answer for factual correctness and completeness.
    2.  **Assign a Score:** Provide a score out of 100 based on accuracy and completeness.
        - 90-100: Excellent, largely complete and accurate.
        - 70-89: Good, mostly accurate but might miss minor details or phrasing.
        - 50-69: Fair, contains some correct points but is incomplete or has minor inaccuracies.
        - 30-49: Poor, shows some understanding but is largely incorrect or very incomplete.
        - 0-29: Very poor, little to no correct information.
    3.  **Provide Constructive Feedback:** Explain why the score was given and suggest areas for improvement or missing information.
    4.  **Determine Correctness:** Output a boolean (True/False) indicating if the student's answer can be considered correct (generally >= 70 score).

    Provide your output in a JSON format with the following keys: `score`, `feedback`, `is_correct`.

    ---
    Question: {question_text}
    Sample Answer: {sample_answer}
    Student Response: {student_response}
    ---
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125", # Or "gpt-4o", "gpt-4-turbo" for better quality, depending on cost/speed needs
            messages=[
                {"role": "system", "content": "You are a helpful assistant that evaluates student answers."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}, # Instruct GPT to return JSON
            temperature=0.2, # Keep temperature low for deterministic evaluation
            max_tokens=500 # Adjust as needed for feedback length
        )
        
        evaluation_result = json.loads(response.choices[0].message.content)
        return evaluation_result

    except openai.APIConnectionError as e:
        print(f"OpenAI API connection error: {e}")
        return {"score": 0, "feedback": f"AI evaluation failed: API connection error: {e}", "is_correct": False}
    except openai.RateLimitError as e:
        print(f"OpenAI API rate limit exceeded: {e}")
        return {"score": 0, "feedback": f"AI evaluation failed: Rate limit exceeded: {e}", "is_correct": False}
    except openai.APIStatusError as e:
        print(f"OpenAI API status error: {e.status_code} - {e.response}")
        return {"score": 0, "feedback": f"AI evaluation failed: API error {e.status_code}", "is_correct": False}
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from OpenAI response: {e}")
        return {"score": 0, "feedback": f"AI evaluation failed: Invalid response format from AI. Debugging needed. Raw: {response.choices[0].message.content}", "is_correct": False}
    except Exception as e:
        print(f"An unexpected error occurred during AI evaluation: {e}")
        return {"score": 0, "feedback": f"AI evaluation failed: An unexpected error occurred: {e}", "is_correct": False}