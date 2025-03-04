# Demonstrates the two ways to run Playwright (prerecorded script or "manual")

# Notes:
# Dont forget to first install the browsers by running: playwright install
# Browsers are heavy. Dont expect to be able to do as much load as usual with Locust. Optimize your tests by blocking requests for unnecessary resources.
# Dont run too many users per worker instance (or you'll get the dreaded "CPU usage over 90%" warning). Instead, scale using more Locust workers. 4-5 users/browsers per workers seems ok. If you are using locust-swarm, increase the --processes-per-loadgen parameter.
# Some things, such as adding request callbacks (Page.route()), will cause intense communication with the browser will overload Python/Playwright so be careful.
# It is easy to accidentally make Playwright tests stall for a long time, for example if your page does finish loading completely (triggering the "load" event). Experiment with alternative wait strategies (e.g. wait_until="domcontentloaded" or self.page.wait_for_selector(...))


from locust import run_single_user, task
from locust_plugins.users.playwright import PageWithRetry, PlaywrightUser, PlaywrightScriptUser, pw, event


class ScriptBased(PlaywrightScriptUser):
    # run a script that you recorded in playwright, exported as Python Async
    script = "playwright-recording.py"


class Manual(PlaywrightUser):
    host = "https://www.google.com"
    multiplier = 10  # run ten concurrent playwright sessions/browsers for each Locust user. This helps improve load generation efficiency.

    @task
    @pw
    async def google(self, page: PageWithRetry):
        try:
            async with event(self, "Load up google"):  # log this as an event
                await page.goto("/")  # load a page

            async with event(self, "Approve terms and conditions"):
                async with page.expect_navigation(wait_until="domcontentloaded"):
                    await page.click('button:has-text("Jag godkänner")')  # Click "I approve" in swedish...
                    # sometimes even Playwright has issues with stability (especially under high load)
                    await page.click_retry('[aria-label="Sök"]', retries=1)
        except:
            pass


if __name__ == "__main__":
    run_single_user(Manual)
