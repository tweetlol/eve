
from langchain.messages import SystemMessage
import system_messages
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import cast
from models import summarizer_agent, writer_agent, reviewer_agent, reviser_agent, translator_agent

from time import sleep
from parameters import RATE_LIMIT_DELAY
from models import ReviewOutput


def summarize_paper(filepath: str) -> str:

    """Summarize a scientific paper from a PDF or text file."""

    if filepath.endswith(".pdf"):
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        paper_text = "\n\n".join([page.page_content for page in pages])
    else:
        loader = TextLoader(filepath)
        docs = loader.load()
        paper_text = docs[0].page_content

    response = summarizer_agent.invoke([
        SystemMessage(content=system_messages.summarizer),
        {"role": "user", "content": paper_text}
    ])

    return str(response.content[0]['text'])

def write_article(paper_summary: str) -> str:

    """Write an engaging pop-science article from a scientific paper summary.
    Args:
        paper_summary: A summary of the scientific paper's key findings
    Returns:
        A complete pop-science article draft
    """

    response = writer_agent.invoke([
        SystemMessage(content=system_messages.writer),
        {"role": "user", "content": f"Please, write a pop-science article based on this summary:\n\n{paper_summary}"}
    ])
    sleep(RATE_LIMIT_DELAY)

    return str(response.content[0]['text'])


def review_article(article: str) -> ReviewOutput:

    """Review a pop-science article for accessibility and engagement.
    Args:
        article: The article to review
    Returns:
        ReviewOutput with approved status and feedback list
    """

    response = reviewer_agent.invoke([
        SystemMessage(content=system_messages.reviewer),
        {"role": "user", "content": f"Please, review the following article:\n\n{article}"}
    ])
    sleep(RATE_LIMIT_DELAY)

    return cast(ReviewOutput, response)

def revise_article(article: str, feedback: str) -> str:

    """Revise an article based on editorial feedback.
    Args:
        article: The original article
        feedback: Review feedback with specific improvements needed
    Returns:
        An improved version of the article
    """

    response = reviser_agent.invoke([
        SystemMessage(content=system_messages.reviser),
        {"role": "user", "content": f"Original article:\n{article}\n\nReviewer's feedback:\n{feedback}\n\nPlease, revise the article."}
    ])
    sleep(RATE_LIMIT_DELAY)

    return str(response.content[0]['text'])


def save_article_english(article: str) -> str:

    """Save the finalized article to a file.
    Args:
        article: The complete finalized article text
    Returns:
        Confirmation message with file path
    """

    filepath = "/home/fj/eve/final_article_english.md"
    with open(filepath, 'w') as f:
        f.write(article)

    return filepath


def translate_article(article: str) -> str:

    """Translate the finalized article to czech.
    Args:
        article: The finalized article
    Returns:
        The translated article
    """

    response = translator_agent.invoke([
        SystemMessage(content=system_messages.translator),
        {"role": "user", "content": f"Please, translate the following article to Czech:\n\n{article}"}
    ])

    return str(response.content[0]['text'])


def save_article_czech(article: str) -> str:

    """Save the finalized and translated article to a file.
    Args:
        article: The complete finalized and translated article text
    Returns:
        Confirmation message with file path
    """

    filepath = "/home/fj/eve/final_article_czech.md"
    with open(filepath, 'w') as f:
        f.write(article)

    return filepath