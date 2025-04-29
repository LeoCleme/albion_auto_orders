
from pathlib import Path

from src.config.structure import Structure
from pandas import DataFrame, read_excel
import pyautogui
import pyperclip

def get_structure():
    return Structure()

orders_file = Path("orders.xlsx")
if not orders_file.exists():
    df = DataFrame(columns=["Item", "Price"])
else:    
    df = read_excel(orders_file)
struct = get_structure()

MAP_ITEMS = {
    "mage": ["cowl", "robe", "sandals"],
    "warrior": ["helmet", "armor", "boots"],
    "ranger": ["hood", "jacket", "shoes"]
}

struct.ORDERS.click()
struct.CATEGORY.click()
struct.CATEGORY.click(offset=(0, 81))

struct.BOUGHT_ORDERS.click()


for category, items in MAP_ITEMS.items():
    for item in items:
        struct.SEARCH.insert(f"royal {item}")
        tier_init = 135
        for i in range(5):
            enchantment_init = 54
            struct.TIER.click()
            struct.TIER.click(offset=(0, tier_init))
            for j in range(4):
                struct.ENCHANTMENT.click()
                struct.ENCHANTMENT.click(offset=(0, enchantment_init))
                item_name = f"{item} {i} {j}"
                if item_name == f"{item} 4 3" or item_name == f"{item} 3 3":
                    continue
                struct.BUY_ORDER_BUTTON.click()
                highest_price = 0
                for quality in range(4):
                    struct.QUALITY_SELECTOR.click()
                    struct.QUALITY_SELECTOR.click(offset=(0, (quality + 1) * 27))
                    struct.PRICE_INPUT.click(offset=(100, 0))
                    pyautogui.hotkey("ctrl", "c")
                    value = pyperclip.paste()
                    casted_value = int(value)
                    if casted_value > 60000:
                        continue
                    elif casted_value < 10000:
                        highest_price = 10000
                    else:
                        highest_price = casted_value if casted_value > highest_price else highest_price
                if highest_price == 0:
                    struct.CLOSE_BUY_ORDER.click()
                    enchantment_init += 27
                    continue
                found = df[df.Item == item_name]
                if found.empty:
                    df.loc[len(df)] = [item_name, highest_price + 1]
                    struct.QUALITY_SELECTOR.click()
                    struct.QUALITY_SELECTOR.click(offset=(0, 27))
                    struct.PRICE_INPUT.insert(str(highest_price + 1), offset=(100, 0))
                    struct.CREATE_BUY_ORDER.click()
                    struct.CONFIRM_BUY_ORDER.click()
                else:
                    previous_price = df.loc[found.index.values[0], "Price"]
                    if highest_price > previous_price:
                        struct.CLOSE_BUY_ORDER.click()
                        struct.REGISTERED_ORDERS.click()
                        struct.SEARCH.insert(f"royal {item}")
                        struct.TIER.click()    
                        struct.TIER.click(offset=(0, tier_init))
                        struct.ENCHANTMENT.click()
                        struct.ENCHANTMENT.click(offset=(0, enchantment_init))
                        struct.REMOVE_OLD_ORDER.click()
                        struct.ORDERS.click()
                        struct.BUY_ORDER_BUTTON.click()
                        df.loc[found.index.values[0], "Price"] = highest_price + 1
                        struct.QUALITY_SELECTOR.click()
                        struct.QUALITY_SELECTOR.click(offset=(0, 27))
                        struct.PRICE_INPUT.insert(str(highest_price + 1), offset=(100, 0))
                        struct.CREATE_BUY_ORDER.click()
                        struct.CONFIRM_BUY_ORDER.click()
                struct.CLOSE_BUY_ORDER.click()
                enchantment_init += 27
            tier_init += 27

df.to_excel("orders.xlsx", index=False)


def main():
    print("Hello from albion-auto-orders!")


if __name__ == "__main__":
    main()
