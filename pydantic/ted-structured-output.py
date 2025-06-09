# =============================================================================
# Structured output - Test summarization
# Created: 9, Jun 2025
# Updated: 9, Jun 2025
# Writer: Ted, Jung
# Description: 
#   Type types(one for json string the other pydantic mapping with pair of key-values)
#   Second option leverage pydantic (type validation with format)
# =============================================================================


import os

from textwrap import dedent
from pydantic import BaseModel, ValidationError
from openai import OpenAI

MODEL = "gpt-4.1-nano"

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

class ArticleSummary(BaseModel):
    invented_year: int
    summary: str
    inventors: list[str]
    description: str

    class Concept(BaseModel):
        title: str
        description: str

    concepts: list[Concept]



article_data = {
    "invented_year": 2022,
    "summary": "A novel method for sustainable energy production.",
    "inventors": ["Dr. Jane Doe", "Dr. John Smith"],
    "description": "This invention describes a breakthrough in renewable energy.",
    "concepts": [
        {"title": "Renewable Energy", "description": "Energy from natural resources."},
        {"title": "Sustainable Production", "description": "Producing goods without depleting resources."}
    ]
}

# Create a valid ArticleSummary object
# pass this article_data (pairs of key and value) into Pydantic object
try:
    article = ArticleSummary(**article_data)
    print("Article created successfully:")
    print(article.model_dump_json(indent=2))
except ValidationError as e:
    print("Validation Error:", e)



summarization_prompt = '''
    You will be provided with content from an article about an invention.
    Your goal will be to summarize the article following the schema provided.
    Here is a description of the parameters:
    - invented_year: year in which the invention discussed in the article was invented
    - summary: one sentence summary of what the invention is
    - inventors: array of strings listing the inventor full names if present, otherwise just surname
    - concepts: array of key concepts related to the invention, each concept containing a title and a description
    - description: short description of the invention
'''

def get_article_summary(text: str):
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": dedent(summarization_prompt)},
            {"role": "user", "content": text}
        ],
        response_format=ArticleSummary,
    )

    return completion.choices[0].message.parsed


def get_article_content(path):
    with open(path, 'r') as f:
        content = f.read()
    return content


articles = [
    "./data/structured_outputs_articles/cnns.md",
    "./data/structured_outputs_articles/llms.md",
    "./data/structured_outputs_articles/moe.md"
]
content = [get_article_content(path) for path in articles]

summaries = []

for i in range(len(content)):
    print(f"Analyzing article #{i+1}...")
    summaries.append(get_article_summary(content[i]))
    print("Done.")


def print_summary(summary):
    print(f"Invented year: {summary.invented_year}\n")
    print(f"Summary: {summary.summary}\n")
    print("Inventors:")
    for i in summary.inventors:
        print(f"- {i}")
    print("\nConcepts:")
    for c in summary.concepts:
        print(f"- {c.title}: {c.description}")
    print(f"\nDescription: {summary.description}")


for i in range(len(summaries)):
    print(f"ARTICLE {i}\n")
    print_summary(summaries[i])
    print("\n\n")