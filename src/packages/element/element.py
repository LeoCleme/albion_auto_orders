""" Generic Element Module """

from logging import getLogger
from pathlib import Path
from time import sleep
from types import NoneType
from typing import Union, Dict, List, Tuple

import PIL.Image
import pyautogui

logger = getLogger("element")


class Element:
    """
    Class that implements and manage image elements with optimal properties
    and common functions.

    Example usage:
        >>> from image_manager import ImageManager
        >>> image_manager = ImageManager('path/to/your/image_storage')
        >>> element = Element(name='element', image_manager=image_manager)
        >>> element.name
        ... 'element'
        >>> element.visible()
        ... True
        >>> element.click()
        ... True
    """

    def __init__(
        self,
        name: str | Path,
        image_manager: object = None,
        location: tuple = None,
        parent: object = None,
        children: Union[object, Dict[str, object], List[object]] = None
    ) -> None:
        """
        Initializes an Element instance.

        Args:
            name: str or Path, The image file path or name associated with
                the element. (Path(image).name or Path(image))
            image_manager: object, The ImageManager instance for locating
                images.
            location: tuple, The location of the element.
            parent: object, The parent Element instance.
            children: object or dict[object] or list[object], Child elements.
        """
        self.element = Path(name)
        self.image_manager = image_manager
        self.parent = parent
        self.children = self._get_children(children)
        self._offsetx = location[0] if location is not None else 0
        self._offsety = location[1] if location is not None else 0
        self.location = self.set_location(location)
        self.path_to_origin = [self]
        self.images = {}
        self._name = self.name
        self._image_element = self.image_element
        self._width = self.width
        self._height = self.height
        self._valid = self._check_image_manager_instance()
        self.set_parent(parent)

    def _check_element_path(self) -> bool | Path:
        """
        Check if the element path exists and returns it.

        Returns:
            bool | Path: The element path if exists, False otherwise.
        """
        if path := self.element.exists():
            path = self.element
        if self.image_manager is not None:
            path = [
                path
                for path in self.image_manager.folder_path.iterdir()
                if path.stem == self.element.stem
            ]
            if len(path) == 0:
                return None
            return path[0]
        if not path:
            logger.debug('%s is not a valid image path', self.element)
        return path

    def _check_image_manager_instance(self):
        """
        Check if the Image Manager instance exists and is valid.

        Returns:
            bool: True if valid, False otherwise.
        """
        if self.image_manager is not None:
            path = self._check_element_path()
            if path is None:
                return False
            if self.image_manager.images_map.get(path.stem) is not None:
                return True
            logger.debug('%s is not mapped in the ImageManager instance', path)
            return False
        return False

    @property
    def name(self) -> str:
        """
        Gets the name of the element.

        Returns:
            str : The name of the image element.
        """
        return self.element.stem

    @property
    def image_element(self) -> PIL.Image.Image:
        """
        Gets the PIL.Image object associated with the element.

        Returns:
            PIL.Image: Image element.
        """
        if path:= self._check_element_path():
            return PIL.Image.open(path)
        return path

    @property
    def width(self) -> float:
        """
        Gets the width of the image element.

        Returns:
            int or float: The width of the image element.
        """
        if self._image_element:
            return self._image_element.size[0]
        return 0

    @property
    def height(self) -> float:
        """
        Gets the height of the image element.

        Returns:
            int or float: The height of the image element.
        """
        if self._image_element:
            return self._image_element.size[1]
        return 0

    def visible(self, confidence: float=0.9, timeout: float=0.1) -> bool:
        """
        Checks if the image associated with the element is currently visible.

        Args:
            confidence (float): Confidence level for image localization.
            timeout (float): Time interval to wait for the image.
        
        Returns:
            bool: True if visible, False otherwise.
        """
        if self._check_image_manager_instance():
            return self.image_manager.wait_image(
                self.name,
                confidence=confidence,
                timeout=timeout
            )
        return False

    def _update_children_location(self):
        for element in self.children.values():
            element.set_location()
        logger.debug("Childrens location updated!")

    def set_location(
        self,
        location: tuple = None,
        x: float = None,
        y: float = None
    ) -> tuple | bool:
        """
        Set location to the Element by provide coordinates.

        Args:
            location (tuple, optional): Tuple of coordinates (x, y).
            x (float, optional): X-axis coordinate.
            y (float, optional): Y-axis coordinate.

        Returns:
            tuple | bool: Tuple of coordinates or boolean.
        """
        if all(value is None for value in [location, x, y, self.parent]):
            self._update_children_location()
            return location
        if self.parent is None:
            self._update_children_location()
            return location or (0, 0)
        loc = self.parent.location or (0, 0)
        if location:
            self.location = (loc[0]+location[0], loc[1]+location[1])
            self._update_children_location()
            return self.location
        if x is not None and y is not None:
            self.location = (loc[0]+x, loc[1]+y)
            self._update_children_location()
            return self.location
        self.location = (loc[0] + self._offsetx, loc[1] + self._offsety)
        self._update_children_location()
        return self.location

    def set_walk_path(self, element: object) -> None:
        """ 
        Retrieves the element walk path recursively. 

        Args:
            element (object): The element for which to retrieve the walk path.
        """
        if isinstance(element, Element):
            if element.parent is not None:
                self.path_to_origin.append(element.parent)
                self.set_walk_path(element.parent)

    def wait_till_visible(self, timeout: float | None = 10) -> bool:
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
        if not self._valid:
            logger.info(
                "%s is not an image or the Image Manager is not provided, \
                cannot check if is visible or invisible.",
                self.element
            )
            return False
        return self.image_manager.wait_till_visible(self.name, timeout)

    def locate(
        self,
        confidence: float = 0.85,
        is_image: bool = False
    ) -> Tuple | None:
        """
        Locates the image associated with the element using the ImageManager.

        Args:
            confidence (float): Confidence level for image localization.
                Defaults to 0.85.
            image (bool): If False, will search for the image again,
                else use the last location. Defaults to False.

        Returns:
            bool: True if the image is located, None otherwise.
        """
        if not is_image:
            if self.location is not None:
                return self.location
        if self._valid:
            self.location = self.image_manager.locate_image(
                self.name, confidence
            )
            self._update_children_location()
            return self.location
        logger.error(
            "Cannot locate and element that is not an image or without the \
            Image Manager instance."
        )
        return None

    def _get_children(
        self,
        children: Union[object, Dict[str, object], List[object]]
    ) -> dict:
        """
        Prepares and organizes child elements based on different input types.

        Args:
            children (Element, Dict[str, Element], List[Element]): Child element.

        Returns:
            dict: Dictionary containing child elements mapped by their names.
        """
        match children:
            case c if isinstance(c, dict):
                pass
            case c if isinstance(c, list):
                for child in children:
                    child.parent = self
                children = {child.image.stem: child for child in children}
            case c if isinstance(c, Element):
                children.parent = self
                children = {children.image.stem: children}
            case c if isinstance(c, NoneType):
                children = {}
            case _:
                raise ValueError(f'{type(children)} is not valid for child.')
        return children

    def set_parent(self, parent: object) -> object:
        """ 
        Sets the parent of the element and updates the walk path.

        Args:
            parent (object): Parent Element instance.

        Returns:
            object: The assigned parent object.
        """
        if self.parent is not None:
            self.parent = parent
            parent.children.update({self.element.stem: self})
            self.set_walk_path(self)
        return self.parent

    def set_children(
        self,
        children: Union[object, Dict[str, object], List[object]]
    ) -> dict:
        """ 
        Sets the child elements of the element.

        Args:
            children (Element, Dict[str, Element], List[Element]): Element.

        Returns:
            dict: Dictionary containing the set child elements.
        """
        self.children = self._get_children(children)
        return self.children

    def add_child(
        self,
        children: Union[object, Dict[str, object], List[object]],
        overwrite: bool = False
    ) -> dict:
        """ 
        Adds children elements to the element.

        Args:
            children (Element, Dict[str, Element], List[Element]): Child
                element to be added.
            overwrite (bool, optional): If True, overwrites existing child
                with the same name. Defaults to False.

        Returns:
            dict: Updated dictionary containing child elements.
        """
        children = self._get_children(children)
        for name, child in children.items():
            child_found = self.children.get(name)
            if child_found is not None and overwrite:
                logger.info("Child overwrited: %s", child)
            elif child_found is not None and not overwrite:
                continue
            self.children[name] = child
            logger.info("Child added: %s", child)
        return self.children

    def remove_child(
        self,
        children: Union[object, Dict[str, object], List[object]]
    ) -> dict:
        """ 
        Removes children elements from the existing element.

        Args:
            children (Element, Dict[str, Element], List[Element]): Element.
                to be removed.

        Returns:
            dict: Updated dictionary containing child elements.
        """
        children = self._get_children(children)
        for child in children:
            if self.children.get(child) is not None:
                self.children.pop(child)
                logger.info("Child removed: %s", child)
        return self.children

    def update_child(self, child: object):
        """ 
        Updates an existing child element.

        Args:
            child (object): Child element to be updated.

        Returns:
            bool: True if the child was successfully updated, False otherwise.
        """
        if self.children.get(child) is not None:
            child.parent = self
            self.children[child.element.name] = child
            return True
        return False

    def _click_coordinates(
        self,
        button: str = pyautogui.LEFT,
        offset: tuple = (0, 0),
        times: int = 1,
    ) -> bool:
        """ 
        Clicks on the coordinates of the element.

        Args:
            button (str): Mouse button to click. Defaults to pyautogui.LEFT.
            offset (tuple): Offset coordinates for the click. Defaults to (0, 0).
            times (int): Number of clicks. Defaults to 1.

        Returns:
            bool: True if the click was successful, False otherwise.
        """
        if self.location is None:
            return False
        pyautogui.moveTo(
            self.location[0] + offset[0],
            self.location[1] + offset[1],
            duration=0.1
        )
        pyautogui.click(button=button, clicks=times)
        return True

    def _click_image(
        self,
        offset: tuple = (0, 0),
        confidence: float = 0.9,
        button: str = pyautogui.LEFT,
        times: int = 1
    ) -> bool:
        """ 
        Clicks on the image associated with the element.

        Args:
            offset (tuple, optional): Offset coordinates for the click.
                Defaults to (0, 0).
            confidence (float, optional): Confidence level image localization.
                Defaults to 0.9.
            button (str, optional): Mouse button to click.
                Defaults to pyautogui.LEFT.
            times (int, optional): Number of clicks.
                Defaults to 1.

        Returns:
            bool: True if the click was successful, False otherwise.
        """
        if self._valid:
            if self.visible():
                self.image_manager.click_image(
                    name=self.name,
                    button=button,
                    times=times,
                    offset=offset,
                    confidence=confidence
                )
                return True
            logger.error("%s is not visible and clickable", self.element)
        return False

    def move_to(self, location: tuple = None) -> bool:
        """ 
        Moves the cursor to the specified location or element.

        Args:
            location (tuple, optional): Coords (x, y) to move the cursor to.
                Defaults to None.

        Returns:
            bool: True if the cursor moved successfully, False otherwise.
        """
        if location is None:
            location = self.location
        if isinstance(location, tuple):
            pyautogui.moveTo(location[0], location[1], duration=0.1)
            return True
        logger.error("location provided: %s is not a tuple.", location)
        return False

    def click(
        self,
        offset: Tuple = (0, 0),
        confidence: float = 0.9,
        button: str = pyautogui.LEFT,
        times: int = 1,
        timeout: int | float = 0.3,
        walk: bool = False,
        through: str = 'coordinates',
        fail_safe: bool = False
    ) -> bool:
        """ 
        Performs a click action on the element or its parents in the walk path.

        Args:
            offset (Tuple): Offset coordinates to click to. Defaults to (0, 0).
            confidence (float): Confidence level for image localization.
                Defaults to 0.9.
            button (str): Mouse button to click. Defaults to pyautogui.LEFT.
            times (int): Number of clicks. Defaults to 1.
            timeout (int | float): Waiting timeout before click the element.
                Defaults to 1.
            walk (bool): If True, clicks on all elements in the walk path.
                Defaults to False.
            through (str): Method to click, either 'coordinates' or 'image'.
                Defaults to 'coordinates'.

        Returns:
            bool: True if the click was successful, False otherwise.
        """
        pyautogui.FAILSAFE = fail_safe
        if walk:
            for element in reversed(self.path_to_origin):
                if element is None:
                    continue
                element.click(
                    confidence=confidence,
                    timeout=timeout,
                    walk=False,
                    through=through
                )
            return True
        sleep(timeout)
        if through == 'coordinates':
            clicked = self._click_coordinates(button, offset, times)
            if not clicked:
                return self._click_image(offset, confidence, button, times)
            return clicked
        if through == 'image':
            return self._click_image(offset, confidence, button, times)
        logger.error("There isnot ImageManager instance or location provided")
        return False

    def insert(
        self,
        text: str,
        interval: float = 0,
        enter: bool = False,
        offset: Tuple = (0, 0),
        through: str = "coordinates",
        clear: bool = True
    ) -> None:
        """
        Performs a text insert into the element.

        Args:
            text (str): text to insert in the text box clicked.
            interval (float): interval to write each letter of the text.
            enter (bool): if True press the `enter` hotkey otherwise nothing.
            offset (Tuple): Offset coordinates to click to. Defaults to (0, 0).
            through (str): Method to click, either 'coordinates' or 'image'.
        
        Returns:
            None
        """
        self.click(offset=offset, through=through)
        if clear:
            pyautogui.hotkey("ctrl", "a")
        text = text.as_posix() if isinstance(text, Path) else text
        pyautogui.write(message=text, interval=interval)
        if enter:
            pyautogui.press('enter')
