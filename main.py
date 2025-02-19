import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import pytz

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class WhatsAppBot:
    LONG_SLEEP = 5
    SHORT_SLEEP = 2
    def __init__(self, profile_path):
        logger.info('Initializing WhatsAppBot')
        self.BASE_URL = "https://web.whatsapp.com/"
        self.browser = self._setup_browser(profile_path)
        logger.info('Initialization completed')
        
    def _setup_browser(self, profile_path):
        """Initialize Firefox browser with custom options"""
        options = self._configure_firefox_options(profile_path)
        return webdriver.Firefox(options=options)
    
    def _configure_firefox_options(self, profile_path):
        """Configure Firefox browser options"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--profile")
        options.add_argument(profile_path)
        return options
    
    def click_button(self, xpath, by, wait_time=10):
        """Click button with specified xpath"""
        logger.info(f'Attempting to click button: {xpath}, {by}')
        try:
            btn = WebDriverWait(self.browser, wait_time).until(
                EC.element_to_be_clickable((by, xpath))
            )
            time.sleep(self.SHORT_SLEEP)
            btn.click()
            time.sleep(self.LONG_SLEEP)
            logger.info('Button clicked successfully')
        except Exception as e:
            logger.error(f'Button not found {xpath}: {e}')
            raise Exception(f'Button not found {xpath}: {e}')

    def find_input_box(self):
        """Find the message input box"""
        possible_xpaths = ['//div[@contenteditable="true"][@data-tab="10"]']
        
        for xpath in possible_xpaths:
            try:
                input_box = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if input_box:
                    return input_box
            except:
                continue
        return None

    def perform_action(self, node, message):
        logger.info(f'Performing action with message: {message}')
        actions = ActionChains(self.browser)
        actions.move_to_element(node)
        actions.click()
        actions.pause(1)
        actions.send_keys(message)
        actions.pause(1)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        logger.info("Action performed successfully")

    def create_poll(self, group_link, question, options):
        """Create a poll in WhatsApp group"""
        try:
            logger.info('Starting poll creation process')
            # Navigate to WhatsApp Web
            self.browser.get(self.BASE_URL)

            self.browser.get(group_link)
            time.sleep(self.LONG_SLEEP)
            
            # Join group
            self.click_button("//*[contains(text(), 'Join Chat')]", By.XPATH)
            self.click_button("//*[contains(text(), 'use WhatsApp Web')]", By.XPATH)

            # Click attach then poll
            self.click_button("button[title='Attach']", By.CSS_SELECTOR, 20)
            self.click_button("//span[contains(text(), 'Poll')]", By.XPATH)

            # Get poll textboxes
            textboxes = WebDriverWait(self.browser, 10).until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, 
                    "div[role='textbox'][contenteditable='true']"
                ))
            )

            # Enter poll question and options
            self.perform_action(textboxes[0], question)
            self.perform_action(textboxes[1], options[0])
            self.perform_action(textboxes[2], options[1])

            # Allow only one vote
            self.click_button("div[role='switch'][aria-checked='true']", By.CSS_SELECTOR)

            # Click create button
            self.click_button("div[aria-label='Send']", By.CSS_SELECTOR)
            time.sleep(self.LONG_SLEEP)

            logger.info('Poll created successfully')
            
        except Exception as e:
            logger.error(f"Error creating poll: {e}")
            raise e
        finally:
            self.quit()

    def quit(self):
        """Close the browser"""
        self.browser.quit()
        logger.info('Browser closed')

def execute():
    logger.info('Starting job')
    # Configuration
    PROFILE_PATH = "YOUR_PATH"
    GROUP_LINK = "YOUR_GROUP"
    
    # Poll details
    timezone = pytz.timezone('Africa/Cairo')  
    QUESTION = f"[Auto] Gym {datetime.datetime.now(timezone).strftime('%d/%m')}" 
    OPTIONS = ["Yes", "No"]

    # Initialize and run bot
    bot = WhatsAppBot(PROFILE_PATH)
    bot.create_poll(GROUP_LINK, QUESTION, OPTIONS)
    logger.info('Job done')

def main():
    executions =0
    while executions<3:
        executions += 1
        logger.info(f"Starting execution number {executions}")
        try:
            execute()
            logger.info(f"Execution {executions} completed successfully")
            break
        except Exception as e:
            logger.error(f"Error in execution {executions}: {e}")
    
    

if __name__ == "__main__":
    main()
