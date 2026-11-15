
# AI Email Assistant Agent

## Project Description
An Agentic AI application that generates professional
emails, suggests replies, and categorizes messages.

## Features
1. User Input
2. Task Identification
3. Email Generation
4. Reply Suggestion
5. Email Categorization
6. Edit Draft
7. Save Draft
8. Draft History
9. Input Validation
10. Error Handling

## Technologies
- Python
- Streamlit
- Ollama
- LangChain
- SQLite
- Git and GitHub

## Installation

pip install -r requirements.txt

ollama pull llama3.2:3b

streamlit run app.py

## Database
SQLite stores email drafts locally.

## Security
The application generates and saves drafts.
It does not send emails automatically.
