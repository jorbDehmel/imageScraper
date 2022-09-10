import requests as r
import regex as re
import tkinter as tk
from tkinter import filedialog as fd
from shutil import copyfileobj
import os
import threading

image_formats = ('image/png', 'image/jpg', 'image/jpeg')
def is_image_link(url: str, timeout=1) -> bool:
    global image_formats
    try:
        is_image = r.get(url, timeout=timeout).headers['content-type'] in image_formats
    except Exception as e:
        print(e)
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

    print(out_folder)
    with open(out_folder + name, 'wb') as file:
        copyfileobj(image.raw, file)

class ImageScraper:
    def __init__(self, link='https://www.google.com/', output_folder='', timeout=0.5):
        self.link, self.output_folder, self.timeout = link, output_folder, timeout

        print(os.getcwd())
        if output_folder == '':
            if not os.path.exists('output'):
                os.makedirs('output')
            self.output_folder = 'output/'

        self.counter = 0
        self.root = tk.Tk()
        self.root.geometry('250x220')
        self.root.title('Image Scraper')
        self._page1()
        self.root.mainloop()
    
    def scrape(self, url, out_folder, timeout, depth=0):
        print(self.output_folder)
        
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
        links = re.findall(r'(?<==")(?:https?:)?//[^ ]*?(?=")', html)
        links += re.findall(r'(?<=src=")[^"]+', html)

        print('Found: ', links)

        # Test each link for image-hood
        links.sort()
        for link in links:
            # Fix link if needed
            if link[:4].lower() != 'http':
                link = re.search(r'https?://[^/\\]+(/|\\)?', url).group() + link

            # If is image, download
            if is_image_link(link):
                print('Scraping single image', link)
                scrape_single_image(link, out_folder, timeout)
            elif depth != 0:
                print('Scraping non-image link', link)

                try:
                    self.scrape(link, out_folder, timeout, depth - 1)
                except Exception as e:
                    print(e)

        return
    
    def clear(self):
        for child in self.root.winfo_children():
            child.destroy() # metal line
        return
    
    def _select_folder(self):
        self.output_folder = fd.askdirectory()
        return
    
    def _go(self, link_textbox: tk.Text, depth_textbox: tk.Text):
        self.link = link_textbox.get('1.0', tk.END)
        depth = int(depth_textbox.get('1.0', tk.END))
        self._page2()

        self.scrape(self.link, self.output_folder, self.timeout, depth)

        self._page1()
        return

    def _page1(self):
        self.clear()

        tk.Label(self.root, text='Python Image Scraping Script\n').pack()
        
        tk.Label(self.root, text='Number scraped: ' + str(self.counter)).pack()

        tk.Label(self.root, text='URL:').pack()
        link_textbox = tk.Text(self.root, width=30, height=1)
        link_textbox.pack()
        
        tk.Label(self.root, text='Depth:').pack()
        depth_textbox = tk.Text(self.root, width=30, height=1)
        depth_textbox.pack()

        tk.Button(self.root, text='Select output folder', command=self._select_folder).pack()
        tk.Button(self.root, text='Go', command=lambda: self._go(link_textbox, depth_textbox)).pack()

        tk.Button(self.root, text='Quit', command=self.root.destroy).pack()

        return
    
    def _page2(self):
        self.clear()

        tk.Label(self.root, text='Working...').pack()
        tk.Button(self.root, text='Cancel', command=self._page1).pack()
        tk.Button(self.root, text='Quit', command=self.root.destroy).pack()

        return
