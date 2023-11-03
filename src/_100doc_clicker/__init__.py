'''
100doc_clicker provides a script that will click its way through
all 100 lessons in Replit's 100 Days of Code Python course
should you so choose.

This package is not intended to be imported.
Regardless, it is fully typed and documented.
Import it at your own risk.
'''

import re
import logging
from collections.abc import Iterable
from enum import Enum
from typing import Any

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import (
	element_to_be_clickable,
	invisibility_of_element,
	visibility_of_element_located
)
from selenium.webdriver.support.wait import WebDriverWait


logging.basicConfig(
	datefmt = '%Y-%m-%d %H:%M:%S',
	encoding = 'utf-8',
	format = '[%(asctime)s.%(msecs)03d]: %(message)s',
	level = logging.INFO
)
_logger = logging.getLogger(__name__)

_issue_tracker_url = 'https://github.com/InSyncWithFoo/100doc-clicker/issues'


def _normalize(text: str) -> str:
	'''
	Strip surrounding whitespace, collapse whitespace sequence
	to single space and convert to lowercase.
	
	:param text: The text to normalize.
	:return: The normalized text.
	'''
	
	stripped = text.strip()
	lowercase = stripped.lower()
	whitespace_collapsed = re.sub(r'\s+', ' ', lowercase)
	
	return whitespace_collapsed


def _get_lesson_number(text: str) -> int:
	'''
	Get the lesson number from a start button's text.
	'''
	
	match = re.search(r'\d+\Z', _normalize(text))
	
	if match is None:
		raise ValueError(
			f'Unexpected text: {text!r}. '
			f'Please report this error at {_issue_tracker_url}.'
		)
	
	return int(match[0])


class CannotAccessHub(RuntimeError):
	pass


class ThisLessonHasAlreadyBeenStarted(RuntimeError):
	pass


class _Selector(str, Enum):
	START_BUTTON = 'button[data-cy="lesson-cta"]'
	CLOSE_SIDEBAR_BUTTON = 'button[data-cy="sidebar-toggle-btn"]'
	SIDEBAR = 'nav[aria-label="sidebar" i]'
	OVERLAY = '.overlay'
	TUTORIAL_PANEL = 'div[data-cy="tutorial-viewer-content"]'
	RUN_BUTTON = 'div[data-cy="ws-run-btn"]'
	DIALOG = 'div[role="dialog"]'
	BACK_TO_HUB_LINK = 'a[href*="100-days-of-python/hub"]'


class _JSScript(str, Enum):
	get_first_header_button = f'''
		const runButton = document.querySelector('{_Selector.RUN_BUTTON}');
		const rightHeader = runButton.nextElementSibling;
		const showTutorialOrMarkAsCompleted = rightHeader.children[0];
		
		return showTutorialOrMarkAsCompleted;
	'''
	checks_if_button_is_show_tutorial_button = r'''
		const button = arguments[0];
		const normalizedButtonText = button.innerText
			.trim().replace(/\s+/g, ' ')
			.toLowerCase();
		
		return normalizedButtonText === 'show tutorial';
	'''
	remove_elements = '''
		[...arguments].forEach(element => element.remove());
	'''
	
	def execute(
		self, driver: WebDriver,
		arguments: Iterable[object] = ()
	) -> Any:
		'''
		Execute the script.
		
		:param driver: The driver that will be used to execute the script.
		:param arguments: Arguments to pass to the script.
		:return: The return value of the script.
		'''
		
		return driver.execute_script(self, *arguments)  # type: ignore


