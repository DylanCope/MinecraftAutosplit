import os

import win32file
import win32event
import win32con

from mc_autosplit.utils.stoppable_thread import StoppableThread


class PathWatcher(StoppableThread):

    def __init__(self, path_to_watch, callback):
        super(PathWatcher, self).__init__(target=self.watch_path)
        self.path_to_watch = str(path_to_watch)
        self.callback = callback

    def watch_path(self):
        #
        # FindFirstChangeNotification sets up a handle for watching
        #  file changes. The first parameter is the path to be
        #  watched; the second is a boolean indicating whether the
        #  directories underneath the one specified are to be watched;
        #  the third is a list of flags as to what kind of changes to
        #  watch for. We're just looking at file additions / deletions.
        #
        change_handle = win32file.FindFirstChangeNotification(
            self.path_to_watch, 0, win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
        )

        #
        # Loop forever, listing any file changes. The WaitFor... will
        #  time out every half a second allowing for keyboard interrupts
        #  to terminate the loop.
        #
        try:
            old_path_contents = dict([
                (f, None) for f in os.listdir(self.path_to_watch)
            ])
            while not self.stopped():
                result = win32event.WaitForSingleObject(change_handle, 500)

                #
                # If the WaitFor... returned because of a notification (as
                #  opposed to timing out or some error) then look for the
                #  changes in the directory contents.
                #
                if result == win32con.WAIT_OBJECT_0:
                    new_path_contents = dict([
                        (f, None) for f in os.listdir(self.path_to_watch)
                    ])
                    self.callback(old_path_contents, new_path_contents)
                    old_path_contents = new_path_contents
                    win32file.FindNextChangeNotification(change_handle)
        except FileNotFoundError:
            print('Failed to find', self.path_to_watch)
        finally:
            win32file.FindCloseChangeNotification(change_handle)

        print('Watcher closed for', self.path_to_watch)
