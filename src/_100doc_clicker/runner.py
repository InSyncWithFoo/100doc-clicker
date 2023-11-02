'''
The main script of 100doc_clicker.
Only supports Chrome.
'''

from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException

from . import Clicker


def _make_parser():
	parser = ArgumentParser()
	parser.add_argument(
		'-r', '--dry-run',
		action = BooleanOptionalAction,
		help = 'Dry run. For debugging.'
	)
	parser.add_argument(
		'-s', '--stop-at',
		type = int,
		help = 'The lesson to stop at. Defaults to None (run through 100).'
	)
	
	subparsers = parser.add_subparsers(help = 'The webdriver type to use')
	
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
	
	return parser


def _make_chrome_driver(args):
	options = webdriver.ChromeOptions()
	options.add_argument('--no-sandbox')
	options.add_argument(f'--user-data-dir={args.user_data_directory}')
	options.add_argument(f'--profile-directory={args.profile_directory}')
	
	return webdriver.Chrome(options)


def _make_firefox_driver(args):
	options = webdriver.FirefoxOptions()
	options.profile = webdriver.FirefoxProfile(args.profile_directory)
	
	return webdriver.Firefox(options)


def _run_clicker(driver, stop_at):
	try:
		Clicker(driver, stop_at = stop_at).start()
	except UnexpectedAlertPresentException:
		# Ignore "You have unsaved changes" alerts.
		_run_clicker(driver, stop_at)

def main():
	parser = _make_parser()
	args = parser.parse_args()
	
	driver = None
	
	if args.dry_run:
		print(args.__dict__)
		return
	
	match args.driver:
		case 'chrome':
			driver = _make_chrome_driver(args)
		
		case 'firefox':
			driver = _make_firefox_driver(args)
	
	_run_clicker(driver, args.stop_at)


if __name__ == '__main__':
	main()
