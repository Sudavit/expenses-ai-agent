![GitHub Release](https://img.shields.io/github/v/tag/Sudavit/expenses-ai-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/jsh/trendlist/blob/master/LICENSE)
![Pytest Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jsh/adf6157270f535d96810040c16f44a3f/raw/expenses_badge.json)


# expenses_ai_agent

An AI agent that tracks expenses.


## CI/CD

The agent needs both OPENAI_API_KEY and EXCHANGE_RATE_API_KEY to run successfully. Without these in the environment, it can't function.
Putting these into the repository for everyone to see is a bad idea. 
To put these into the environment for CI/CD on GitHub, under GitHub Actions, they need to be GitHub secrets.

If you fork this repository to run the tests yourself, you can run them locally by copying .env-template to .env and filling in your own values for these keys.
To do CI/CD on GitHub actions yourself, you also need to make them GitHub Secrets.
Once that's done, `.github/workflow/ci.yaml` will retrieve these values and place them in the environment during each CI/CD run.

To add them as secrets, go to your repository on GitHub, then

"""
Settings -> Secreta and variables -> Actions -> New repository secret
"""
