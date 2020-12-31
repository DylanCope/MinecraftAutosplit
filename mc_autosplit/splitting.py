import keyboard
import time


def press_split_hotkey():
    keyboard.press('home')
    time.sleep(0.5)


def handle_advancement_changes(old_advancements, new_advancements):
    if 'minecraft:story/enter_the_nether' in new_advancements:
        print('Entered the Nether!')
        press_split_hotkey()

    if 'minecraft:nether/find_fortress' in new_advancements:
        print('Entered a Nether Fortress!')
        press_split_hotkey()

    if 'minecraft:nether/obtain_blaze_rod' in new_advancements:
        print('Obtained a Blaze rod!')
        press_split_hotkey()
        if 'minecraft:nether/find_fortress' not in old_advancements:
            print('Detected found rod before entering fortress - splitting twice...')
            press_split_hotkey()

    if 'minecraft:story/follow_ender_eye' in new_advancements:
        print('Entered Stronghold!')
        press_split_hotkey()

    if 'minecraft:story/enter_the_end' in new_advancements:
        print('Entered the End!')
        press_split_hotkey()
