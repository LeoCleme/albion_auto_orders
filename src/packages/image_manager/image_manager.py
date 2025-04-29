""" Image ImageManager Module """

from datetime import datetime, timedelta
from logging import getLogger
from os import mkdir
from pathlib import Path
from time import sleep
from typing import Tuple
from sys import platform

import cv2
import pyautogui
import pytesseract as pyt

logger = getLogger("image_manager")

class ImageManager():
    """A class to select and interact with images on the screen."""

    def __init__(
        self,
        folder_path: str,
        tesseract_path: str = None
    ) -> None:
        """
        Initialize the ImageManager.

        Args:
            image_folder_name (str): The name of the folder containing images.
            tesseract_path (str): The tesseract exe path.
        """
        self.config_tesseract(tesseract_path)
        self.folder_path = Path(folder_path)
        if not self.folder_path.is_dir():
            mkdir(self.folder_path)
            logger.info("%s created. Fill it with images!", folder_path)
        self.images_map: dict = {}
        self.load_images()

    def config_tesseract(self, tesseract_path: str = None) -> None:
        """
        Configure pytesseract.
        
        """
        if tesseract_path:
            pyt.pytesseract.tesseract_cmd = tesseract_path
        else:
            if platform == "linux":
                path_exe = "/usr/bin/tesseract"
            elif platform == "win32":
                path_exe = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            pyt.pytesseract.tesseract_cmd = path_exe
        try:
            tesseract_version = pyt.get_tesseract_version()
            logger.debug("Tesseract version: %s", tesseract_version)
        except pyt.TesseractNotFoundError as exc:
            raise ValueError(
                f"Tesseract ocr not found! The exe should be in {path_exe}"
            ) from exc

    def load_images(self) -> None:
        """Load images from the specified folder."""
        for photo_path in self.folder_path.iterdir():
            img_cv = cv2.imread(str(photo_path), cv2.IMREAD_COLOR)
            if img_cv is None:
                logger.warning("Error loading image: %s", photo_path.name)
                continue
            self.images_map[photo_path.stem] = img_cv
        logger.debug("Loaded %s images!", len(self.images_map))

    def locate_image(self, image: str, confidence: float) -> tuple:
        """
        Locate the position of the given image on the screen.

        Args:
            image (str): The name of the image to locate.
            confidence (float): The confidence threshold for image matching.

        Returns:
            tuple: The position of the image if found, None otherwise.
        """
        selected_image = self.images_map.get(image)
        if selected_image is None:
            logger.error("Image %s not mapped, check image folder!", image)
            return None
        try:
            return pyautogui.locateCenterOnScreen(
                selected_image,
                confidence=confidence,
                minSearchTime=2
            )
        except pyautogui.ImageNotFoundException:
            logger.debug("Image %s not found!", image)
            return None

    def move_to_image(
        self,
        name: str,
        offset: Tuple = (0,0),
        confidence: float = 0.85
    ) -> bool:
        """
        Move the mouse pointer to the specified image on the screen.

        Args:
            name (str): The name of the image.
            offset (tuple): The offset from the image's center.
            confidence (float): The confidence threshold for image matching.

        Returns:
            bool: True if the image is located and the cursor is moved,
                False otherwise.
        """
        sleep(0.5)
        position = self.locate_image(name, confidence)
        if position is None:
            logger.debug("Not moved to image %s", name)
            return False
        pyautogui.moveTo(position[0]+offset[0], position[1]+offset[1], 0.1)
        return True

    def click_image(
        self,
        name: str,
        button: str = pyautogui.LEFT,
        times: int = 1,
        offset: Tuple = (0,0),
        confidence: float = 0.9
    ) -> bool:
        """
        Click on the specified image on the screen.

        Args:
            name (str): The name of the image.
            button (str): The mouse button to click. Default to pyautogui.LEFT.
            times (int): The number of clicks. Defaults to 1.
            offset (tuple): The offset from the image's center.
            confidence (float): The confidence threshold for image matching.

        Returns:
            bool: True if the image is located and clicked successfully,
                False otherwise.
        """
        sleep(0.5)
        position = self.locate_image(name, confidence)
        if position is None:
            logger.debug("Not clicked %s", name)
            return False
        updated_position = (position[0]+offset[0], position[1]+offset[1])
        logger.debug("Image %s clicked on %s", name, str(updated_position))
        pyautogui.moveTo(updated_position[0], updated_position[1], 0.1)
        if button == pyautogui.LEFT:
            pyautogui.click(button=pyautogui.LEFT, clicks=times)
        elif button == pyautogui.RIGHT:
            pyautogui.click(button=pyautogui.RIGHT, clicks=times)
        else:
            logger.error("Unknown mouse button: %s", button)
            return False
        sleep(2)
        return True

    def wait_image(
        self,
        name: str,
        timeout: float = 1,
        confidence: float = 0.85,
        revive_img: str = None
    ) -> bool:
        """
        Wait for the specified image to appear on the screen.

        Args:
            name (str): The name of the image.
            timeout (Tuple): The maximum time to wait (in minutes). Defaults 1.
            confidence (Tuple): The confidence threshold for image matching.
            revive_img (str): The image to click on to revive the application.

        Returns:
            bool: True if the image appears within the timeout period,
                False otherwise.
        """
        is_visible = None
        start_time = datetime.now() + timedelta(minutes=timeout)
        checkpoint_time = start_time
        while is_visible is None and datetime.now() < start_time:
            is_visible = self.locate_image(name, confidence)
            sleep(0.5)
            now = datetime.now()
            if now - checkpoint_time > timedelta(seconds=5):
                if revive_img is not None:
                    self.click_image(revive_img)
                checkpoint_time = now
        logger.debug("Image %s visible: %s", name, is_visible is not None)
        return is_visible is not None

    def wait_till_visible(
        self,
        name: str,
        timeout: float | None = 10,
        confidence: float = 0.85,
        revive_img: str = None
    ):
        """
        Checks if the image associated with the element is visible
        and waits until it is visible if timeout is set as None.

        Args:
            timeout : (float | None, optional)
            Time interval to wait for the image to be visible. If set to None,
            it waits indefinitely until the image is visible. (default is 10)

        Returns:
            bool, True if the image is visible, False otherwise.
        """
        if timeout is None:
            visible = False
            while not visible:
                visible = self.wait_image(name, 1, confidence, revive_img)
            return visible
        visible = self.wait_image(name, timeout, confidence, revive_img)
        return visible

    def move_to_text(
        self,
        name: str,
        text_to_search: str,
        offset: Tuple = (0,0),
        region: Tuple[int] = None
    ) -> bool:
        """
        Move the mouse pointer to the specified text on the screen.

        Args:
            name (str): text searching image name.
            text_to_search (str): The text to search for.
            offset (Tuple): The offset from the text's position.
            region (Tuple[int]): The region to search within. Defaults to None.

        Returns:
            bool: True if the text is found and mouse movement is successful,
                False otherwise.
        """
        if region is not None:
            offset = (offset[0]+region[0], offset[1]+region[1])
        image_path = self.folder_path.joinpath(name)
        if not image_path.exists():
            logger.error('Image %s is not in the image folder provided', name)
            return False
        pyautogui.screenshot(image_path, region=region)
        img = cv2.imread(image_path)
        image_data = pyt.image_to_data(img, output_type=pyt.Output.DICT)
        for i in range(len(image_data['level'])):
            text = image_data['text'][i]
            if text_to_search in text:
                center_x = image_data['left'][i] + image_data['width'][i] / 2
                center_y = image_data['top'][i] + image_data['height'][i] / 2
                logger.debug("Text %s found!", text)
                pyautogui.moveTo(center_x + offset[0] , center_y + offset[1])
                return True
        logger.warning("Text %s not found!", text_to_search)
        return False

    def wait_text(
        self,
        text_to_search: str,
        timeout: int = 5,
        offset: Tuple = (0,0),
        region: Tuple[int] = None,
        revive_img: str = None,
        tesseract_config: str = "--psm 8"
    ) -> bool:
        """
        Wait for the specified text to appear on the screen.

        Args:
            text_to_search (str): The text to search for.
            timeout (int): The maximum time to wait (in seconds).Defaults to 5.
            offset (Tuple): The offset from the text's position.
            region (Tuple[int]): The region to search within.
            revive_img (str): The image to click on to revive the application.
            tesseract_config (str): Additional config options for Tesseract.

        Returns:
            str: True if the text appears within the timeout period,
                False otherwise.
        """
        found=False
        if region is not None:
            offset = (offset[0]+region[0], offset[1]+region[1])
        start_time = datetime.now() + timedelta(minutes=timeout)
        checkpoint_time = start_time
        while found is None and datetime.now() < start_time:
            img = cv2.imread(pyautogui.screenshot(region=region))
            image_data = pyt.image_to_data(
                img, config=tesseract_config, output_type=pyt.Output.DICT
            )
            for i in range(len(image_data['level'])):
                text = image_data['text'][i]
                if text_to_search in text:
                    found = True
            now = datetime.now()
            if now - checkpoint_time > timedelta(seconds=5):
                if revive_img is not None:
                    self.click_image(revive_img)
                checkpoint_time = now
            sleep(1)
        logger.debug("Text %s found: %s", text_to_search, found)
        return found


img_mngr = ImageManager("image_folder")