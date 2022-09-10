import tkinter as tk
from tkinter import filedialog as fd
import requests as r
from shutil import copyfileobj

"""
A basic, easily modifiable installer.
Downloads an exe from github according to inputted url,
constructs the needed directory structure via a function
passed as a parameter.
"""

# Todo: Create shortcut for exe on desktop

class Installer:
    def __init__(self, exe_url: str, **kwargs):
        try:
            self.exe_url = kwargs['exe_url']
        except KeyError:
            self.exe_url = None

        try:
            self.make_dir_structure = kwargs['make_dir_structure']
        except KeyError:
            self.make_dir_structure = None

        try:
            self.final_exe_path = kwargs['final_exe_path']
        except KeyError:
            self.final_exe_path = '/'

        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = 'Program'

        try:
            self.size = kwargs['size']
        except KeyError:
            self.size = None

        try:
            self.timeout = kwargs['timeout']
        except KeyError:
            self.timeout = 1

        try:
            self.download_attempts = kwargs['download_attempts']
        except KeyError:
            self.download_attempts = 10

        try:
            self.settings_page = kwargs['settings_page']
        except KeyError:
            self.settings_page = self._page2

        self.dir = ''

        self.root = tk.Tk()
        self.root.title(self.name + ' installer')

        self.cur_page = 0
        self.textbox = tk.Text()

        self._page1()
        self.root.mainloop()

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()
        return

    def _get_dir(self):
        self.textbox.delete('0.0', tk.END)
        self.textbox.insert('0.0', fd.askdirectory())
        self.root.update()
        return

    def _page1(self):
        """
        Page for selecting target directory
        :return: None
        """
        self.clear()
        self.cur_page = 1

        tk.Label(self.root, text=self.name + ' Installer').pack()
        if self.size is not None:
            tk.Label(self.root, text='Estimated size: ' + self.size + '\n').pack()

        tk.Label(self.root, text='Destination folder:').pack()
        self.textbox = tk.Text(self.root, width=30, height=1)
        self.textbox.insert('0.0', self.dir)
        self.textbox.pack()
        tk.Button(self.root, text='Browse', command=self._get_dir).pack()
        tk.Button(self.root, text='Next', command=self.settings_page).pack()
        tk.Button(self.root, text='Quit', command=self.root.destroy).pack()

        return

    def _page2(self):
        """
        Setup page.
        Also the default settings page if none is provided.
        :return:
        """
        if self.cur_page == 1:
            self.dir = self.textbox.get('1.0', tk.END).strip()
        self.cur_page = 2
        self.clear()

        label = tk.Label(self.root, text='Creating directories...')
        label.pack()
        tk.Button(self.root, text='Cancel', command=self.root.destroy).pack()

        if self.make_dir_structure is not None:
            self.make_dir_structure()

        label.configure(text='Downloading exe...')
        self.root.update()

        exe = None
        for i in range(self.download_attempts):
            try:
                exe = r.get(self.exe_url, stream=True, timeout=self.timeout)
                break
            except r.exceptions.RequestException:
                if i == self.download_attempts - 1:
                    self._fail_page()
                continue

        label.configure(text='Moving exe to directory...')
        self.root.update()

        try:
            with open(self.dir + self.final_exe_path + self.name + '.exe', 'wb') as file:
                copyfileobj(exe.raw, file)
        except Exception as e:
            print(e)
            self._fail_page()

        self._page3()

        return

    def _page3(self):
        self.clear()
        self.cur_page = 3

        tk.Label(self.root, text='Successfully finished.\n').pack()
        tk.Button(self.root, text='Quit installer', command=self.root.destroy).pack()

        return

    def _fail_page(self):
        self.cur_page = -1
        self.clear()

        tk.Label(self.root, text='FATAL ERROR ENCOUNTERED').pack()
        tk.Button(self.root, text='Quit', command=self.root.destroy).pack()
