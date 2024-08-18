import os
import colorama
import re

class BadTargetError(Exception):
    pass


# dir path where this script is stored
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# https://stackoverflow.com/questions/29768937/return-the-file-path-of-the-file-not-the-current-directory


def replace_link_target(link_path, new_target_path, make_relative=False, prompt=False):
    """Replace a link's target with new target path. Set as relative
    link if relative set to True. Otherwise use new_target_path as entered
    (rel or abs).
    If new_target_path is a relative path, it is interpreted as relative to
    existing link's directory, not working dir.
    """
    link_abspath = os.path.abspath(os.path.join(os.getcwd(), link_path))
    # Check path exists.
    # Use lexists() instead of exists() because exists() returns False if link
    # exists but is broken.
    if not os.path.lexists(link_abspath):
        raise Exception("Invalid path specified from link_path.")

    # Check link_path is actually a symlink
    elif not os.path.islink(link_abspath):
        raise Exception("link_path does not refer to a symlink.")

    # Establish the basis for relative link targets
    # Symlinks resolved in path.
    link_realdir = os.path.realpath(os.path.dirname(link_abspath))

    # Determine if new link target is relative
    if not new_target_path:
        raise BadTargetError("new_target_path cannot be empty string.")
        # Without this, abspath() will join empty string to a basepath, which
        # results in a valid (but unintended) path.
    elif os.path.isabs(new_target_path):
        new_target_abspath = new_target_path
    else:
        new_target_abspath = os.path.abspath(os.path.join(link_realdir,
                                                            new_target_path))
    if not os.path.exists(new_target_abspath):
        raise BadTargetError("new_target_path is an invalid path.")

    old_target_path = os.readlink(link_abspath)
    # Determine if old link target is relative
    if os.path.isabs(old_target_path):
        old_target_abspath = old_target_path
    else:
        # Evaluate the absolute path of the link target, based on link dir.
        old_target_abspath = os.path.abspath(os.path.join(link_realdir,
                                                            old_target_path))

    if make_relative:
        # Use realpath to resolve all symlinks in each path so they have as much
        # in common for relative path eval.
        # This makes the relative path as short as possible and w/ fewer chances
        # for breaking later.
        new_target_realpath = os.path.realpath(new_target_abspath)
        new_target_path = os.path.relpath(new_target_realpath, start=link_realdir)

    if old_target_path == new_target_path:
        # No replacement needed
        # print("No replacement done (new target same as old):\n\t'%s'"
        #                                                     % old_target_path)
        return

    # Confirm before making link relative. Sometimes result is unexpected.
    if prompt:
        print("Replace target path?\n\t" +
                                "'%s'" % old_target_path +
                                "\nwith\n\t" + colorama.Fore.CYAN + "'%s'"
                                % new_target_path + colorama.Style.RESET_ALL)
        answer = input("[Y/N]> ")
        if answer.lower() == "y":
            pass
        else:
            return

    os.remove(link_abspath)
    os.symlink(new_target_path, link_abspath) # use new_target_path as entered
    #                   (src <- dst)

    if os.path.exists(old_target_abspath):
        broken = False
    else:
        broken = True

    if broken:
        colorama.init()
        print("Replaced target path\n\t" + colorama.Back.RED +
                                    "'%s'" % old_target_path +
                                    colorama.Style.RESET_ALL + "\nwith\n\t'%s'"
                                    % new_target_path)
        # https://www.devdungeon.com/content/colorize-terminal-output-python
        # https://github.com/tartley/colorama
    else:
        print("Replaced target path\n\t'%s'\nwith\n\t'%s'" % (old_target_path, new_target_path))


