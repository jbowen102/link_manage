import os
import re
import colorama


# dir path where this script is stored
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# https://stackoverflow.com/questions/29768937/return-the-file-path-of-the-file-not-the-current-directory


# os.path.islink() test if something is a symlink. False if link doesn't exist. Returns True for broken symlinks
# os.readlink() # get path string where link points. Works even if link broken.
# os.path.realpath() # get 'canonical' path to file, eliminating symlinks in path.
# os.path.exists(os.readlink()) # figure out if link broken.
# os.path.lexists() # test whether a symlink exists (broken or not)
# os.symlink(src, dst) # 'Create a symbolic link pointing to src named dst.' allows creation of broken links (bad dest path)
# os.path.relpath() # get relative path to use w/ os.symlink()
# https://stackoverflow.com/questions/11068419/how-to-check-if-file-is-a-symlink-in-python
# https://stackoverflow.com/questions/9793631/creating-a-relative-symlink-in-python-without-using-os-chdir


def replace_link_target(link_path, new_target_path, relative=False):
    """Replace a link's target with new target path. Set as relative
    link if relative set to True.
    """
    # Use lexists() instead of exists() because exists() returns False if link exists but is broken.
    # Check path exists.
    if not os.path.lexists(link_path):
        raise Exception("Invalid path specified from link_path.")

    # Check link_path is actually a symlink
    elif not os.path.islink(link_path):
        raise Exception("link_path does not refer to a symlink.")

    elif not os.path.exists(os.path.realpath(new_target_path)):
        raise Exception("new_target_path is an invalid path.")

    old_target_path = os.readlink(link_path)

    if relative:
        # Use realpath to resolve all symlinks in each path so they have as much
        # path in common for relative path use.
        # This makes the relative path as short as possible and w/ fewer chances
        # for breaking.
        link_dir = os.path.realpath(os.path.dirname(link_path))
        new_target_path = os.path.realpath(new_target_path)
        new_target_path = os.path.relpath(new_target_path, start=link_dir)

    os.remove(link_path)
    os.symlink(new_target_path, link_path)
    #                   (src <- dst)
    print("Replaced target path\n\t'%s'\nwith\n\t'%s'" % (old_target_path, new_target_path))


def list_links_in_dir(dir_path):
    # one level only
    dir_path = os.path.realpath(dir_path)

    if not os.path.exists(dir_path):
        raise Exception("dir_path not found.")
    elif not os.path.isdir(dir_path):
        raise Exception("dir_path should be a directory.")

    dir_contents = os.listdir(dir_path)
    dir_contents.sort()

    print("")
    for item in dir_contents:
        item_path = os.path.join(dir_path, item)
        if os.path.islink(item_path):
            link_target = os.readlink(item_path)
            broken = not os.path.exists(os.path.realpath(item_path))
            if broken:
                colorama.init(autoreset=True)
                print("%s -> " % item_path + colorama.Back.RED + "%s" % link_target)
                # https://www.devdungeon.com/content/colorize-terminal-output-python
                # https://github.com/tartley/colorama
            else:
                print("%s -> %s" % (item_path, link_target))