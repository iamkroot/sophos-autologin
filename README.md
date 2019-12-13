# Sophos/Cyberoam Autologin

A Python script to cycle through multiple Sophos/Cyberoam accounts to ensure continuous internet connection, once the data cap is exhausted.

## Installing
1. Clone/Download this repo.
2. Install Python 3.6 or higher.
3. Install Poetry for Python. Reboot.
4. Run `poetry install` in project directory in a terminal.

## Configuration
1. Create a simple CSV file with usernames and passwords of the accounts to be used. Eg:
	```csv
	login1,pwd1
	login2,pwd2
	login3,pwd3
	``` 
2. Rename `sample_config.toml` to `config.toml` and edit the appropriate values.

## Running
In a shell in the project directory, just run `poetry run python autologin.py`.

## Authors
[iamkroot](https://github.com/iamkroot)
