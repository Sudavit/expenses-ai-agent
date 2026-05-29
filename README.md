![GitHub Release](https://img.shields.io/github/v/tag/Sudavit/expenses-ai-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/jsh/trendlist/blob/master/LICENSE)
![Pytest Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jsh/adf6157270f535d96810040c16f44a3f/raw/expenses_badge.json)


# expenses_ai_agent

An AI agent that tracks expenses.


## CI/CD

The agent uses some outside services, such as LLMs and currency converters, that requrie user-specific keys.
Requiring these for unit testing or CI/CD is a bad idea for a couple of reasons:

1. These services often require internet access, are sometimes slow, and can cost money for every run.
2. They require secrets that can't be placed into the GitHub repository.

Accordingly the tests are divided into `tests/unit/` and `tests/integration/`. The tests in `tests/unit/` can require no secrets, and can be run with `pytest -m'not integration'`.

 Tests in `tests/integration/` are decorated with `@pytest.mark.integration`, and run with `pytest -m integration`. 

If you fork this repository to run the tests yourself, you can run them locally by copying .env-template to .env and filling in your own values for these keys.

If you want to do integration testing to GitHub Actions, do *not* check in your `.env` file.

1. Change `.github/workflows/ci.yaml` to use `pytest -m integration`
2. Commit your own values for the required keys -- `OPENAI_API_KEY` and `EXCHANGE_RATE_API_KEY` -- as GitHub secrets

You can find and store thes on GitHub, under

```
Settings -> Secreta and variables -> Actions -> New repository secret
```

3. Retrieve those values in `ci.yaml` like this:

```
env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    EXCHANGE_RATE_API_KEY: ${{ secrets.EXCHANGE_RATE_API_KEY }}
```