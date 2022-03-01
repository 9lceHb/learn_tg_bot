-include .env
export

lint:
	@flake8 bot
	@mypy bot

run:
	@python -m bot