def find_links_in_dir(dir_path, spec_target=None, replace_broken=False,
                                                                make_rel=False):
    """Find all symlinks directly under dir_path.
    If spec_target (path) specified, only links pointing to spec_target will be found.
    If replace_broken is set to True, user will be prompted for a new target
    when a broken link is encountered, unless link can be resolved with simple
    space-replace operation on target.
    If make_rel is set to True, every link found will be converted to relative.
    """
    # one level only
    dir_abspath = os.path.abspath(os.path.join(os.getcwd(), dir_path))

    if not os.path.exists(dir_abspath):
        raise Exception("dir_path not found.")
    elif not os.path.isdir(dir_abspath):
        raise Exception("dir_path should be a directory.")

    if spec_target:
        # If target is relative, treat as relative to dir_path
        if os.path.isabs(spec_target):
            spec_target_abspath = spec_target
        else:
            spec_target_abspath = os.path.abspath(os.path.join(dir_abspath,
                                                                spec_target))
        spec_target_realpath = os.path.realpath(spec_target_abspath)
        # Does not have to exist. May be searching for old location to fix.

    dir_contents = os.listdir(dir_abspath)
    dir_contents.sort()

    for item in dir_contents:
        item_path = os.path.join(dir_abspath, item)
        item_abspath = os.path.abspath(os.path.join(os.getcwd(), item_path))
        item_realpath = os.path.realpath(item_abspath) # Resolves link if it exists

        if os.path.islink(item_abspath):
            if spec_target and spec_target_realpath != item_realpath:
                # Skip if only searching for links pointing to spec_target, and
                # current link has a different target.
                # Can't use os.path.samefile() because that requires valid paths.
                # May be searching for broken links to specific old dests.
                continue
            link_target = os.readlink(item_abspath)
            broken = not os.path.exists(item_realpath)
            if broken:
                colorama.init(autoreset=True)
                print("%s -> " % item_path + colorama.Back.RED + "%s" % link_target)
                # https://www.devdungeon.com/content/colorize-terminal-output-python
                # https://github.com/tartley/colorama
                if replace_broken:
                    # Try fixing certain cases automatically

                    # Try fixing by replacing spaces in target filename.
                    # Only replaces spaces in basename, so won't fix case
                    # where dir in path has had spaces replaced.
                    if " " in os.path.basename(item_realpath):
                        target_name_no_spaces = os.path.basename(
                                                item_realpath).replace(" ", "_")
                        target_path_no_spaces = os.path.join(
                                                os.path.dirname(item_realpath),
                                                        target_name_no_spaces)
                        if os.path.exists(target_path_no_spaces):
                            new_target_str = target_path_no_spaces
                            replace_link_target(item_abspath, new_target_str,
                                                        make_relative=make_rel)
                            link_fixed = True
                        else:
                            link_fixed = False
                    else:
                        link_fixed = False

                    # Try fixing incorrect username in home dir path.
                    # Check if home subpath is the issue before entering block.
                    user_home_matches = re.findall(r"^/home/user\d{3}/",
                                                                  item_realpath)
                    assert len(user_home_matches) in [0, 1], "Found more than one \
                            user home match in %s" % os.path.basename(item_realpath)
                    if user_home_matches and not os.path.isdir(user_home_matches[0]):
                        replacement_home_path = "/home/%s/" % os.getlogin()
                        target_path_user_fix = item_realpath.replace(
                                    user_home_matches[0], replacement_home_path)
                        if os.path.exists(target_path_user_fix):
                            new_target_str = target_path_user_fix
                            answer = input("Replace with this path?:\n\t%s"
                                "\n['Y' for yes or 'M' to manual entry]> " % target_path_user_fix)
                            if answer.upper() == "Y":
                                replace_link_target(item_abspath, new_target_str,
                                                        make_relative=make_rel)
                                link_fixed = True
                            else:
                                # Anything but 'Y' triggers manual path entry
                                link_fixed = False

                        else:
                            link_fixed = False
                    else:
                        link_fixed = False

                    while not link_fixed:
                        new_target_str = input("Enter new target:")
                        try:
                            replace_link_target(item_abspath, new_target_str,
                                                        make_relative=make_rel)
                        except BadTargetError:
                            continue
                        else: # only runs if no exception
                            link_fixed = True
            else:
                print("%s -> %s" % (item_path, link_target))
                if make_rel:
                    replace_link_target(item_abspath, link_target,
                                                make_relative=True, prompt=True)


def find_links_in_tree(dir_path, spec_target=None, replace_broken=False,
                                            make_rel=False, follow_links=False):
    start_dir = os.path.abspath(os.path.join(os.getcwd(), dir_path))
    """Find all symlinks at any level under dir_path.
    """

    if not os.path.exists(start_dir):
        raise Exception("dir_path not found.")
    elif not os.path.isdir(start_dir):
        raise Exception("dir_path should be a directory.")

    for root_dir, dir_list, file_list in os.walk(start_dir,
                                                    followlinks=follow_links):
        # https://stackoverflow.com/questions/6639394/what-is-the-python-way-to-walk-a-directory-tree
        find_links_in_dir(root_dir, spec_target, replace_broken, make_rel)