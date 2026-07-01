
from langchain.messages import SystemMessage
import system_messages
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import cast
from time import sleep
from pathlib import Path


from parameters import RATE_LIMIT_DELAY
from models import summarizer_agent, writer_agent, reviewer_agent, reviser_agent, ReviewOutput

def extract_text(filepath: str) -> str:

    """extract the text from the original scientific paper"""
    if filepath.endswith(".pdf"):
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        paper_text = "\n\n".join([page.page_content for page in pages])
    else:
        loader = TextLoader(filepath)
        docs = loader.load()
        paper_text = docs[0].page_content

    return paper_text

def summarize_paper(paper_text: str) -> str:

    """Summarize a scientific paper from a PDF or text file."""

    response = summarizer_agent.invoke([
        SystemMessage(content=system_messages.summarizer),
        {"role": "user", "content": paper_text}
    ])

    return str(response.content[0]['text'])

def write_article_czech(paper_summary: str, original_text: str) -> str:

    """Write a Czech pop-science article from a scientific paper summary.
    Args:
        paper_summary: A summary of the scientific paper's key findings
        original_text: The original research paper text
    Returns:
        A complete pop-science article draft
    """

    response = writer_agent.invoke([
        SystemMessage(content=system_messages.writer),
        {"role": "user", "content": f"Here is the entirety of the reserch paper text for reference:\n\n{original_text}\n\nPlease, write an article based on this summary:\n\n{paper_summary}"}
    ])
    sleep(RATE_LIMIT_DELAY)

    return str(response.content[0]['text'])


def review_article(article: str, original_text: str) -> ReviewOutput:

    """Review a pop-science article for accessibility and engagement.
    Args:
        article: The article to review
        original_text: The original research paper text
    Returns:
        ReviewOutput with approved status and feedback list
    """

    response = reviewer_agent.invoke([
        SystemMessage(content=system_messages.reviewer),
        {"role": "user", "content": f"Please, review the following article:\n\n{article}\n\nCompare it with the original research paper for fact-checking: {original_text}"}
    ])
    sleep(RATE_LIMIT_DELAY)

    return cast(ReviewOutput, response)

def revise_article(article: str, original_text: str, feedback: str) -> str:

    """Revise an article based on editorial feedback.
    Args:
        article: The original article
        original_text: The original research paper text
        feedback: Review feedback with specific improvements needed
    Returns:
        An improved version of the article
    """

    response = reviser_agent.invoke([
        SystemMessage(content=system_messages.reviser),
        {"role": "user", "content": f"Original research paper:\n{original_text}\n\nArticle for revision:\n{article}\n\nReviewer's feedback:\n{feedback}\n\nPlease, revise the article to include any requested changes."}
    ])
    sleep(RATE_LIMIT_DELAY)

    return str(response.content[0]['text'])


def save_article(article: str) -> str:

    """Save the finalized article to a file.
    Args:
        article: The complete finalized article text
    Returns:
        Confirmation message with file path
    """

    filepath = "/home/fj/eve/final_article.md"
    with open(filepath, 'w') as f:
        f.write(article)

    return filepath


## LOG WRITING AND CLEARING FUNCTIONS
def clear_state_outputs_txt() -> None:
    output_dir = Path(__file__).resolve().parent / "state_outputs"
    if not output_dir.exists():
        return

    for txt_file in output_dir.glob("*.txt"):
        txt_file.unlink()


def write_to_file(filename: str, content: str):
    filepath = f"/home/fj/eve/state_outputs/{filename}"
    with open(filepath, 'w') as f:
        f.write(content)
