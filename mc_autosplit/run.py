import msvcrt
import time
from threading import Thread

from mc_autosplit.utils.exception import FailedToReadAdvancements
from mc_autosplit.utils.mc_utils import get_last_played_level, get_advancements
from mc_autosplit.splitting import handle_advancement_changes
from mc_autosplit.watcher import PathWatcher


class Runner:

    def __init__(self):
        initialised = False
        while not initialised:
            try:
                _, self.level_path = get_last_played_level()
                self.advancements = get_advancements(self.level_path)
                self.advancements_watcher = PathWatcher(self.level_path / 'advancements',
                                                        self.advancement_watcher_callback)
                self.user_inp_thread = Thread(target=self.watch_user_input)
                initialised = True
            except FileNotFoundError:
                print('No levels found, sleeping for 5 seconds...')
                time.sleep(5)

    def reset(self, level_path=None):
        self.level_path = None
        while self.level_path is None:
            try:
                print('Resetting...')
                self.level_path = level_path or get_last_played_level()[1]
            except FileNotFoundError:
                print('Failed to find level, sleeping for 5 seconds...')
                time.sleep(5)

        print('Now watching:', self.level_path)
        self.advancements = get_advancements(self.level_path)
        self.advancements_watcher.stop()
        self.advancements_watcher = PathWatcher(self.level_path / 'advancements',
                                                self.advancement_watcher_callback)
        self.advancements_watcher.start()

    def advancement_watcher_callback(self, _, __):
        self.check_advancements_changed()

    def _check_advancements_changed(self):
        advancements_updated = get_advancements(self.level_path)
        if advancements_updated != self.advancements:
            new_advancements = set(advancements_updated) - set(self.advancements)
            print('Detected Advancements: ', new_advancements)
            handle_advancement_changes(set(self.advancements), new_advancements)
            self.advancements = advancements_updated

    def check_advancements_changed(self):
        have_checked = False
        while not have_checked:
            try:
                self._check_advancements_changed()
                have_checked = True
            except FileNotFoundError:
                print('World being watched has been disappeared!')
                self.reset()
                have_checked = True
            except FailedToReadAdvancements:
                print('Failed to read advancements... trying again in 1 second')
                time.sleep(1)

    def watch_user_input(self):
        while True:
            input_char = msvcrt.getch()
            if input_char == 'r':
                self.reset()

    def check_for_world_change(self):
        try:
            _, last_played_path = get_last_played_level()
            if last_played_path != self.level_path:
                self.reset(last_played_path)
        except FileNotFoundError:
            self.reset()

    def watch_saves(self):
        while True:
            self.check_for_world_change()
            time.sleep(3)

    def run(self):
        self.user_inp_thread.start()

        print('Watching advancements at:', self.level_path)
        self.advancements_watcher.start()

        self.watch_saves()


if __name__ == '__main__':
    runner = Runner()
    runner.run()
