# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.4] - 2021-01-07
- Minor compatibility fix with Selenium 4
- Slight performance improvements
- Replaced several list typehints with more appropriate versions

## [0.11.3] - 2020-12-29
- Massive performance enhancements, especially in headless mode

## [0.11.2] - 2020-12-28
- Updated user agents, split firefox into firefox_desktop and firefox_mobile
- Added WaitForElement action
- Fixed bug in Refresh action
- Now performs basic validation of config inputs
- Prints browser and webdriver versions on startup
- Added config settings for javascript log level
- Added sort_by methods to Elements and Actions to simplify sorting by score

## [0.11.1] - 2020-12-17
- Added local_text entry in element metadata for text specific to that element

## [0.11] - 2020-12-17
- Fixed bug when taking a full page screenshot of a size that's a non-multiple of the viewport height
- Added basic Firefox support
- Replaced "commit_hash" entry in page metadata with "wtl_version"
- Much improved documentation

## [0.10.1] - 2020-10-13
- Added a scraping.history setting for constant memory footprint at the cost of not being able to reset
- Support for Python 3.9

## [0.10] - 2020-10-09
- Performance boost when using multiple tabs
- Rewrote documentation system, now based on modern Sphinx
- Fixed a bug where deep config settings couldn't be updated with dot syntax
- Added a scraping.preserve_full_history setting to (slightly) reduce memory footprint

## [0.9] - 2020-07-08
First open-source release, everything is subject to change!
