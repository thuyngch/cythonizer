from glob import glob
import os
import argparse
import warnings


# ------------------------------------------------------------------------------
#  ArgumentParser
# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument("mode", type=str, default='encrypt',
                    help="Cythonization mode [encrypt, decrypt, clean]")

parser.add_argument("dir", type=str,
                    help="The directory for cythonization")

parser.add_argument("--no-backup", action='store_true', default=False,
                    help="Do not backup the dir")

parser.add_argument("--compile-file", type=str, default=None,
                    help="Write compile commands into a script file")

args = parser.parse_args()


# ------------------------------------------------------------------------------
#  Utils
# ------------------------------------------------------------------------------
SETUP_TEMPLATE = 'templates/setup.py'
COMPILE_HEADER_TEMPLATE = 'templates/compile_header.sh'
COMPILE_ELEMENT_TEMPLATE = 'templates/compile_element.sh'


def _execute_and_print(cmd):
    os.system(cmd)
    print(cmd)


def backup_folder(folder):
    if folder[-1] == '/':
        folder = folder[:-1]
    dirname = os.path.dirname(folder)
    basename = os.path.basename(folder)
    backup_dir = os.path.join(dirname, "."+basename+".backup")
    os.system("cp -r \'{}\' \'{}\'".format(folder, backup_dir))
    print("Folder \'{}\' is backuped at \'{}\'".format(folder, backup_dir))


def encrypt_folder(folder):
    # Get files, excepting __init__.py
    files = sorted(glob(os.path.join(folder, "*.py")))
    files = list(filter(  # do not get '__init__.py'
        lambda x: False if os.path.basename(x) == '__init__.py' else True,
        files))

    # Create src folder
    src_folder = os.path.join(folder, 'src')
    os.makedirs(src_folder, exist_ok=True)

    # Move all files into src folder
    for file in files:
        dst_file = os.path.join(src_folder, os.path.basename(file))
        os.system("mv \'{}\' \'{}\'".format(file, dst_file))

    # Copy setup.py
    os.system("cp \'{}\' \'{}\'".format(SETUP_TEMPLATE, folder))
    print("Folder \'{}\' is encrypted".format(folder))


def decrypt_folder(folder):
    if folder[-1] == '/':
        folder = folder[:-1]
    dirname = os.path.dirname(folder)
    basename = os.path.basename(folder)
    backup_dir = os.path.join(dirname, "."+basename+".backup")

    if not os.path.exists(backup_dir):
        warnings.warn("Folder backup \'{}\' doesn't exist!".format(backup_dir))
    else:
        os.system("rm -rf {}".format(folder))
        os.system("mv {} {}".format(backup_dir, folder))
        print("Folder \'{}\' is decrypted".format(folder))


def clean_folder(folder):
    # Find and remove .so files
    so_files = sorted(glob(os.path.join(folder, "*.so")))
    for so_file in so_files:
        cmd = "rm {}".format(so_file)
        _execute_and_print(cmd)

    # Find and remove setup.py file
    setup_file = os.path.join(folder, 'setup.py')
    if os.path.exists(setup_file):
        cmd = "rm {}".format(setup_file)
        _execute_and_print(cmd)

    # Find and remove __pycache__ folder
    pycache_folder = os.path.join(folder, '__pycache__')
    if os.path.exists(pycache_folder):
        cmd = "rm -rf {}".format(pycache_folder)
        _execute_and_print(cmd)


def create_compile_file(compile_file):
    with open(COMPILE_HEADER_TEMPLATE, 'r') as fp:
        content = fp.read()
    with open(compile_file, 'w') as fp:
        fp.write(content)
    print("Compile file is created at \'{}\'".format(compile_file))


def write_compile_commands(compile_file, folder):
    with open(COMPILE_ELEMENT_TEMPLATE, 'r') as fp:
        content = fp.read()
        content = content.replace("xxxxx", folder)
    with open(compile_file, 'a') as fp:
        fp.write(content)
    print("Compile file \'{}\' is appended".format(compile_file))


# ------------------------------------------------------------------------------
#  Main execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # Encrypt mode
    if args.mode == 'encrypt':
        # Backup the dir
        if not args.no_backup:
            backup_folder(args.dir)

        # Encrypt folder
        encrypt_folder(args.dir)

        # Output a compile file
        if args.compile_file is not None:
            # If not exist, create one from template
            if not os.path.exists(args.compile_file):
                create_compile_file(args.compile_file)

            # Write (append mode) compile commands for the examined folder
            write_compile_commands(args.compile_file, args.dir)

    # Decrypt mode
    elif args.mode == 'decrypt':
        decrypt_folder(args.dir)

    # Clean mode
    elif args.mode == 'clean':
        clean_folder(args.dir)

    # Not support
    else:
        raise NotImplementedError(
            "Mode {} is not supported!".format(args.mode))
