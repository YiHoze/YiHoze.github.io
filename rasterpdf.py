import os
import argparse
import glob
import subprocess
import img2pdf
from iu import ImageUtility
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
from PIL import Image

class RasterizePDF(object):

    def __init__(self):

        self.parse_args()
        self.rasterize()

    def parse_args(self):

        parser = argparse.ArgumentParser(
            description = 'Convert PDF pages to PNG.'
        )
        parser.add_argument(
            'pdf',
            nargs = '+',
            help = 'Specify one or more PDF files.'
        )
        parser.add_argument(
            '-j',
            dest = 'jpg_bool',
            action = 'store_true',
            default = False,
            help = 'Convert to JPEG.'
        )
        parser.add_argument(
            '-k',
            dest = 'remove_bool',
            action = 'store_false',
            default = True,
            help = 'Keep secondary image files.',
        )
        self.args = parser.parse_args()

    def count_page_digits(self, img):

        with open(img, 'rb') as f:
            pdf = PdfFileReader(f)
            pages = pdf.getNumPages()

        digits = 0
        while(pages >= 1):
            digits += 1
            pages = pages /10
        return digits

    def rasterize(self):

        for i in self.args.pdf:
            self.convert_pages(i)

    def convert_pages(self, pdf):

        if self.args.jpg_bool:
            image_format = 'jpeg'
        else:
            image_format = 'png'

        filename = os.path.splitext(pdf)[0]
        digits = self.count_page_digits(pdf)

        # save pages as images
        pages = convert_from_path(pdf)
        for i in range(len(pages)):
            output = '{}_{}.{}'.format(filename, str(i+1).zfill(digits), image_format)
            pages[i].save(output, image_format)

        # adjust the density
        page_images = filename + '_*.' + image_format
        for i in glob.glob(page_images):
            img = Image.open(i)
            img.save(i, dpi=(200,200))

        # merge images into pdf
        output = filename + '_rasterized.pdf'
        with open(output, 'wb') as f:
            f.write(img2pdf.convert(glob.glob(page_images)))

        if self.args.remove_bool:
            for i in glob.glob(page_images):
                os.remove(i)


if __name__ == '__main__':
    RasterizePDF()

