default:
  just --list

run:
  poetry run uvicorn src.main:app --reload
