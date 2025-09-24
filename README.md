# Creative Automation Pipeline

This repository contains a proof-of-concept (POC) for automating creative asset generation for social ad campaigns.

Task 1 – High-level architecture and roadmap (see Task1.png)

Task 2 – Creative automation pipeline (code in this repo)

Task 3 – AI-driven agent design and stakeholder communication (see Task3.png)


## Project Structure

adobe/
- pipeline.py          # main script
- requirements.txt     # dependencies
- brief.json           # example campaign brief
- Task1.png            # architecture & roadmap diagram
- Task3.png            # agent design diagram
- assets/
    -  input/          # input assets (logo, product images)
- outputs/             # generated creatives + logs

## Setup

`pip3 install -r requirements.txt`

## Minimal requirements:
    Pillow
    requests
    openai

`export OPENAI_API_KEY="your_api_key_here"`

## Running the Pipeline
`python3 pipeline.py`


The script will:

- Read brief.json (campaign metadata).
- Use existing assets from assets/input/ or call the OpenAI Images API to generate new ones.
- Produce creatives in 3 aspect ratios (1:1, 9:16, 16:9).
- Overlay campaign message + add brand logo.
- Run compliance checks (brand color, prohibited words).
- Save outputs under outputs/<campaign>/<product>/<ratio>/.
- Log results to outputs/pipeline_log.csv.

## Sample Input - brief.json
{
  "campaign_name": "Spring Sale 2025",
  "products": ["Laptop", "Headphones"],
  "region": "US",
  "audience": "Students",
  "message": "Big Spring Discounts - Shop Now!"
}


## Email to customer:
    email.txt
