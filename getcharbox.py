import os
import codecs
import tempfile
import sys
import time


from src.pyocr import builders
from src.pyocr import tesseract
from PIL import Image

filepath = os.path.split(os.path.realpath(__file__))[0]
print "filepath:", filepath
print os.environ['TESSDATA_PREFIX']

class BaseTest(object):
    tool = None

    def _path_to_img(self, image_file):
        raise NotImplementedError("Implement in subclasses.")

    def _path_to_out(self, expected_output_file):
        raise NotImplementedError("Implement in subclasses.")

    def _read_from_expected(self, expected_output_path):
        raise NotImplementedError("Implement in subclasses.")

    def _read_from_img(self, image_path, lang=None):
        return self.tool.image_to_string(
            Image.open(image_path),
            lang=lang,
            builder=self._builder
        )

    def _test_equal(self, output, expected_output):
        raise NotImplementedError("Implement in subclasses.")

    def set_builder(self):
        raise NotImplementedError("Implemented in subclasses.")

    def setUp(self):
        self.set_builder()

    def _test_txt(self, image_file, expected_output_file, lang='eng'):
        image_path = self._path_to_img(image_file)
        expected_output_path = self._path_to_out(expected_output_file)

        expected_output = self._read_from_expected(expected_output_path)
        output = self._read_from_img(image_path, lang)

        self._test_equal(output, expected_output)


class BaseTestBox(BaseTest):
    def _read_from_expected(self, expected_output_path):
        with codecs.open(expected_output_path, 'r', encoding='utf-8') \
                as file_descriptor:
            expected_boxes = self._builder.read_file(file_descriptor)
        expected_boxes.sort()

        return expected_boxes

    def _read_from_img(self, image_path, lang=None):
        boxes = tesseract.image_to_string(
            Image.open(image_path),
            lang=lang,
            builder=self._builder
        )
        boxes.sort()

        return boxes


class BaseTesseract(BaseTest):
    tool = tesseract

    def _path_to_img(self, image_file):
        return os.path.join(
            filepath, "tests", "charboxtest",  image_file
        )

    def _path_to_out(self, expected_output_file):
        return os.path.join(
            filepath, "tests", "charboxtest", expected_output_file
        )


class GetCharBox(BaseTestBox, BaseTesseract):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def set_builder(self):
        self._builder = tesseract.CharBoxBuilder()



    def test_basic(self):
        self._test_txt('test.png', 'test.box')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.box')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.box', 'fra')

    def test_japanese(self):
        self._test_txt('test-japanese.jpg', 'test-japanese.box', 'jpn')

    def test_write_read(self):
        image_path = self._path_to_img("test.jpg")
        original_boxes = self._read_from_img(image_path, lang="chisim")
        print "original_boxes num:", len(original_boxes)
        print original_boxes

        out_path = self._path_to_out("result")

        (file_descriptor, tmp_path) = tempfile.mkstemp()
        try:
            # we must open the file with codecs.open() for utf-8 support
            os.close(file_descriptor)

            with codecs.open(out_path, 'w', encoding='utf-8') as fdescriptor:
                self._builder.write_file(fdescriptor, original_boxes)

            with codecs.open(tmp_path, 'r', encoding='utf-8') as fdescriptor:
                new_boxes = self._builder.read_file(fdescriptor)


        finally:
            os.remove(tmp_path)


if __name__ == '__main__':
    t0 = time.time()
    charBox = GetCharBox()
    charBox.set_builder()
    charBox.test_write_read()
    print "timecost:", time.time() - t0