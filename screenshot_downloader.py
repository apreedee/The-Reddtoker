from pathlib import Path
from typing import Final

from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
from rich.progress import track


"""
This is a modified and edited form of a file made on github by
Lewis Menelaws & TMRRW. 
The Original file is at:
https://github.com/elebumm/RedditVideoMakerBot/blob/master/video_creation/screenshot_downloader.py
"""

__all__ = ["download_screenshots_of_reddit_posts"]


def get_screenshots_of_reddit_posts(
    reddit_object: dict,
    screenshot_num: int,
    WIDTH: int,
    HEIGHT: int,
    PATH: str,
    USERNAME: str,
    PASSWORD: str,
    max_screenshots_available_fullfilled_value: bool,
    verbose,
):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to PATH/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """
    # settings values
    W: Final[int] = WIDTH
    H: Final[int] = HEIGHT

    if verbose:
        print("Downloading screenshots of reddit posts...")
    reddit_id = reddit_object["thread_id"]
    # ! Make sure the reddit screenshots folder exists
    Path(f"{PATH}/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        if verbose:
            print("Launching Headless Browser...")

        browser = p.chromium.launch(
            headless=True
        )  # headless=False will show the browser for debugging purposes
        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # so we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        dsf = (W // 600) + 1

        context = browser.new_context(
            locale="en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf,
        )

        # Login to Reddit
        if verbose:
            print("Logging in to Reddit...")
        page = context.new_page()
        page.goto("https://www.reddit.com/login", timeout=0)
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        page.wait_for_load_state()

        if verbose:
            print(" -- 1")
        # Filling in login details
        page.locator('[name="username"]').fill(USERNAME)
        page.locator('[name="password"]').fill(PASSWORD)
        page.locator("button[class$='m-full-width']").click()
        page.wait_for_timeout(5000)

        if verbose:
            print(" -- 2")
        # Get the thread for the screenshot
        page.goto(reddit_object["thread_url"], timeout=0)
        page.set_viewport_size(ViewportSize(width=W, height=H))
        page.wait_for_load_state()
        page.wait_for_timeout(5000)

        print(" -- 3")
        if page.locator(
            "#t3_12hmbug > div > div._3xX726aBn29LDbsDtzr_6E._1Ap4F5maDtT1E1YuCiaO0r.D3IL3FD0RFy_mkKLPwL4 > div > div > button"
        ).is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            if verbose:
                print("Post is NSFW.")
            page.locator(
                "#t3_12hmbug > div > div._3xX726aBn29LDbsDtzr_6E._1Ap4F5maDtT1E1YuCiaO0r.D3IL3FD0RFy_mkKLPwL4 > div > div > button"
            ).click()
            page.wait_for_load_state()  # Wait for page to fully load

        # Making the cookies message dissapear
        if page.locator(
            "div.trdUvQxqQHHqQKOUBcgnr._3RhWPJfjpsEoBw52x0fQp2.n4AaEF3hCCYK665NCiJr8 > section:nth-child(2) > section:nth-child(1) > form > button"
        ).is_visible():
            if verbose:
                print("Took Out Cookies Message.")
            page.locator(
                "div.trdUvQxqQHHqQKOUBcgnr._3RhWPJfjpsEoBw52x0fQp2.n4AaEF3hCCYK665NCiJr8 > section:nth-child(2) > section:nth-child(1) > form > button"
            ).click()
            page.wait_for_load_state()

        if page.locator(
            "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
        ).is_visible():
            page.locator(
                "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
            ).click()  # Interest popup is showing, this code will close it
            page.wait_for_load_state()
        postcontentpath = f"{PATH}/{reddit_id}/png/title.png"
        if verbose:
            print(page.url)

        try:
            page.locator(
                "xpath=/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[1]/div/div[3]"
            ).screenshot(path=postcontentpath)
        except Exception as e:
            if verbose:
                print("TITLE PIC - SCREENSHOT NOT WORKING")
            raise e

        for comment in (reddit_object["comments"])[1:screenshot_num]:
            comment_index = (reddit_object["comments"])[1:screenshot_num].index(comment)
            print(f"{comment_index+1} screenshots downloaded")
            if page.locator('[data-testid="content-gate"]').is_visible():
                page.locator('[data-testid="content-gate"] button').click()

            page.goto(
                f'https://reddit.com{comment["comment_url"].split("/")[0]}/{comment["comment_url"].split("/")[1]}/{comment["comment_url"].split("/")[2]}/{comment["comment_url"].split("/")[3]}/{comment["comment_url"].split("/")[4]}/',
                timeout=0,
            )
            page.wait_for_load_state()

            try:
                page.locator(f"#t1_{comment['comment_id']}").screenshot(
                    path=f"{PATH}/{reddit_id}/png/comment_{comment_index}.png"
                )
            except TimeoutError:
                del reddit_object["comments"]
                screenshot_num += 1
                if verbose:
                    print("TimeoutError: Skipping screenshot...")

        # close browser instance when we are done using it
        browser.close()

    if verbose:
        print("Screenshots downloaded Successfully.")
