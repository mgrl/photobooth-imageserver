import piexif
import datetime
import logging
logger = logging.getLogger(__name__)


class Exif():
    """Handle all image related stuff"""

    def __init__(self, frameServer, locationservice):
        self._frameServer = frameServer
        self._locationservice = locationservice

    def createExifBytes(self):
        # grab metadata from frameserver
        now = datetime.datetime.now()
        zero_ifd = {piexif.ImageIFD.Make: "Arducam",
                    piexif.ImageIFD.Model: self._frameServer._picam2.camera.id,
                    piexif.ImageIFD.Software: "Photobooth Imageserver"}
        total_gain = self._frameServer._metadata["AnalogueGain"] * \
            self._frameServer._metadata["DigitalGain"]
        exif_ifd = {piexif.ExifIFD.ExposureTime: (self._frameServer._metadata["ExposureTime"], 1000000),
                    piexif.ExifIFD.DateTimeOriginal: now.strftime("%Y:%m:%d %H:%M:%S"),
                    piexif.ExifIFD.ISOSpeedRatings: int(total_gain * 100)}

        exif_dict = {"0th": zero_ifd, "Exif": exif_ifd}

        if (self._locationservice.accuracy):
            logger.info("adding GPS data to exif")
            logger.debug(
                f"gps location: {self._locationservice.latitude},{self._locationservice.longitude}")

            gps_ifd = {
                piexif.GPSIFD.GPSLatitudeRef: self._locationservice.latitudeRef,
                piexif.GPSIFD.GPSLatitude: self._locationservice.latitudeDMS,
                piexif.GPSIFD.GPSLongitudeRef: self._locationservice.longitudeRef,
                piexif.GPSIFD.GPSLongitude: self._locationservice.longitudeDMS,
            }
            # add gps dict
            exif_dict.update({"GPS": gps_ifd})

        exif_bytes = piexif.dump(exif_dict)

        return exif_bytes

    def injectExifToJpeg(self, filepath):
        # gater data
        exif_bytes = self.createExifBytes()
        # insert exif data
        piexif.insert(exif_bytes, filepath)
