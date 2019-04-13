#!/usr/bin/env python3
import glob, os
import pyexiv2
from PIL import Image
import hashlib
import base64

ORIGINAL_IMAGE_PATHS = set(os.path.normpath(os.path.normpath(f'{os.path.join(os.getcwd(), "../test_images")}')))
PROCESSED_IMAGE_PATH = os.path.normpath(os.path.normpath(f'{os.path.join(os.getcwd(), "../test_images/processed")}'))
CONVERSION_FORMAT = 'jpg'


class ProcessImages:
    """
    Processes images by:
        - convert image format (e.g. .tif to .jpg)
        - read & transfer IPTC 'keyword' tags from original to converted image
    """

    ALLOWED_CONVERSION_FORMATS = ['jpeg', 'jpg', 'tiff', 'tif', 'png']

    def __init__(self, image_paths=None, processed_image_path=None, conversion_format=None,
                 retag=False):
        """
        initiate the class
        :param image_paths: set of paths of dirs of photos to be converted and/or tagged
        :param processed_image_path: path to save the processed image to
        :param conversion_format: file format to convert image to
        :param retag: boolean value, signifying whether to perform re-tagging
            if the image name already exists in the defined location where
            converted images are saved.
        """
        self.ORIGINAL_IMAGE_PATHS = image_paths
        self.PROCESSED_IMAGE_PATH = processed_image_path
        self.CONVERSION_FORMAT = conversion_format if conversion_format.lower() in self.ALLOWED_CONVERSION_FORMATS \
            else 'jpg'
        self.retag = retag if isinstance(retag, bool) else False

    @staticmethod
    def read_iptc_tags(filename, path):
        """
        method to read IPTC tags
        :param filename: filename of image
        :param path: path to image
        :return: [{'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}] | False
        """
        try:
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            iptc_keys = meta.iptc_keys
            image_data = []
            if iptc_keys:
                for key in iptc_keys:
                    tag = meta[key]
                    image_data.append({'iptc_key': key, 'tags': tag.raw_value or []})
                print(image_data)
            else:
                image_data.append({'iptc_key': '', 'tags': []})
            return image_data
        except (IOError, Exception) as e:
            print(f'An error occurred in read_iptc_tags: {e}')
            return False

    @staticmethod
    def write_iptc_tags(path, filename, tag_data):
        """
        method to write IPTC tags to image
        :param path: path to target image
        :param filename: filename of target image
        :param tag_data: original image data: in form: {'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}
        :return: True | False
        Note: Only handle KEYWORDS IPTC key (TODO: for now! Implement others later - may require some debug)
        """
        try:
            iptc_key = tag_data['iptc_key'] if tag_data['iptc_key'] == 'Iptc.Application2.Keywords' else None
            if iptc_key:
                tags = tag_data['tags']
                url = os.path.join(path, filename)
                meta = pyexiv2.ImageMetadata(os.path.join(url))
                meta.read()
                meta[iptc_key] = pyexiv2.IptcTag(iptc_key, tags)
                meta.write()
                print('Tags successfully written!')
                return True
            print('No tag to write!')
        except (TypeError, Exception) as e:
            print(f'An error occurred in write_iptc_tags: {e}')
        return False

    @staticmethod
    def convert_format(orig_filename, new_filename, path, save_path, conversion_format):
        """
        method to convert the format of an image file
        :param orig_filename: original filename of image
        :param new_filename: new filename of image (i.e. with appended directory hash)
        :param path: path of image
        :param conversion_format: file format to covert to
        :param save_path: where to save the converted image
        :return: {'orig_file_path': path, 'processed_path': save_path, 'filename': filename} | False
        """
        try:
            url = os.path.join(path, orig_filename)
            file, extension = os.path.splitext(new_filename)
            outfile = f'{file}.{conversion_format}'
            Image.open(url).save(os.path.join(save_path, outfile), quality=100)
            print('Conversion done!')
            return {'orig_path': path, 'processed_path': save_path, 'filename': outfile}
        except (IOError, Exception) as e:
            print(f'An error occurred in convert_format: {e}')
        return False

    @staticmethod
    def get_filenames(directory):
        """
        method to get filenames of all files (not sub-dirs) in a directory
        :param directory: the directory to scan for files
        :return: a list of files
        """
        filenames = []
        try:
            for filename in os.listdir(directory):
                if not os.path.isdir(os.path.join(directory, filename)):
                    filenames.append(filename)
            return filenames
        except (IOError, Exception) as e:
            print(f'An error occurred in get_filenames: {e}')
        return False

    def generate_processed_copies(self):
        """
        generator method to run the image conversion and tagging processes
        :yield: generator, that processes files in an origin directory &
        produces dicts of saved conversion data and tags: e.g.:
            {conversion_data: {'orig_path': '/path/to/orig/image', 'processed_path':'/path/to/processed_image',
            'filename': '4058.jpeg'}, tag_data: {'iptc_key': 'Iptc.Application2.Keywords', 'tags':
            ['DATE: 1974', 'PLACE: The Moon']}
        Note: hash of path appended to file names to ensure duplicate name of files in other
        origin directories do not overwrite pre-existing files of the same name in the processed directory.
        """
        try:
            existing_converted = self.get_filenames(self.PROCESSED_IMAGE_PATH)
            processed_data = {'conversion_data': {'orig_path': '', 'processed_path': '', 'filename': ''},
                              'tag_data': {'iptc_key': '', 'tags': []}}
            for image_path in self.ORIGINAL_IMAGE_PATHS:
                path_hash = hashlib.sha1(image_path.encode()).hexdigest()
                for filename in os.listdir(image_path):
                    if not os.path.isdir(os.path.join(image_path, filename)):  # if file (not dir)
                        """
                        save converted file
                        """
                        # generate required filename with new extension
                        new_filename = f'{path_hash}_{os.path.splitext(filename)[0]}.{self.CONVERSION_FORMAT}'
                        # check if converted file already exists
                        converted_did_exist = new_filename in existing_converted
                        print(f'New filename: {new_filename}')
                        print(f'Already exists in processed directory? : {converted_did_exist}')
                        if not converted_did_exist:  # if filename does not already exist (not already converted)
                            # save copy of the image with converted format
                            converted = self.convert_format(orig_filename=filename,
                                                            new_filename=new_filename,
                                                            path=image_path,
                                                            save_path=self.PROCESSED_IMAGE_PATH,
                                                            conversion_format=self.CONVERSION_FORMAT)
                            processed_data['conversion_data'] = converted
                        else:
                            """
                            if converted image file already existed, save existing conversions in
                            a list for the return dict here, as it was not already returned by the new image 
                            conversion function (above)
                            """
                            processed_data['conversion_data'] = {'orig_path': image_path,
                                                                 'processed_path': self.PROCESSED_IMAGE_PATH,
                                                                 'filename': new_filename}
                        """
                        write tags to file
                        """
                        if self.retag or not converted_did_exist:  # if retag is set, or newly converted image
                            # read tag data from original image
                            tag_data = self.read_iptc_tags(filename=filename, path=image_path)
                            # any additions or updates to the incoming tag data
                            if tag_data:
                                for tag in tag_data:
                                    if tag['tags']:
                                        tag['tags'].append(
                                            'SPM: TAGS COPIED FROM ORIGINAL')  # add tag to identify as copied
                                        processed_data['tag_data'] = tag  # add to the return dicts
                                        # write the tags to the converted file
                                        self.write_iptc_tags(path=self.PROCESSED_IMAGE_PATH,
                                                             filename=new_filename,
                                                             tag_data=tag)
                                    else:
                                        processed_data['tag_data'] = tag  # add to the return dicts
                                        file = os.path.join(self.PROCESSED_IMAGE_PATH, new_filename)
                                        print(f'No tag was saved for this file: {file}')
                        yield processed_data
        except (TypeError, Exception) as e:
            print(f'Error occurred processing images, in main(): {e}')
        return False


if __name__ == '__main__':
    ProcessImages(image_paths=ORIGINAL_IMAGE_PATHS,
                  processed_image_path=PROCESSED_IMAGE_PATH,
                  conversion_format=CONVERSION_FORMAT,
                  retag=False).generate_processed_copies()
