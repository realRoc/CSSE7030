from PIL import Image
from tkinter import messagebox
import os
import sys


class SpriteSheetLoader:
    def __init__(self, path, position: (int, int, int, int), name_id):
        self._path = path
        self._position = position
        self._name = name_id

    def load_image(self):
        try:
            return Image.open(self._path, 'r')
        except IOError:
            messagebox.showerror("Error", "Wrong sprite file path!")

    def load_sprite(self):
        im = self.load_image()
        print(im.size)
        region = im.crop(self._position)
        # region = region.transpose(Image.ROTATE_180)
        # region = im.paste(region, self._position)
        save_name = os.path.abspath(os.path.dirname(sys.argv[0])) + '\\sprite\\' + self._name + '.png'
        region.save(save_name)
        print(save_name)
        print(type(region))


path = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\spritesheets\\enemies.png"
print(os.path.isfile(path))
print(path)
SpriteSheetLoader(path, (0, 0, 100, 100), '11').load_sprite()