class Clicker:
	'''
	The main class.
	'''
	
	_hub_url = 'https://replit.com/learn/100-days-of-python/hub'
	
	def __init__(
		self, driver: WebDriver, *,
		stop_at: int | None = None
	) -> None:
		'''
		Construct a clicking process from a given driver.
		
		:param driver: The driver to work with.
		:param stop_at: The lesson to stop at.
		'''
		
		self.driver = driver
		self.patiently_wait = WebDriverWait(self.driver, 1000)
		self.stop_at = stop_at
	
	def _get_to_hub(self) -> None:
		'''
		Try to get to the hub and raise a ``RuntimeError``
		if we can't.
		'''
		
		_logger.info(f'Trying to get to hub: {self._hub_url}')
		self.driver.get(self._hub_url)
		
		if self.driver.current_url != self._hub_url:
			_logger.info(f'Current URL: {self.driver.current_url}')
			
			raise CannotAccessHub('Log in or start the course first.')
	
	def _find_element(self, selector: str) -> WebElement | None:
		'''
		Shorthand for ``self.driver.find_element(By.CSS_SELECTOR, selector)``.
		Return ``None`` instead of erring out if the element is not found.
		'''
		
		try:
			return self.driver.find_element(By.CSS_SELECTOR, selector)
		except NoSuchElementException:
			return None
	
	def _load_lesson(self, start_button: WebElement) -> None:
		'''
		Click the start/continue lesson button
		once it is clickable, then wait until
		the sidebar is loaded.
		
		:param start_button: The button to click.
		'''
		
		tutorial_panel_is_visible = visibility_of_element_located(
			(By.CSS_SELECTOR, _Selector.TUTORIAL_PANEL)
		)
		
		_logger.info('Waiting for the start button to be clickable')
		self.patiently_wait.until(element_to_be_clickable(start_button))
		
		_logger.info(f'Loading day {_get_lesson_number(start_button.text)}')
		start_button.click()
		
		timeout = 10
		wait = WebDriverWait(self.driver, timeout)
		
		try:
			_logger.info(f'Waiting for the IDE to load; timeout in {10}s')
			wait.until(invisibility_of_element(start_button))
		except TimeoutException:
			_logger.info(
				'IDE failed to load. Possibly due to a '
				'"This lesson has already been started" error.'
			)
			raise ThisLessonHasAlreadyBeenStarted
		else:
			_logger.info('IDE is loading; waiting for the panel to be loaded')
			self.patiently_wait.until(tutorial_panel_is_visible)
	
	def _close_sidebar_if_it_is_visible(self) -> None:
		'''
		Close the sidebar, in case it forbids us from
		clicking the continue/start lesson button.
		'''
		
		sidebar = self._find_element(_Selector.SIDEBAR)
		
		if sidebar is None:
			logging.info('No sidebar found.')
			return
		
		if sidebar.is_displayed():
			_logger.info('Sidebar is visible')
			_logger.info('Clicking the close button')
			
			close_button = self._find_element(_Selector.CLOSE_SIDEBAR_BUTTON)
			close_button.click()
			
			_logger.info('Waiting for the sidebar to disappear')
			self.patiently_wait.until(invisibility_of_element(sidebar))
		
		if sidebar.is_displayed():
			# This should not happen.
			_logger.info('Close button did not close the sidebar')
			_logger.info('Closing manually using JavaScript')
			
			overlay = self._find_element(_Selector.OVERLAY)
			
			_JSScript.remove_elements.execute(
				self.driver,
				arguments = [sidebar, overlay]
			)
	
	def _mark_lesson_as_completed(self) -> None:
		'''
		Wait until the "Show tutorial" button changes into
		"Mark lesson as completed", then click it.
		'''
		
		leftmost_button_in_header = _JSScript.get_first_header_button \
			.execute(self.driver)
		is_show_tutorial = _JSScript.checks_if_button_is_show_tutorial_button \
			.execute(self.driver, arguments = [leftmost_button_in_header])
		
		if is_show_tutorial:
			_logger.info('Cannot mark as completed just yet; waiting for the button')
			self.patiently_wait.until(
				invisibility_of_element(leftmost_button_in_header)
			)
		
		leftmost_button_in_header.click()
	
	def _get_back_to_hub(self) -> None:
		'''
		Click the "Back to hub" link once the dialog appears.
		'''
		
		dialog_locator = (By.CSS_SELECTOR, _Selector.DIALOG)
		link_locator = (By.CSS_SELECTOR, _Selector.BACK_TO_HUB_LINK)
		
		dialog_is_visible = visibility_of_element_located(dialog_locator)
		
		_logger.info('Waiting for the dialog to be visible')
		self.patiently_wait.until(dialog_is_visible)
		
		dialog = self.driver.find_element(*dialog_locator)
		back_to_hub_link = dialog.find_element(*link_locator)
		
		_logger.info('Getting back to hub')
		back_to_hub_link.click()
	
	def _reached_stop(self, button_text: str) -> bool:
		'''
		If ``stop_at`` was given to :meth:`__init__`,
		check if the current lesson is still smaller than that.
		Else, return whether the button text normalized is
		equals to "completed day 100".
		
		:param button_text: The start button's text.
		'''
		
		if self.stop_at is None:
			return _normalize(button_text) == 'completed day 100'
		
		return _get_lesson_number(button_text) >= self.stop_at
	
	def start(self) -> None:
		'''
		The method that starts the whole process.
		'''
		
		self._get_to_hub()
		
		start_button_locator = (By.CSS_SELECTOR, _Selector.START_BUTTON)
		start_button = self.driver.find_element(*start_button_locator)
		
		while not self._reached_stop(start_button.text):
			self._close_sidebar_if_it_is_visible()
			
			try:
				self._load_lesson(start_button)
			except ThisLessonHasAlreadyBeenStarted:
				continue
			
			self._mark_lesson_as_completed()
			self._get_back_to_hub()
			
			self.patiently_wait.until(
				visibility_of_element_located(start_button_locator)
			)
			start_button = self.driver.find_element(*start_button_locator)
		
		_logger.info('Reached stop; terminating')
