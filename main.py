import time
import csv
import json
import random
import logging
import re
import os
from datetime import datetime
from urllib.parse import quote
from typing import List, Dict, Optional, Union
import sys
import getpass

import pandas as pd

# Try undetected_chromedriver first, fallback to regular selenium
try:
    import undetected_chromedriver as uc

    USE_UC = True
except ImportError:
    from selenium import webdriver

    USE_UC = False

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)


class AdvancedXScraper:
    def __init__(
        self,
        headless: bool = False,
        proxy: Optional[str] = None,
        user_data_dir: Optional[str] = None,
    ):
        self.setup_logging()
        self.setup_driver(headless, proxy, user_data_dir)
        self.comments_data: List[Dict] = []
        self.is_logged_in: bool = False
        self.rate_limit_delay: int = 2
        self.max_retries: int = 3
        self.processed_tweet_ids: set = set()  # Avoid duplicates
        self.config: Dict = {}

    def setup_logging(self) -> None:
        """Setup comprehensive logging with better formatting"""
        log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler
        file_handler = logging.FileHandler("x_scraper.log", encoding="utf-8")
        file_handler.setFormatter(log_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)

        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Suppress some noisy loggers
        logging.getLogger("selenium").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def setup_driver(
        self, headless: bool, proxy: Optional[str], user_data_dir: Optional[str]
    ) -> None:
        """Setup WebDriver with enhanced anti-detection measures"""
        try:
            if USE_UC:
                options = uc.ChromeOptions()
            else:
                from selenium.webdriver.chrome.options import Options

                options = Options()

            # Basic options
            if headless:
                options.add_argument("--headless=new")
            if proxy:
                options.add_argument(f"--proxy-server={proxy}")
            if user_data_dir:
                options.add_argument(f"--user-data-dir={user_data_dir}")

            # Enhanced anti-detection options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")

            # Suppress DevTools and GCM errors
            options.add_argument("--disable-logging")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-background-networking")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("excludeSwitches", ["enable-logging"])

            # Suppress log levels
            options.add_argument("--log-level=3")
            options.add_argument("--silent")

            # Random realistic user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            ]
            options.add_argument(f"--user-agent={random.choice(user_agents)}")

            # Initialize driver
            if USE_UC:
                self.driver = uc.Chrome(options=options, version_main=120)
                # Enhanced stealth mode
                self.driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en', 'id']});
                        Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                        window.chrome = { runtime: {} };
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    """
                    },
                )
                self.logger.info("Undetected Chrome driver initialized successfully")
            else:
                self.driver = webdriver.Chrome(options=options)
                # Basic stealth for regular selenium
                self.driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                self.logger.info("Standard Selenium Chrome driver initialized")

            # Set window size and timeouts
            self.driver.set_window_size(1920, 1080)
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)

        except Exception as e:
            self.logger.error(f"Error setting up driver: {str(e)}")
            raise

    def human_like_delay(self, min_delay: float = 1, max_delay: float = 3) -> None:
        """Human-like delay with random variance"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def human_like_typing(self, element, text: str) -> None:
        """Type text with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def auto_login(self, username: str, password: str) -> bool:
        """
        Automatically login to X (Twitter) using the provided credentials

        Args:
            username (str): Username, email, or phone number
            password (str): Account password

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.logger.info("🔐 Starting automatic login process...")

            # Navigate to login page
            self.driver.get("https://x.com/i/flow/login")
            self.human_like_delay(3, 5)

            # Wait for username/email/phone input field
            self.logger.info("📝 Looking for username input field...")
            username_selectors = [
                'input[name="text"]',
                'input[autocomplete="username"]',
                'input[data-testid="ocfEnterTextTextInput"]',
                '//input[contains(@placeholder, "Phone, email, or username")]',
                '//div[contains(@class, "css-175oi2r")]//input',
            ]

            username_element = None
            for selector in username_selectors:
                try:
                    if selector.startswith("//"):
                        username_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        username_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except TimeoutException:
                    continue

            if not username_element:
                self.logger.error("❌ Could not find username input field")
                return False

            # Clear and enter username
            username_element.clear()
            self.human_like_typing(username_element, username)
            self.human_like_delay(1, 2)

            # Press Enter or click Next button
            try:
                username_element.send_keys(Keys.RETURN)
                self.human_like_delay(2, 3)
            except:
                # Try to find and click Next button
                next_button_selectors = [
                    '//div[@role="button"]//span[text()="Next"]',
                    '//button[@role="button"]//span[text()="Next"]',
                    '[data-testid="LoginForm_Login_Button"]',
                ]

                for selector in next_button_selectors:
                    try:
                        if selector.startswith("//"):
                            next_button = self.driver.find_element(By.XPATH, selector)
                        else:
                            next_button = self.driver.find_element(
                                By.CSS_SELECTOR, selector
                            )
                        next_button.click()
                        break
                    except:
                        continue

                self.human_like_delay(2, 3)

            # Check if we need to handle unusual activity check
            try:
                unusual_activity_elements = self.driver.find_elements(
                    By.XPATH, "//span[contains(text(), 'unusual')]"
                )
                if unusual_activity_elements:
                    self.logger.warning(
                        "⚠️  Unusual activity detected - you may need to verify manually"
                    )
                    time.sleep(5)  # Give user time to handle manually
            except:
                pass

            # Wait for password input field
            self.logger.info("🔑 Looking for password input field...")
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[autocomplete="current-password"]',
                '//input[@type="password"]',
                '//div[contains(@class, "css-175oi2r")]//input[@type="password"]',
            ]

            password_element = None
            for selector in password_selectors:
                try:
                    if selector.startswith("//"):
                        password_element = WebDriverWait(self.driver, 15).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        password_element = WebDriverWait(self.driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except TimeoutException:
                    continue

            if not password_element:
                self.logger.error("❌ Could not find password input field")
                return False

            # Clear and enter password
            password_element.clear()
            self.human_like_typing(password_element, password)
            self.human_like_delay(1, 2)

            # Find and click login button
            self.logger.info("🚀 Clicking login button...")
            login_button_selectors = [
                '[data-testid="LoginForm_Login_Button"]',
                '//div[@role="button"]//span[text()="Log in"]',
                '//button[@role="button"]//span[text()="Log in"]',
                '//div[contains(@class, "css-175oi2r") and contains(@class, "r-sdzlij")]//span[text()="Log in"]',
            ]

            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        login_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )

                    # Scroll button into view and click
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView();", login_button
                    )
                    self.human_like_delay(0.5, 1)
                    login_button.click()
                    login_clicked = True
                    break
                except Exception as e:
                    self.logger.debug(f"Failed to click with selector {selector}: {e}")
                    continue

            if not login_clicked:
                # Fallback: try pressing Enter on password field
                try:
                    password_element.send_keys(Keys.RETURN)
                except:
                    self.logger.error("❌ Could not submit login form")
                    return False

            # Wait for login to complete
            self.logger.info("⏳ Waiting for login to complete...")
            self.human_like_delay(5, 8)

            # Check if login was successful by looking for home page indicators
            max_wait_time = 30
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                current_url = self.driver.current_url.lower()

                # Success indicators
                if any(
                    indicator in current_url
                    for indicator in ["home", "timeline", "/compose"]
                ):
                    self.is_logged_in = True
                    self.logger.info("✅ Login successful! Redirected to home page")
                    self.save_cookies()  # Save session
                    return True

                # Check for login page indicators (failure)
                if any(
                    indicator in current_url
                    for indicator in ["login", "signin", "flow"]
                ):
                    # Check for error messages
                    error_indicators = [
                        "//span[contains(text(), 'Wrong password')]",
                        "//span[contains(text(), 'error')]",
                        "//span[contains(text(), 'incorrect')]",
                        "//div[contains(@data-testid, 'error')]",
                    ]

                    for error_selector in error_indicators:
                        try:
                            error_element = self.driver.find_element(
                                By.XPATH, error_selector
                            )
                            if error_element.is_displayed():
                                self.logger.error(
                                    f"❌ Login failed: {error_element.text}"
                                )
                                return False
                        except:
                            continue

                # Check for 2FA or verification requirements
                verification_indicators = [
                    "//span[contains(text(), 'verification')]",
                    "//span[contains(text(), 'code')]",
                    "//span[contains(text(), 'phone')]",
                    "//input[@placeholder]",
                ]

                for verification_selector in verification_indicators:
                    try:
                        verification_element = self.driver.find_element(
                            By.XPATH, verification_selector
                        )
                        if verification_element.is_displayed():
                            self.logger.warning(
                                "⚠️  Two-factor authentication or verification required"
                            )
                            self.logger.warning(
                                "Please complete verification manually and then continue..."
                            )

                            # Wait for user to complete verification
                            input(
                                "Press Enter after completing verification manually..."
                            )
                            self.human_like_delay(2, 3)

                            # Check again if we're logged in
                            current_url = self.driver.current_url.lower()
                            if any(
                                indicator in current_url
                                for indicator in ["home", "timeline"]
                            ):
                                self.is_logged_in = True
                                self.logger.info(
                                    "✅ Login successful after manual verification!"
                                )
                                self.save_cookies()
                                return True
                    except:
                        continue

                time.sleep(2)

            # Final check
            current_url = self.driver.current_url.lower()
            if any(indicator in current_url for indicator in ["home", "timeline"]):
                self.is_logged_in = True
                self.logger.info("✅ Login successful!")
                self.save_cookies()
                return True
            else:
                self.logger.error(
                    "❌ Login appears to have failed - still on login page"
                )
                return False

        except Exception as e:
            self.logger.error(f"❌ Error during login: {str(e)}")
            return False

    def save_cookies(self, filename: str = "x_cookies.json") -> bool:
        """Save browser cookies for session persistence"""
        try:
            cookies = self.driver.get_cookies()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            self.logger.info(f"Cookies saved to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save cookies: {str(e)}")
            return False

    def load_cookies(self, filename: str = "x_cookies.json") -> bool:
        """Load saved cookies to maintain session"""
        try:
            if not os.path.exists(filename):
                self.logger.info("No saved cookies found")
                return False

            with open(filename, "r", encoding="utf-8") as f:
                cookies = json.load(f)

            self.driver.get("https://x.com")
            self.human_like_delay(2, 3)

            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"Failed to add cookie: {e}")

            self.driver.refresh()
            self.human_like_delay(3, 5)

            # Check if login was successful
            current_url = self.driver.current_url.lower()
            if "home" in current_url or "timeline" in current_url:
                self.is_logged_in = True
                self.logger.info("Successfully logged in using saved cookies")
                return True

        except Exception as e:
            self.logger.error(f"Failed to load cookies: {str(e)}")
        return False

    def wait_for_element(
        self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10
    ) -> Optional[object]:
        """Wait for element with error handling"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found: {selector}")
            return None

    def scroll_and_load_content(self, scroll_pause_time: float = 2) -> int:
        """Intelligent scrolling with content loading detection"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        # Scroll down
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.human_like_delay(scroll_pause_time, scroll_pause_time + 1)

        # Check if new content loaded
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        return new_height - last_height

    def advanced_search_tweets(
        self,
        keyword: str,
        max_tweets: int = 50,
        search_type: str = "latest",
        lang: str = "id",
        date_since: Optional[str] = None,
        date_until: Optional[str] = None,
        min_replies: Optional[int] = None,
        min_likes: Optional[int] = None,
        exclude_replies: bool = False,
        include_retweets: bool = True,
        config: Dict = None,
    ) -> None:
        """Advanced tweet search with comprehensive filtering"""
        self.config = config
        try:
            if not self.is_logged_in:
                self.logger.warning("⚠️  Not logged in - search results may be limited")

            query_parts = [keyword]

            if lang:
                query_parts.append(f"lang:{lang}")
            if date_since:
                query_parts.append(f"since:{date_since}")
            if date_until:
                query_parts.append(f"until:{date_until}")
            if min_replies:
                query_parts.append(f"min_replies:{min_replies}")
            if min_likes:
                query_parts.append(f"min_faves:{min_likes}")
            if exclude_replies:
                query_parts.append("-filter:replies")
            if not include_retweets:
                query_parts.append("-filter:retweets")

            query = " ".join(query_parts)
            encoded_query = quote(query)

            search_url = f"https://x.com/search?q={encoded_query}&src=typed_query"

            search_filters = {
                "latest": "&f=live",
                "top": "&f=top",
                "people": "&f=user",
                "photos": "&f=image",
                "videos": "&f=video",
            }

            if search_type in search_filters:
                search_url += search_filters[search_type]

            self.logger.info(f"Searching tweets with query: {query}")
            self.logger.info(f"Target: {max_tweets} tweets, Type: {search_type}")

            self.driver.get(search_url)
            self.human_like_delay(3, 5)

            tweets_processed = 0
            consecutive_no_new = 0
            scroll_attempts = 0
            max_scroll_attempts = max_tweets // 5 + 10

            while (
                tweets_processed < max_tweets
                and consecutive_no_new < 5
                and scroll_attempts < max_scroll_attempts
            ):
                scroll_attempts += 1
                content_added = self.scroll_and_load_content(2)

                tweets = self.driver.find_elements(
                    By.CSS_SELECTOR, 'article[data-testid="tweet"]'
                )

                if not tweets:
                    self.logger.warning("No tweets found on page")
                    consecutive_no_new += 1
                    continue

                current_count = tweets_processed

                for tweet in tweets:
                    if tweets_processed >= max_tweets:
                        break

                    if self.extract_tweet_data(tweet, keyword):
                        tweets_processed += 1

                    if tweets_processed % 10 == 0 and tweets_processed > 0:
                        self.logger.info(
                            f"Processed {tweets_processed}/{max_tweets} tweets - taking break..."
                        )
                        self.human_like_delay(3, 7)

                if tweets_processed == current_count:
                    consecutive_no_new += 1
                    self.logger.info(
                        f"No new tweets found (attempt {consecutive_no_new}/5)"
                    )
                else:
                    consecutive_no_new = 0

                if tweets_processed > 0 and tweets_processed % 25 == 0:
                    self.logger.info(
                        f"Progress: {tweets_processed}/{max_tweets} tweets collected"
                    )

            self.logger.info(f"Scraping completed! Collected {tweets_processed} tweets")

        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            raise

    def extract_tweet_data(self, tweet_element: object, keyword: str) -> bool:
        """Enhanced tweet data extraction with error handling"""
        try:
            tweet_text = tweet_element.text
            if not tweet_text or "Promoted" in tweet_text or "Ad" in tweet_text:
                return False

            try:
                tweet_links = tweet_element.find_elements(By.CSS_SELECTOR, "time")
                if tweet_links:
                    tweet_url = (
                        tweet_links[0]
                        .find_element(By.XPATH, "./..")
                        .get_attribute("href")
                    )
                    tweet_id = (
                        tweet_url.split("/status/")[-1].split("?")[0]
                        if "/status/" in tweet_url
                        else None
                    )

                    if tweet_id and tweet_id in self.processed_tweet_ids:
                        return False

                    if tweet_id:
                        self.processed_tweet_ids.add(tweet_id)
            except:
                tweet_id = None

            tweet_data = {
                "type": "tweet",
                "scraped_at": datetime.now().isoformat(),
                "keyword": keyword,
                "tweet_id": tweet_id,
            }

            try:
                user_element = tweet_element.find_element(
                    By.CSS_SELECTOR, '[data-testid="User-Name"]'
                )
                user_text = user_element.text.split("\n")

                tweet_data["display_name"] = user_text[0] if user_text else "Unknown"
                tweet_data["username"] = (
                    user_text[1].replace("@", "") if len(user_text) > 1 else "unknown"
                )

                try:
                    profile_link = user_element.find_element(
                        By.CSS_SELECTOR, "a"
                    ).get_attribute("href")
                    tweet_data["profile_link"] = profile_link
                except:
                    tweet_data["profile_link"] = (
                        f"https://x.com/{tweet_data['username']}"
                    )

            except Exception as e:
                tweet_data.update(
                    {
                        "display_name": "Unknown",
                        "username": "unknown",
                        "profile_link": "",
                    }
                )

            try:
                text_elements = tweet_element.find_elements(
                    By.CSS_SELECTOR, '[data-testid="tweetText"]'
                )
                if text_elements:
                    tweet_data["tweet_text"] = text_elements[0].text
                else:
                    tweet_data["tweet_text"] = (
                        tweet_text.split("\n")[2:]
                        if len(tweet_text.split("\n")) > 2
                        else [""]
                    )
                    tweet_data["tweet_text"] = (
                        "\n".join(tweet_data["tweet_text"])
                        if isinstance(tweet_data["tweet_text"], list)
                        else ""
                    )
            except:
                tweet_data["tweet_text"] = ""

            try:
                time_element = tweet_element.find_element(By.CSS_SELECTOR, "time")
                tweet_data["timestamp"] = time_element.get_attribute("datetime")

                link_element = time_element.find_element(By.XPATH, "./..")
                tweet_data["tweet_link"] = link_element.get_attribute("href")
            except:
                tweet_data.update({"timestamp": "", "tweet_link": ""})

            try:
                reply_elements = tweet_element.find_elements(
                    By.CSS_SELECTOR, '[data-testid="reply"]'
                )
                tweet_data["replies"] = (
                    reply_elements[0].text
                    if reply_elements and reply_elements[0].text
                    else "0"
                )

                retweet_elements = tweet_element.find_elements(
                    By.CSS_SELECTOR, '[data-testid="retweet"]'
                )
                tweet_data["retweets"] = (
                    retweet_elements[0].text
                    if retweet_elements and retweet_elements[0].text
                    else "0"
                )

                like_elements = tweet_element.find_elements(
                    By.CSS_SELECTOR, '[data-testid="like"]'
                )
                tweet_data["likes"] = (
                    like_elements[0].text
                    if like_elements and like_elements[0].text
                    else "0"
                )

            except:
                tweet_data.update({"replies": "0", "retweets": "0", "likes": "0"})

            if tweet_data["tweet_text"] or tweet_data["username"] != "unknown":
                self.comments_data.append(tweet_data)
                return True

        except StaleElementReferenceException:
            self.logger.warning("Stale element encountered, skipping...")
        except Exception as e:
            self.logger.warning(f"Error extracting tweet data: {str(e)}")

        return False

    def _generate_summary(self) -> Dict:
        """Helper to generate a clean summary dictionary."""
        if not self.comments_data:
            return {"message": "No data collected"}

        unique_users = set(
            [
                item["username"]
                for item in self.comments_data
                if item.get("username") and item["username"] != "unknown"
            ]
        )
        keywords = list(
            set([item["keyword"] for item in self.comments_data if item.get("keyword")])
        )

        dates = [
            item["scraped_at"] for item in self.comments_data if item.get("scraped_at")
        ]
        date_range = (
            {"start": min(dates), "end": max(dates)}
            if dates
            else {"start": None, "end": None}
        )

        formatted_config = {
            "keyword": self.config.get("keyword"),
            "max_tweets": self.config.get("max_tweets"),
            "search_type": self.config.get("search_type"),
            "language": self.config.get("language"),
            "date_since": self.config.get("date_since"),
            "date_until": self.config.get("date_until"),
        }

        summary = {
            "scraper_version": "1.0.0",
            "scraping_time": datetime.now().isoformat(),
            "search_parameters": formatted_config,
            "results_summary": {
                "total_tweets_collected": len(self.comments_data),
                "unique_users_found": len(unique_users),
                "scraped_date_range": date_range,
                "searched_keywords": keywords,
            },
        }
        return summary

    def export_to_multiple_formats(
        self, base_filename: str = "x_results"
    ) -> Dict[str, str]:
        """Export data to multiple formats with better error handling and summary inclusion"""
        if not self.comments_data:
            self.logger.warning("No data to export")
            return {}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}

        summary_data = self._generate_summary()
        export_data = {"summary": summary_data, "tweets": self.comments_data}

        try:
            # JSON Export
            json_file = f"{base_filename}_{timestamp}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            exported_files["json"] = json_file

            # Excel Export
            try:
                xlsx_file = f"{base_filename}_{timestamp}.xlsx"
                writer = pd.ExcelWriter(xlsx_file, engine="xlsxwriter")

                # Create DataFrame for tweets
                df = pd.DataFrame(self.comments_data)

                # Sheet: Tweets (Data Mentah)
                df.to_excel(writer, sheet_name="Tweets", index=False)

                # Get the xlsxwriter workbook and worksheet objects.
                workbook = writer.book
                worksheet_tweets = writer.sheets["Tweets"]

                # Apply column auto-width
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet_tweets.set_column(i, i, max_len)

                # Sheet: Summary (Ringkasan)
                summary_df = pd.DataFrame.from_dict(summary_data, orient="index").T
                summary_df.to_excel(writer, sheet_name="Summary")

                # Get summary sheet object
                worksheet_summary = writer.sheets["Summary"]

                # Apply column auto-width for summary
                for i, col in enumerate(summary_df.columns):
                    max_len = (
                        max(summary_df[col].astype(str).map(len).max(), len(col)) + 2
                    )
                    worksheet_summary.set_column(i, i, max_len)

                writer.close()
                exported_files["xlsx"] = xlsx_file
            except Exception as e:
                self.logger.warning(f"Could not export to Excel: {e}")

            # CSV Export
            csv_file = f"{base_filename}_{timestamp}.csv"
            df = pd.DataFrame(self.comments_data)

            header_lines = [
                f"# X Scraping Report\n",
                f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                f"# Keyword: {summary_data['search_parameters']['keyword']}\n",
                f"# Total Tweets: {summary_data['results_summary']['total_tweets_collected']}\n",
                f"# Date Range: {summary_data['results_summary']['scraped_date_range']['start']} to {summary_data['results_summary']['scraped_date_range']['end']}\n",
                "#\n",
            ]

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                f.writelines(header_lines)
                df.to_csv(f, index=False, encoding="utf-8")
            exported_files["csv"] = csv_file

            self.logger.info(f"Data exported to: {', '.join(exported_files.values())}")

        except Exception as e:
            self.logger.error(f"Error during export: {str(e)}")

        return exported_files

    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return self._generate_summary()

    def save_session(self) -> None:
        """Save session data including cookies and login status"""
        try:
            session_data = {
                "is_logged_in": self.is_logged_in,
                "last_login": datetime.now().isoformat(),
                "processed_tweets": len(self.processed_tweet_ids),
            }

            with open("session_data.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2)

            if self.is_logged_in:
                self.save_cookies()

        except Exception as e:
            self.logger.error(f"Error saving session: {e}")

    def close(self) -> None:
        """Clean up resources"""
        try:
            if hasattr(self, "driver"):
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing driver: {e}")


def get_login_credentials() -> Dict[str, str]:
    """Securely get login credentials from user"""
    print("\n🔐 LOGIN CREDENTIALS")
    print("=" * 30)

    username = input("Username/Email/Phone: ").strip()
    if not username:
        print("❌ Username is required!")
        sys.exit(1)

    password = getpass.getpass("Password: ").strip()
    if not password:
        print("❌ Password is required!")
        sys.exit(1)

    return {"username": username, "password": password}


def get_user_input() -> Dict:
    """Get user configuration with validation"""
    print("=== ADVANCED X (TWITTER) SCRAPER ===")
    print("Enhanced version with automatic login and better error handling\n")

    config = {}

    login_choice = input(
        "Do you want to login automatically? (y/n, default: y): "
    ).lower()
    if login_choice != "n":
        config["auto_login"] = True
        config.update(get_login_credentials())
    else:
        config["auto_login"] = False
        print("⚠️  Note: Some search features may be limited without login")

    config["headless"] = (
        input("\nRun in headless mode? (y/n, default: n): ").lower().startswith("y")
    )
    config["proxy"] = (
        input("Use proxy? (format: ip:port, leave empty for none): ").strip() or None
    )

    print("\n📊 SEARCH PARAMETERS")
    print("=" * 25)
    config["keyword"] = input("Enter search keyword: ").strip()
    if not config["keyword"]:
        print("Error: Keyword is required!")
        sys.exit(1)

    try:
        config["max_tweets"] = int(
            input("Number of tweets to collect (default: 50): ") or 50
        )
    except ValueError:
        config["max_tweets"] = 50

    config["search_type"] = (
        input(
            "Search type (latest/top/people/photos/videos, default: latest): "
        ).strip()
        or "latest"
    )
    config["language"] = (
        input("Language filter (default: id for Indonesian): ").strip() or "id"
    )

    print("\n🔍 ADVANCED FILTERS (optional)")
    print("=" * 35)
    config["date_since"] = input("Date since (YYYY-MM-DD, optional): ").strip() or None
    config["date_until"] = input("Date until (YYYY-MM-DD, optional): ").strip() or None

    try:
        min_likes = input("Minimum likes (optional): ").strip()
        config["min_likes"] = int(min_likes) if min_likes else None
    except ValueError:
        config["min_likes"] = None

    try:
        min_replies = input("Minimum replies (optional): ").strip()
        config["min_replies"] = int(min_replies) if min_replies else None
    except ValueError:
        config["min_replies"] = None

    config["exclude_replies"] = (
        input("Exclude replies? (y/n, default: n): ").lower().startswith("y")
    )
    config["include_retweets"] = (
        not input("Exclude retweets? (y/n, default: n): ").lower().startswith("y")
    )

    return config


def main():
    """Main function with comprehensive error handling"""
    scraper = None
    try:
        config = get_user_input()

        print(f"\n🚀 STARTING SCRAPER")
        print("=" * 50)
        print(f"- Keyword: {config['keyword']}")
        print(f"- Max tweets: {config['max_tweets']}")
        print(f"- Search type: {config['search_type']}")
        print(f"- Language: {config['language']}")
        print(f"- Auto-login: {'Yes' if config.get('auto_login') else 'No'}")
        print(f"- Headless: {config['headless']}")
        if config["proxy"]:
            print(f"- Proxy: {config['proxy']}")
        print("=" * 50)

        print("\n🔧 Initializing browser...")
        scraper = AdvancedXScraper(headless=config["headless"], proxy=config["proxy"])

        if config.get("auto_login"):
            print("\n🔐 Starting login process...")

            if not scraper.load_cookies():
                login_success = scraper.auto_login(
                    config["username"], config["password"]
                )

                if not login_success:
                    print("❌ Auto-login failed!")
                    choice = input("Continue without login? (y/n): ").lower()
                    if choice != "y":
                        print("Exiting...")
                        return
                    else:
                        print("⚠️  Continuing without login - results may be limited")
        else:
            print("\n🍪 Checking for saved session...")
            scraper.load_cookies()

        print("\n🕷️ Starting tweet collection...")
        print("This may take a while depending on your settings...\n")

        scraper.advanced_search_tweets(
            keyword=config["keyword"],
            max_tweets=config["max_tweets"],
            search_type=config["search_type"],
            lang=config["language"],
            date_since=config["date_since"],
            date_until=config["date_until"],
            min_likes=config["min_likes"],
            min_replies=config["min_replies"],
            exclude_replies=config["exclude_replies"],
            include_retweets=config["include_retweets"],
            config=config,
        )

        stats = scraper.get_stats()
        print(f"\n{'='*50}")
        print("🎉 SCRAPING COMPLETED!")
        print(f"{'='*50}")
        if "results_summary" in stats:
            summary_res = stats["results_summary"]
            print(f"✅ Total tweets collected: {summary_res['total_tweets_collected']}")
            print(f"✅ Unique users: {summary_res['unique_users_found']}")
            print(
                f"✅ Keywords searched: {', '.join(summary_res['searched_keywords'])}"
            )

        if scraper.comments_data:
            print("\n💾 Exporting data...")
            exported = scraper.export_to_multiple_formats("x_scraping_results")
            if exported:
                print("✅ Files exported:")
                for format_type, filename in exported.items():
                    print(f"   - {format_type.upper()}: {filename}")
        else:
            print("\n❌ No data collected.")
            print("\n💡 Possible reasons:")
            print("   - Search query returned no results")
            print("   - Rate limiting is active")
            print("   - Login required for this type of search")
            print("   - Network connectivity issues")

            if not config.get("auto_login"):
                print("   - Try enabling auto-login for better results")

            if config.get("headless"):
                print("   - Try running in non-headless mode for debugging")

        print("\n💾 Saving session data...")
        scraper.save_session()

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")

        if scraper and scraper.comments_data:
            print("💾 Saving collected data before exit...")
            try:
                scraper.export_to_multiple_formats("interrupted_save")
                print("✅ Data saved successfully")
            except:
                print("❌ Failed to save data")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print(f"📋 Error type: {type(e).__name__}")
        logging.exception("Detailed error traceback:")

        if scraper and scraper.comments_data:
            print("💾 Attempting emergency save of collected data...")
            try:
                scraper.export_to_multiple_formats("emergency_save")
                print("✅ Emergency save completed")
            except:
                print("❌ Emergency save failed")

    finally:
        if scraper:
            print("\n🔧 Cleaning up browser...")
            scraper.close()

        print(f"\n{'='*50}")
        print("👋 Thanks for using Advanced X Scraper!")
        print(f"{'='*50}")
        print("💡 Troubleshooting tips:")
        print("   - Check logs in 'x_scraper.log' for detailed error info")
        print("   - Try running without headless mode for debugging")
        print("   - Ensure stable internet connection")
        print("   - Update Chrome browser to latest version")
        if config.get("auto_login"):
            print("   - Verify your login credentials are correct")
        print("   - Consider using different search keywords or filters")


if __name__ == "__main__":
    main()
