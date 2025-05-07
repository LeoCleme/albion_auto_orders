"""Element Definitions"""

from pathlib import Path

from src.packages import Element
from src.packages import ImageManager

class Structure:
    """ Structure class. """

    CWD_PATH = Path(__file__).parent.parent.parent.resolve()

    img_manager = ImageManager(CWD_PATH.joinpath("images"))

    ORDERS = Element("orders", img_manager, (1387, 495))

    SEARCH = Element("search", img_manager, (592, 270))

    CATEGORY = Element("category", img_manager, (766, 270))

    TIER = Element("tier", img_manager, (938, 270))

    ENCHANTMENT = Element("enchantment", img_manager, (1110, 270))

    CLOSE_MARKET = Element("close_market", img_manager, (1350, 180))

    BUY_ORDER_BUTTON = Element("buy_order_button", img_manager, (1270, 434))

    CLOSE_BUY_ORDER = Element("close_buy_order", img_manager, (936, 306))

    CREATE_BUY_ORDER = Element("create_buy_order", img_manager, (880, 727))

    PRICE_INPUT = Element("price", img_manager, (513, 630))  # (640, 630)

    QUALITY_SELECTOR = Element("quality", img_manager, (826, 396)) # first 28 to - 27

    CONFIRM_BUY_ORDER = Element("confirm_buy_order", img_manager, (857, 556))

    REGISTERED_ORDERS = Element("registered_orders", img_manager, (1384, 582))

    REMOVE_OLD_ORDER = Element("remove_old_order", img_manager, (1317, 410))

    BOUGHT_ORDERS = Element("bought_orders", img_manager, (1384, 740))

    TAKE_ITEM = Element("take_item", img_manager, (1270, 427))

    MATERIALS = Element("materials", img_manager, (783, 622))

    RUNE = Element("rune", img_manager, (950, 753))

    SOUL = Element("soul", img_manager, (950, 783))

    ITEM_NUMBER = Element("item_number", img_manager, (576, 572))

    ADD_ITEM_SILVER = Element("add_item_silver", img_manager, (860, 628))