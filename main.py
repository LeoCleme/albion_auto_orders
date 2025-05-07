
from pathlib import Path
from time import sleep

from src.config.structure import Structure
from pandas import DataFrame, read_excel
import pyautogui
import pyperclip

def get_structure():
    return Structure()

orders_file = Path("fort_sterling_orders.xlsx")
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


# struct.BOUGHT_ORDERS.click()

# indices_to_remove = []
# for row in df.itertuples():
#     item_name, tier, enchant = row.Item.split()
#     struct.SEARCH.insert(f"royal {item_name}")
#     struct.TIER.click()
#     struct.TIER.click(offset=(0, 135 + (int(tier) * 27)))
#     struct.ENCHANTMENT.click()
#     struct.ENCHANTMENT.click(offset=(0, 54 + (int(enchant) * 27)))
#     sleep(0.01)
#     visible = struct.TAKE_ITEM.visible(timeout=0.01)
#     if visible:
#         struct.TAKE_ITEM.click()
#         indices_to_remove.append(row.Index)
#         if int(tier) > 3:
#             continue
#         if int(enchant) == 0:
#             struct.ORDERS.click()
#             struct.CATEGORY.click()
#             struct.MATERIALS.click()
#             struct.RUNE.click()
#             struct.BUY_ORDER_BUTTON.click()
#             item_number = 0
#             if item_name in ["hood", "cowl", "helmet", "shoes", "boots", "sandals"]:
#                 item_number = 96
#             elif item_name in ["jacket", "robe", "armor"]:
#                 item_number = 192
#             struct.ITEM_NUMBER.insert(str(item_number))
#             struct.ADD_ITEM_SILVER.click()
#             struct.CREATE_BUY_ORDER.click()
#             struct.CONFIRM_BUY_ORDER.click()
#             struct.CATEGORY.click()
#             struct.MATERIALS.click()
#             struct.SOUL.click()
#             struct.BUY_ORDER_BUTTON.click()
#             item_number = 0
#             if item_name in ["hood", "cowl", "helmet", "shoes", "boots", "sandals"]:
#                 item_number = 96
#             elif item_name in ["jacket", "robe", "armor"]:
#                 item_number = 192
#             struct.ITEM_NUMBER.insert(str(item_number))
#             struct.ADD_ITEM_SILVER.click()
#             struct.CREATE_BUY_ORDER.click()
#             struct.CONFIRM_BUY_ORDER.click()
#             struct.CATEGORY.click()
#             struct.CATEGORY.click(offset=(0, 81))
#         if int(enchant) == 1:
#             struct.ORDERS.click()
#             struct.CATEGORY.click()
#             struct.MATERIALS.click()
#             struct.SOUL.click()
#             struct.BUY_ORDER_BUTTON.click()
#             item_number = 0
#             if item_name in ["hood", "cowl", "helmet", "shoes", "boots", "sandals"]:
#                 item_number = 96
#             elif item_name in ["jacket", "robe", "armor"]:
#                 item_number = 192
#             struct.ITEM_NUMBER.insert(str(item_number))
#             struct.ADD_ITEM_SILVER.click()
#             struct.CREATE_BUY_ORDER.click()
#             struct.CONFIRM_BUY_ORDER.click()
#             struct.CATEGORY.click()
#             struct.CATEGORY.click(offset=(0, 81))

# df.drop(indices_to_remove, inplace=True)

struct.CATEGORY.click()
struct.CATEGORY.click(offset=(0, 81))

struct.ORDERS.click()
for category, items in MAP_ITEMS.items():
    for item in items:
        struct.SEARCH.insert(f"royal {item}")
        tier_init = 135
        for i in range(5):
            enchantment_init = 54
            struct.TIER.click()
            struct.TIER.click(offset=(0, tier_init))
            for j in range(5):
                struct.ENCHANTMENT.click()
                struct.ENCHANTMENT.click(offset=(0, enchantment_init))
                item_name = f"{item} {i} {j}"
                if item_name == f"{item} 4 3" or item_name == f"{item} 3 3":
                    continue
                struct.BUY_ORDER_BUTTON.click()
                highest_price = 0
                found = df[df.Item == item_name]
                casted_value_found = 0
                for quality in range(4):
                    if casted_value_found > 62000:
                        continue
                    struct.QUALITY_SELECTOR.click()
                    struct.QUALITY_SELECTOR.click(offset=(0, (quality + 1) * 27))
                    struct.PRICE_INPUT.click(offset=(100, 0))
                    pyautogui.hotkey("ctrl", "c")
                    value = pyperclip.paste()
                    casted_value = int(value)
                    previous_price = df.loc[found.index.values[0], "Price"] if not found.empty else None
                    if previous_price is not None:
                        if casted_value == previous_price:
                            continue
                    if casted_value > 72000 and i <= 1:
                        casted_value_found = casted_value
                        continue
                    elif casted_value > 120000:
                        casted_value_found = casted_value
                        continue
                    elif casted_value < 10000:
                        highest_price = 10000
                    else:
                        highest_price = casted_value if casted_value > highest_price else highest_price
                if highest_price == 0:
                    struct.CLOSE_BUY_ORDER.click()
                    enchantment_init += 27
                    continue
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

df.to_excel("fort_sterling_orders.xlsx", index=False)


def main():
    print("Hello from albion-auto-orders!")


if __name__ == "__main__":
    main()
