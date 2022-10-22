import os
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse
from browser_creator import BrowserCreator
from gcs import BucketManager
from fastapi.responses import HTMLResponse
from movie_config import MovieConfig
from movie_maker import MovieMaker

app = FastAPI()
BUCKET_NAME = os.environ.get("BUCKET_NAME", None)


@app.get("/")
async def index():
    """
    This is usage of this API.
    :return: HTML
    """
    return HTMLResponse("""
    <h1>NorichaConverter</h1>
    <h2>VRChatで表示したいウェブページのURLを入力してください</h2>
    <form action="/create_movie" method="get">
        <input type="text" name="url" placeholder="https://">
        <input type="submit" value="Create Movie">
    </form>
    """)


@app.get("/create_movie/")
def create_movie(url: str, width: int = 1280, height: int = 720, max_height: int = 10000, scroll_px: int = 200):
    """
    Take a screenshot of the given URL. The screenshot is saved in the GCS. Return the file of download URL.
    1. create hash of URL, scroll_px, width, height. max_height.
    2. check if the movie file exists.
    3. if the movie file exists, return the download url.
    4. if the movie file does not exist, take a screenshot and save it to the GCS.
    :param url: URL to take a screenshot
    :param width: Browser width
    :param height: Browser height
    :param max_height: Max scroll height
    :param scroll_px:
    :return: Download URL
    """
    if len(url) == 0:
        raise HTTPException(status_code=400, detail="URL is empty.Please set URL.")
    bucket_manager = BucketManager(BUCKET_NAME)
    movie_config = MovieConfig(url, width, height, max_height, scroll_px)
    if os.path.exists(movie_config.movie_path):
        url = bucket_manager.get_public_file_url(movie_config.movie_path)
        return RedirectResponse(url=url, status_code=303)
    movie_maker = MovieMaker(movie_config)
    movie_maker.create_movie()
    # Upload to GCS
    url = BucketManager(BUCKET_NAME).to_public_url(movie_config.movie_path)
    return RedirectResponse(url=url, status_code=303)


@app.get("/create_github_movie/")
def create_github_movie(url: str, targets: str, width: int = 1280, height: int = 720, max_height: int = 10000,
                        scroll_px: int = 200,
                        catch: bool = True):
    """
    Download github repository, convert file into HTML, and take a screenshot.
    :param url: URL to take a screenshot
    :param targets: target file list to take a screenshot
    :param width: Browser width
    :param height: Browser height
    :param max_height: Max scroll height
    :param scroll_px:
    :param catch: if catch is true, check saved movie is suitable.
    :return: GitHub repository page URL
    """
    targets = targets.split(",")
    if len(url) == 0:
        raise HTTPException(status_code=400, detail="URL is empty.Please set URL.")
    bucket_manager = BucketManager(BUCKET_NAME)
    movie_config = MovieConfig(url, width, height, max_height, scroll_px, targets)
    if catch and os.path.exists(movie_config.movie_path):
        url = bucket_manager.get_public_file_url(movie_config.movie_path)
        return RedirectResponse(url=url, status_code=303)
    # Download the repository.
    movie_maker = MovieMaker(movie_config)
    movie_maker.create_github_movie()
    # Upload to GCS
    url = BucketManager(BUCKET_NAME).to_public_url(movie_config.movie_path)
    return RedirectResponse(url=url, status_code=303)
