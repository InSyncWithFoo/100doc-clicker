from collections.abc import Sequence
from pathlib import Path

import pytest

from _100doc_clicker import runner


def parse_arguments(arguments: Sequence[str]):
	parsed = runner.parse_arguments(arguments)
	
	return parsed.__dict__


def arguments_have_form(arguments, form):
	for key, value_or_type in form.items():
		if isinstance(value_or_type, type):
			assert isinstance(arguments[key], value_or_type)
		else:
			assert arguments[key] == value_or_type
	
	return True

@pytest.mark.parametrize('driver, expected', [
	('chrome', {'driver': 'chrome'}),
	('firefox', {'driver': 'firefox'}),
	('c', {'driver': 'c'}),
	('f', {'driver': 'f'})
])
def test_driver_names(driver, expected):
	parsed = parse_arguments([driver])
	
	assert arguments_have_form(parsed, expected)


@pytest.mark.parametrize('driver', [
	'brave',
	'chromium',
	'edge',
	'ie',
	'opera',
	'safari',
	'vivaldi'
])
def test_invalid_driver_names(driver):
	with pytest.raises(SystemExit):
		parse_arguments([driver])


@pytest.mark.parametrize('stop_at, expected', [
	('100', {'stop_at': 100}),
	('0', {'stop_at': 0}),
	('-14', {'stop_at': -14})
])
def test_stop_at(stop_at, expected):
	parsed = parse_arguments(['-s', stop_at])
	
	assert arguments_have_form(parsed, expected)


@pytest.mark.parametrize('stop_at', [
	'42.43',
	'nan',
	'inf',
	'foo',
	'21lorem',
	'1e4'
])
def test_invalid_stop_at(stop_at):
	with pytest.raises(SystemExit):
		parse_arguments(['-s', stop_at])


@pytest.mark.parametrize('driver, driver_arguments, expected', [
	(
		'chrome', ['-d', 'lorem/ipsum', '-p', 'bar'],
		{'user_data_directory': Path, 'profile_directory': Path}
	),
	(
		'firefox', ['-p', 'lorem/ipsum/dolor/sit/amet'],
		{'profile_directory': Path}
	)
])
def test_driver_arguments(driver, driver_arguments, expected):
	parsed = parse_arguments([driver, *driver_arguments])
	
	assert arguments_have_form(parsed, expected)


@pytest.mark.parametrize('driver, driver_arguments', [
	('chrome', ['-z']),
	('firefox', ['-d', 'consectetur/adipiscing'])
])
def test_invalid_driver_arguments(driver, driver_arguments):
	with pytest.raises(SystemExit):
		parse_arguments([driver, *driver_arguments])
