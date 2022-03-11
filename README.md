# Focus Backend Engineer Exercises

Both exercises involve implementing code and then verifying that the written test cases pass as expected.

All tests are located in `test_backend_engineer_interview.py`

## Structure

```
backend-engineer-interview/
  backend_engineer_interview/
    app.py
    handlers.py - Routes should be implemented here
    models.py - Database models, new models should be added here
  tests/
    test_backend_engineer_interview.py - Test cases for the exercises
  app.db - initialized sqlite db
  openapi.yaml - Open API specifications
```

## In person exercise

Pair programming task (candidate drives) where the goal is to implement a function that splits a start and end date around a specified split date.

### Pair Programming Exercise Instructions

Implement `handlers.split_start_end_dates`. Use the test cases in `TestSplitDates` to verify your work.  The exercise is complete when they all pass.

## Async Exercise

Exercise is meant to be completed asynchronously and then brought to the follow up interview.  The exercise can be completed using any IDE, but this
repo includes settings for VSCode.

The overall structure of the API has routes defined in `openapi.yaml` which are then wired to python functions with `operationId`.  For an example,
look at the provided `/v1/status` endpoint.

### Setup Instructions

1. Install python@3.9.7.  This can be managed with [asdf](https://github.com/asdf-vm/asdf) and [asdf-python](https://github.com/danhper/asdf-python)
2. Install [poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions)
3. Run `poetry config virtualenvs.in-project true`
4. Run `poetry install --no-root`.  Installing the dependencies will take a few minutes.
5. Run `poetry run python -m backend_engineer_interview` to bring up the API server

### Async Exercise Instructions

1. Complete the `get_employee` endpoint in `handlers.py`.  The table model and response model already exist.  To verify that it's working as expected,
all of the `TestGetEmployee` tests should pass.
2. Implement the `patch_employee`.  To verify that it's working as expected, all of the `TestPatchEmployee` tests should pass.
3. Implement the `post_application` API definition and implement the handler. To verify that it's working, all of the `TestPostApplication` tests shuold pass.

## FAQ

- How do I reset the database?

  Delete the app.db file and run `poetry run alembic upgrade head`

- What URL are the docs at?

  http://localhost:1550/v1/docs

- How do I see an example response?

  If you would like to see the example response generated from the open API definition.  Simply comment out `operationId`.

- How do I create new tables from models?

  New tables can be generated by running `poetry run alembic revision --autogenerate -m "Revision name"` and then `poetry run alembic upgrade head`