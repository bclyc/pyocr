import os
import codecs
import tempfile
import sys
import time
import traceback


from src.pyocr import builders
from src.pyocr import tesseract
from src.pyocr.libtesseract import tesseract_raw
from PIL import Image, ImageDraw

filepath = os.path.split(os.path.realpath(__file__))[0]
#print "filepath:", filepath
#print os.environ['TESSDATA_PREFIX']

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


def initTess():
    handle = tesseract_raw.init(lang="chisim")
    return handle


def closeTess(handle):
    tesseract_raw.cleanup(handle)
    pass


def getCharBox(handle, imagePath):

    print tesseract_raw.is_available(), tesseract_raw.get_available_languages(handle)
    # t0 = time.time()
    # charBox = GetCharBox()
    # charBox.set_builder()
    # charBox.test_write_read()
    # print "timecost:", time.time() - t0
    t1 = time.time()
    bbox=[]
    try:
        inputImage = Image.open(imagePath)
        tesseract_raw.set_page_seg_mode(handle=handle, mode=2)
        # tesseract_raw.set_is_numeric(handle=handle, mode=3)
        tesseract_raw.init_for_analyse_page(handle=handle)
        tesseract_raw.set_image(handle=handle, image=inputImage)
        tesseract_raw.analyse_layout(handle=handle)

        iterator = tesseract_raw.get_iterator(handle)
        #print iterator


        count = 0
        imagedraw = ImageDraw.Draw(inputImage)

        level = 2
        hasNext = True
        lx1, ly1, lx2, ly2 = [-1, -1, -1, -1]
        lhwRate = -1.0
        merged_num = 0
        while hasNext:
            coord = tesseract_raw.page_iterator_bounding_box(iterator=iterator, level=level)[1]
            x1, y1, x2, y2 = coord
            hwRate = (float(y2-y1)/(x2-x1) if x2!=x1 else 0)
            print count, tesseract_raw.page_iterator_bounding_box(iterator=iterator, level=level), hwRate


            #merge semi-parts of a CHchar
            if lx2>=x1 and lhwRate>1.2 and hwRate>1.2 and ly1<y2 and ly2>y1 and (lx2-x1)<(ly2-ly1):
                bbox.pop()
                count -= 1
                x1 = (x1 if x1 < lx1 else lx1)
                y1 = (y1 if y1 < ly1 else ly1)
                x2 = (x2 if x2 > lx2 else lx2)
                y2 = (y2 if y2 > ly2 else ly2)
                hwRate = (float(y2 - y1) / (x2 - x1) if x2 != x1 else 0)
                merged_num += 1
                print "merged!"

            lx1, ly1, lx2, ly2 = [x1,y1,x2,y2]
            lhwRate = hwRate
            bbox.append([x1,y1,x2,y2])
            count += 1
            hasNext = tesseract_raw.page_iterator_next(iterator, level=level)
        print "count:", count, "merged:", merged_num

        count = 0
        for x1,y1,x2,y2 in bbox:
            imagedraw.line((x1, y1, x1, y2), fill=(255, 0, 0), width=1)
            imagedraw.line((x1, y1, x2, y1), fill=(255, 0, 0), width=1)
            imagedraw.line((x1, y2, x2, y2), fill=(255, 0, 0), width=1)
            imagedraw.line((x2, y1, x2, y2), fill=(255, 0, 0), width=1)
            imagedraw.text((x1, y1), str(count), fill=(255,0,0))
            count += 1
        inputImage.show()

        # tesseract_raw.recognize(handle)
        # print tesseract_raw.get_utf8_text(handle)
        # print tesseract_raw.page_iterator_bounding_box(iterator=iterator, level=3)
        # print tesseract_raw.page_iterator_is_at_beginning_of(iterator, 3)
        # print tesseract_raw.page_iterator_next(iterator, 3)
        # print tesseract_raw.page_iterator_is_at_beginning_of(iterator, 3)
        # print tesseract_raw.page_iterator_bounding_box(iterator=iterator, level=3)

        print "get bbox time used:", time.time() - t1

    except:
            traceback.print_exc()
    return bbox

if __name__ == '__main__':

    getCharBox(initTess(),"/usr/workspace/pyocr/tests/charboxtest/test.jpg")
