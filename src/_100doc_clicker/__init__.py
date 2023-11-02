'''
100doc_clicker provides a script that will click its way through
all 100 lessons in Replit's 100 Days of Code Python course
should you so choose.

This package is not intended to be imported.
Regardless, it is fully typed and documented.
Import it at your own risk.
'''

import re
from collections.abc import Iterable
from enum import Enum
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import (
	element_to_be_clickable,
	invisibility_of_element,
	visibility_of_element_located
)
from selenium.webdriver.support.wait import WebDriverWait


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


class _Selector(str, Enum):
	START_BUTTON = 'button[data-cy="lesson-cta"]'
	SIDEBAR = 'div[data-cy="tutorial-viewer-content"]'
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
		self.wait = WebDriverWait(self.driver, 1000)
		self.stop_at = stop_at
	
	def _find_element(self, selector: str) -> WebElement:
		'''
		Shorthand for ``self.driver.find_element(By.CSS_SELECTOR, selector)``.
		'''
		
		return self.driver.find_element(By.CSS_SELECTOR, selector)
	
	def _load_lesson(self, start_button: WebElement) -> None:
		'''
		Click the start/continue lesson button
		once it is clickable, then wait until
		the sidebar is loaded.
		
		:param start_button: The button to click.
		'''
		
		sidebar_is_visible = visibility_of_element_located(
			(By.CSS_SELECTOR, _Selector.SIDEBAR)
		)
		
		self.wait.until(element_to_be_clickable(start_button))
		start_button.click()
		
		self.wait.until(sidebar_is_visible)
	
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
			self.wait.until(invisibility_of_element(leftmost_button_in_header))
		
		leftmost_button_in_header.click()
	
	def _get_back_to_hub(self) -> None:
		'''
		Click the "Back to hub" link once the dialog appears.
		'''
		
		dialog_locator = (By.CSS_SELECTOR, _Selector.DIALOG)
		link_locator = (By.CSS_SELECTOR, _Selector.BACK_TO_HUB_LINK)
		
		dialog_is_visible = visibility_of_element_located(dialog_locator)
		
		self.wait.until(dialog_is_visible)
		
		dialog = self.driver.find_element(*dialog_locator)
		back_to_hub_link = dialog.find_element(*link_locator)
		
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
			return _normalize(button_text) != 'completed day 100'
		
		return _get_lesson_number(button_text) < self.stop_at
	
	def start(self) -> None:
		'''
		The method that starts the whole process.
		'''
		
		self.driver.get(self._hub_url)
		
		start_button_locator = (By.CSS_SELECTOR, _Selector.START_BUTTON)
		start_button = self.driver.find_element(*start_button_locator)
		
		while not self._reached_stop(start_button.text):
			self._load_lesson(start_button)
			self._mark_lesson_as_completed()
			self._get_back_to_hub()
			
			self.wait.until(visibility_of_element_located(start_button_locator))
			start_button = self.driver.find_element(*start_button_locator)
