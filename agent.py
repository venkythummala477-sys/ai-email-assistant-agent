
import json
import re

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from prompts import (
    ROUTER_PROMPT,
    EMAIL_PROMPT,
    REPLY_PROMPT,
    CATEGORY_PROMPT
)

MODEL_NAME = "llama3.2:3b"
OLLAMA_URL = "http://127.0.0.1:11434"


def get_llm():
    return ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_URL,
        temperature=0.2,
        format="json",
        timeout=120
    )


def extract_json(text):
    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*", "", cleaned,
        flags=re.I
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            f"Invalid JSON response from AI: {cleaned}"
        )

    return json.loads(cleaned[start:end + 1])


def call_chain(prompt_text, user_text):

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("human", "{user_text}")
    ])

    chain = prompt | get_llm()

    try:
        response = chain.invoke({
            "user_text": user_text
        })

        return extract_json(response.content)

    except Exception as e:
        print("AI AGENT ERROR:", repr(e))
        raise RuntimeError(
            f"AI processing failed: {str(e)}"
        ) from e


def run_agent(user_text, selected_action="Auto Detect"):

    if not user_text.strip():
        raise ValueError("Please enter a message.")

    if selected_action == "Auto Detect":

        route = call_chain(ROUTER_PROMPT, user_text)
        action = route.get("action", "").strip()

        allowed = [
            "Generate Email",
            "Suggest Reply",
            "Categorize Email"
        ]

        if action not in allowed:
            raise ValueError(
                f"Unable to identify task. AI returned: {action}"
            )

    else:
        action = selected_action

    if action == "Generate Email":

        result = call_chain(EMAIL_PROMPT, user_text)

        if not result.get("subject") or not result.get("body"):
            raise ValueError("Invalid email response")

        result.setdefault("category", "Work")
        result.setdefault("reason", "Professional email")

    elif action == "Suggest Reply":

        result = call_chain(REPLY_PROMPT, user_text)

        if not result.get("subject") or not result.get("body"):
            raise ValueError("Invalid reply response")

        result.setdefault("category", "Work")
        result.setdefault("reason", "Reply to incoming email")

    elif action == "Categorize Email":

        result = call_chain(CATEGORY_PROMPT, user_text)

        if result.get("category") not in [
            "Work", "Personal", "Urgent"
        ]:
            raise ValueError("Invalid category")

        result.setdefault("subject", "")
        result.setdefault("body", "")
        result.setdefault("reason", "Message classification")

    else:
        raise ValueError("Unsupported action")

    result["action"] = action

    return result
