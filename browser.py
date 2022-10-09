import os
import time
from pathlib import Path
from typing import List

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class HeadlessDriverGenerator:
    @staticmethod
    def get_headless_chromedriver(width: int = 1026, height: int = 768):
        # The following options are required to make headless Chrome
        # Work in a Docker container
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"window-size={width},{height}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        # Initialize a new browser
        return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)


class Browser:
    def __init__(self, width: int = 1280, height: int = 720):
        self.height = height
        self.driver = HeadlessDriverGenerator.get_headless_chromedriver(width, height)

    @staticmethod
    def create_folder() -> Path:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        folder_path = f"image/{timestamp}"
        os.makedirs(folder_path)
        return Path(folder_path)

    @staticmethod
    def create_movie(file_paths: List[str], movie_path: str):
        """
        Create a movie from the given file paths. Each file is 2 seconds.
        :param file_paths:
        :param movie_path:
        :return:
        """
        from moviepy.editor import ImageSequenceClip
        clip = ImageSequenceClip(file_paths, fps=1)
        clip.write_videofile(movie_path, fps=1)

    def take_screenshot(self, url: str, each_px: int = 300, max_height: int = 5000) -> str:
        """
        Take a screenshot of the given URL and scroll each px then save it to a movie.
        :param url:
        :param each_px:
        :param max_height:
        :return: List of file absolute paths
        """
        self.driver.get(url)
        height = self.driver.execute_script("return document.body.scrollHeight")
        print(f"Height: {height} px URL: {url}")
        file_paths = []
        scroll_height = height - self.height
        if scroll_height == 0: scroll_height = each_px
        print(f"Scroll height: {scroll_height}")
        folder_path = self.create_folder()
        for px in range(0, scroll_height, each_px):
            self.driver.execute_script(f"window.scrollTo(0, {px})")
            file_path = f"{folder_path}/{px}.png"
            self.driver.save_screenshot(file_path)
            file_paths.append(file_path)
            file_paths.append(file_path)  # Add the same file twice to make it 2 seconds
        movie_path = f"{folder_path}/movie.mp4"
        self.create_movie(file_paths, movie_path)
        return movie_path
