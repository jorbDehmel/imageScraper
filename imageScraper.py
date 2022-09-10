import requests as r
import regex as re
from shutil import copyfileobj

image_formats = ('image/png', 'image/jpg', 'image/jpeg')
def is_image_link(url: str, timeout=1) -> bool:
    global image_formats
    try:
        is_image = r.get(url, timeout=timeout).headers['content-type'] in image_formats
    except r.exceptions.RequestException:
        is_image = False
    return is_image

def scrape_single_image(url: str, out_folder: str, timeout) -> None:
    global image_formats

    try:
        image: r.Response = r.get(url, stream=True, timeout=timeout)
    except r.exceptions.RequestException:
        return

    # Failsafe
    if image.status_code != 200:
        print('url get failed')
        return
    if not is_image_link(url, timeout):
        print('not an image file')
        return

    # Get name
    name: str = re.search(r'(?<=/)[^"/]+$', url).group()
    name = re.sub(r'[:;,#<>$+%!`\'&|{}"?=/\\ @]', r'_', name)
    if '.' not in name:
        name += '.jpg'

    with open(out_folder + '/' + name, 'wb') as file:
        copyfileobj(image.raw, file)

def get_images_from_url(url: str, out_folder: str, timeout, depth) -> None:
    # Failsafe
    if is_image_link(url):
        print('Link is image link.')
        scrape_single_image(url, out_folder, timeout)
        return

    # Get url html
    try:
        html = r.get(url, stream=True, timeout=timeout).text
    except r.exceptions.RequestException:
        print('Connection failed.')
        return

    # Find all links within html
    print('Searching for links...')
    if depth == 0:
        links = re.findall(r'(?<==")(?:https?:)?//[^ ]*?\.(?:png|jpg|jpeg)(?=")', html)
    else:
        links = re.findall(r'(?<==")(?:https?:)?//[^ ]*?(?=")', html)
    print('Found: ', links)

    # Test each link for image-hood
    links.sort()
    for link in links:
        # If is image, download
        if is_image_link(link):
            print('Scraping single image', link)
            scrape_single_image(link, out_folder, timeout)
        elif depth != 0:
            print('Scraping non-image link', link)
            get_images_from_url(link, out_folder, timeout, depth - 1)

    return

class ImageScraper:
    def __init__(self, link, output_folder, timeout=1, depth=0):
        self.link, self.output_folder, self.timeout, self.depth = link, output_folder, timeout, depth
