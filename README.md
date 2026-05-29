# FinSight AI

Financial analysis platform with LLM, RAG, and MLOps capabilities.

## Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **LLM Layer:** LangChain, LangGraph, LangSmith, ChromaDB, OpenAI
- **MLOps:** MLflow, scikit-learn, Docker
- **Cloud:** AWS (S3, RDS, ECR, Lambda), Terraform
- **CI/CD:** GitHub Actions

## Status

In active development — AI Engineer portfolio project

## Architecture

> Diagram added at Milestone 3.4

## Setup

```bash
git clone https://github.com/Viicsr/finsight-ai
cd finsight-ai
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # fill in your keys
