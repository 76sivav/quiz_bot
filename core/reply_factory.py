
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:git 
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    
    if current_question_id is None or current_question_id > len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID."

    if not answer.strip():
        return False, "Answer cannot be empty."
        
    valid_options = [str(i + 1) for i in range(len(PYTHON_QUESTION_LIST[current_question_id]["options"]))]
    if answer not in valid_options:
        return False, "Invalid option. Please select a valid option number."

    if "answers" not in session:
        session["answers"] = {}
        
    session["answers"][current_question_id] = answer.strip()
    return True, ""



def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if not PYTHON_QUESTION_LIST:
        return None, None
    if current_question_id is None:
        next_question = PYTHON_QUESTION_LIST[0]
        question_text = f"{next_question['question_text']}\nOptions:\n" + "\n".join(
            [f"{i+1}. {opt}" for i, opt in enumerate(next_question['options'])]
        )
        return question_text, 0

    # Fetch the next question
    next_index = current_question_id + 1
    if next_index < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_index]
        question_text = f"{next_question['question_text']}\nOptions:\n" + "\n".join(
            [f"{i+1}. {opt}" for i, opt in enumerate(next_question['options'])]
        )
        return question_text, next_index
    
    return "dummy question", -1


def generate_final_response(session):
    # sourcery skip: inline-immediately-returned-variable
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_count = 0
    result=[]


    score = f"{correct_count} out of {total_questions}"
    result_message = f"🎉 Quiz Complete! Your score: {score}.\nThanks for participating!"


    for idx, question in enumerate(PYTHON_QUESTION_LIST):
        question_text = question["question_text"]
        correct_answer = question.get("answer", "").strip().lower()
        user_answer = user_answers.get(idx, "").strip().lower()

        if user_answer == correct_answer:
            correct_count += 1
            result.append(f"✅ Q{idx+1}: {question_text}\nYour answer: {user_answer}")
        else:
            result.append(
                f"❌ Q{idx+1}: {question_text}\nYour answer: {user_answer}\nCorrect answer: {correct_answer}"
            )

    # Compile the final result
    score = f"{correct_count} out of {total_questions}"
    result_message = f"🎉 Quiz Complete! Your score: {score}.\n\n" + "\n\n".join(result)

    return result_message

