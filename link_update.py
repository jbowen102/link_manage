import os
import re


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
    # Use lexists() instead of exists() because exists() returns False if link exists but is broken).
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
        link_dir = os.path.dirname(link_path)
        new_target_path = os.path.relpath(new_target_path, start=link_dir)

    os.remove(link_path)
    os.symlink(new_target_path, link_path)
    print("Replaced target path\n\t'%s'\nwith\n\t'%s'" % (old_target_path, new_target_path))

