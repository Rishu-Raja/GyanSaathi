
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# ==================================================
# LOAD ENVIRONMENT
# ==================================================

PROJECT_FOLDER = Path(__file__).resolve().parent
ENV_FILE = PROJECT_FOLDER / ".env"

load_dotenv(ENV_FILE, override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        f"Gemini API key not found.\n"
        f"Expected .env file at: {ENV_FILE}"
    )

# ==================================================
# GEMINI CLIENT
# ==================================================

client = genai.Client(api_key=API_KEY)

# ==================================================
# PREFERRED MODELS
# ==================================================

PREFERRED_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite"
]

# ==================================================
# GET AVAILABLE MODELS
# ==================================================

def get_available_models():

    available = []

    try:

        for model in client.models.list():

            model_name = model.name

            # Remove "models/" if present
            if model_name.startswith("models/"):
                model_name = model_name.replace("models/", "")

            if model_name in PREFERRED_MODELS:
                available.append(model_name)

    except Exception:
        # If model listing fails, use our known list
        available = PREFERRED_MODELS.copy()

    # Keep preferred order
    ordered_models = []

    for model in PREFERRED_MODELS:
        if model in available:
            ordered_models.append(model)

    return ordered_models


# ==================================================
# GENERATE RESPONSE WITH AUTOMATIC FALLBACK
# ==================================================

def generate_response(prompt):

    models = get_available_models()

    if not models:
        return "No compatible Gemini model is available."

    failed_models = []

    for model in models:

        try:

            print(f"Trying: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response.text:

                print(f"Success: {model}")

                return response.text

            failed_models.append(model)

        except Exception as e:

            error = str(e)

            print(f"{model} failed")

            # ------------------------------------------------
            # QUOTA / RATE LIMIT
            # ------------------------------------------------

            if (
                "429" in error
                or "RESOURCE_EXHAUSTED" in error
                or "quota" in error.lower()
                or "rate limit" in error.lower()
            ):

                print(f"Quota/rate limit reached for {model}")
                print("Switching to next model...")

                failed_models.append(model)

                continue

            # ------------------------------------------------
            # MODEL NOT AVAILABLE
            # ------------------------------------------------

            if (
                "404" in error
                or "NOT_FOUND" in error
                or "not found" in error.lower()
            ):

                print(f"{model} is unavailable.")
                failed_models.append(model)

                continue

            # ------------------------------------------------
            # OTHER ERROR
            # ------------------------------------------------

            failed_models.append(model)

            continue

    # ==================================================
    # ALL MODELS FAILED
    # ==================================================

    return (
        "⚠️ All available Gemini models are currently "
        "unavailable or have reached their quota. "
        "Please try again later."
    )
