"""The expert system.

scoring.py       - PURE functions. Imports nothing from app.db or app.models.
explain.py       - supporting / against / missing evidence per ranked disease.
next_question.py - information-gain selection of the most useful next symptom.
runner.py        - the only module here allowed to touch the database.

See docs/ARCHITECTURE.md for the algorithm and the required test cases.
"""
