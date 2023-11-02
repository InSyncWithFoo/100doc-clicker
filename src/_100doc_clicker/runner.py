'''
The main script of 100doc_clicker.
Only supports Chrome.
'''
import sys
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException

from . import Clicker


def parse_arguments(arguments):
	parser = ArgumentParser()
	parser.add_argument(
		'-r', '--dry-run',
		action = BooleanOptionalAction,
		help = 'Dry run. For debugging.'
	)
	parser.add_argument(
		'-s', '--stop-at',
		type = int,
		help = (
			'The lesson to stop at (1 <= s <= 100). '
			'Defaults to None (run through 100).'
		)
	)
	
	subparsers = parser.add_subparsers(
		help = 'The webdriver type to use',
		dest = 'driver'
	)
	
	chrome_parser = subparsers.add_parser('chrome', aliases = ['c'])
	chrome_parser.add_argument(
		'-d', '--user-data-directory',
		type = Path,
		help = 'The directory that contains your user data.'
	)
	chrome_parser.add_argument(
		'-p', '--profile-directory',
		type = Path,
		help = (
			'The profile directory. It should be '
			'relative to/a child of USER_DATA_DIRECTORY.'
		)
	)
	
	firefox_parser = subparsers.add_parser('firefox', aliases = ['f'])
	firefox_parser.add_argument(
		'-p', '--profile-directory',
		type = Path,
		help = 'The profile directory.'
	)
	
	return parser.parse_args(arguments)


def _make_chrome_driver(arguments):
	options = webdriver.ChromeOptions()
	options.add_argument('--no-sandbox')
	options.add_argument(f'--user-data-dir={arguments.user_data_directory}')
	options.add_argument(f'--profile-directory={arguments.profile_directory}')
	
	if arguments.dry_run:
		print(f'{options._arguments = }')
		return
	
	return webdriver.Chrome(options)


def _make_firefox_driver(arguments):
	options = webdriver.FirefoxOptions()
	options.profile = webdriver.FirefoxProfile(arguments.profile_directory)
	
	if arguments.dry_run:
		print(f'{options._arguments = }')
		return
	
	return webdriver.Firefox(options)


def _run_clicker(driver, stop_at):
	try:
		Clicker(driver, stop_at = stop_at).start()
	except UnexpectedAlertPresentException:
		# Ignore "You have unsaved changes" alerts.
		_run_clicker(driver, stop_at)


def main():
	arguments = parse_arguments(sys.argv[1:])
	
	if arguments.dry_run:
		print(f'{arguments = }')
	
	match arguments.driver:
		case 'chrome' | 'c':
			driver = _make_chrome_driver(arguments)
		
		case 'firefox' | 'f':
			driver = _make_firefox_driver(arguments)
		
		case _:
			raise ValueError(f'Unexpected argument: {arguments.driver}')
	
	if arguments.dry_run:
		return
	
	_run_clicker(driver, arguments.stop_at)


if __name__ == '__main__':
	main()
