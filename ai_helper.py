
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class AIConfigurationError(Exception):
    """Raised when the Groq API is not configured."""


class AIServiceError(Exception):
    """Raised when the Groq service cannot complete a request."""


def get_api_key():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_actual_api_key":
        raise AIConfigurationError(
            "Groq API key is missing. Add GROQ_API_KEY to your .env file, then restart the app."
        )
    return api_key


def choose_model(client):
    configured_model = os.getenv("GROQ_MODEL", "").strip()
    if configured_model:
        return configured_model

    # Discover an available text-generation model from the account when possible.
    try:
        available = client.models.list()
        model_ids = [
            model.id for model in available.data
            if getattr(model, "id", None)
            and not any(word in model.id.lower() for word in ("whisper", "guard", "embed"))
        ]
        if model_ids:
            return model_ids[0]
    except Exception:
        pass

    # Fallback is a commonly available Groq text model; users can override it in .env.
    return "llama-3.3-70b-versatile"


def ask_ai(prompt):
    try:
        client = Groq(api_key=get_api_key())
        model = choose_model(client)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a supportive academic study assistant. Give clear, practical, "
                        "age-appropriate guidance. Do not make assumptions beyond the supplied data."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=1800,
        )
        return response.choices[0].message.content.strip()
    except AIConfigurationError:
        raise
    except Exception as error:
        message = str(error)
        print("ACTUAL GROQ ERROR:", repr(error))
        if "model" in message.lower() and ("not found" in message.lower() or "decommission" in message.lower()):
            raise AIServiceError(
                "The selected Groq model is unavailable. Set a currently supported model in GROQ_MODEL in .env."
            )
        if "connection" in message.lower() or "timeout" in message.lower():
            raise AIServiceError("Could not connect to Groq. Check your internet connection and try again.")
        raise AIServiceError("Groq could not complete the request. Check your API key, model name, and account access.")


def describe_student(student):
    # Deliberately exclude student name and ID to protect student privacy.
    subjects = "\n".join(
        f"- {subject}: {mark:g}/100" for subject, mark in student["marks"].items()
    )
    return (
        f"Class/Semester: {student['class']}\n"
        f"Subject marks:\n{subjects}\n"
        f"Total marks: {student['total']}\n"
        f"Average percentage: {student['average']}%\n"
        f"Grade: {student['grade']}"
    )


def analyze_performance(student):
    prompt = (
        "Analyze this student's academic performance. Identify strong subjects and subjects "
        "that need more attention, provide a short balanced summary, and give practical improvement "
        "steps. Use headings and concise bullet points.\n\n"
        + describe_student(student)
    )
    return ask_ai(prompt)


def generate_study_tips(student):
    prompt = (
        "Create a realistic weekly study plan personalized to these marks. Include suggestions "
        "for subjects needing improvement, daily study tips, practical learning methods, and a short "
        "encouraging closing note. Keep it clear and manageable. Use headings and bullet points.\n\n"
        + describe_student(student)
    )
    return ask_ai(prompt)
