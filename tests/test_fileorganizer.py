import unittest
import os
from functools import reduce

import pyfakefs.fake_filesystem_unittest as fakefs

from epflmanager.io.fileorganizer import Directory, Path
import epflmanager.components as components

from components import setup_console

class FileOrganizerTest(fakefs.TestCase):

    def setUp(self):
        setup_console()
        self.setUpPyfakefs()

    def tearDown(self):
        pass

    #======================== HELPER FUNCTIONS ========================#

    def create_path(self, *dirs):
        """ Return a path with all dirs joined """
        return reduce(lambda p, d: os.path.join(p,d), dirs)

    @property
    def root(self):
        """ Return the root of the filesystem. """
        # TODO Windows compatibility
        return "/"

    def assertPathEqual(self, p1, p2, *args, **kwargs):
        """ Test equality between two paths.
        Normalize paths for a meaningful testing """

        norm_paths = [os.path.normpath(p) for p in [p1,p2]]
        all_args = norm_paths + list(args)
        self.assertEqual(*all_args, **kwargs)

    def create_basic_filesystem(self):
        """ Create the following file tree:

            Root
             ├─ Dir1
             │   ├─ EmptyDir
             │   ├─ File1
             │   ├─ EmptyFile
             │   ├─ .hiddenFile
             │   └─ File with spaces
             ├─ Dir2
             ├─ FileInRoot
             ├─ Dir with spaces
             │   ├─ File2
             │   └─ File2 with spaces
             └─ .hiddenDir

        Return the root as a Directory for convenience

        """
        os.mkdir("Dir1")
        os.chdir("Dir1")
        os.mkdir("EmptyDir")
        self.fs.CreateFile("File1", contents="Some content")
        self.fs.CreateFile("EmptyFile")
        self.fs.CreateFile(".hiddenFile", contents="Some content for the hidden file")
        self.fs.CreateFile("File with spaces", contents="Some content for the file with spaces")
        os.chdir("..")

        os.mkdir("Dir2")
        self.fs.CreateFile("FileInRoot", contents="Some content for the file in root")

        os.mkdir("Dir with spaces")
        os.chdir("Dir with spaces")
        self.fs.CreateFile("File2", contents="Some content for File2 inside dir with spaces")
        self.fs.CreateFile("File2 with spaces", contents="Some content for File2 with spaces inside dir with spaces")
        os.chdir("..")

        os.mkdir(".hiddenDir")

        return Directory(self.root)(".")

    #========================= TESTS ON Path ==========================#

    def test_repr(self):
        p = Path("/")("new")
        self.assertEqual("<Path: new>", repr(p))

    def test_is_file(self):
        root = self.create_basic_filesystem()
        file_ = Path(root)("FileInRoot")

        self.assertFalse(root.is_file())
        self.assertTrue(file_.is_file())

    def test_fullpath_with_parent_as_string(self):
        dir_creator = Directory(self.root)
        dirs = ["test", "spam", "egg"]
        for d in dirs:
            self.assertPathEqual(dir_creator(d).fullpath(), os.path.join(self.root,d))

    def test_fullpath_with_parent_as_path(self):
        root_path = Path(self.root)(".")
        dir_creator = Directory(root_path)
        dirs = ["test", "spam", "egg"]
        for d in dirs:
            self.assertPathEqual(dir_creator(d).fullpath(), os.path.join(self.root,d))

    def test_fullpath_with_multi_level_hierarchy(self):
        root_path = Path(self.root)('.')
        dirs = ["test", "spam", "egg"]
        parent = root_path
        for d in dirs:
            parent = Path(parent)(d)

        expected = self.create_path(self.root, *dirs)
        self.assertPathEqual(expected, parent.fullpath())

    def test_path_exists(self):
        dir_creator = Path(self.root)
        dirs = ["test", "spam", "egg"]
        created_dirs = [ dir_creator(d) for d in dirs ]

        for d in created_dirs:
            self.assertFalse(d.exists())
            os.mkdir(d.fullpath())
            self.assertTrue(d.exists())

    def test_is_dir(self):
        root_path = Path(self.root)('.')
        self.assertTrue(root_path.is_dir())

        dirs = ["test", "spam", "egg"]
        created_dirs = [ Path(root_path)(d) for d in dirs ]

        for d in created_dirs:
            self.assertFalse(d.exists())
            os.mkdir(d.fullpath())
            self.assertTrue(d.exists())
            self.assertTrue(d.is_dir())

    def test_split_parent_on_root_path(self):
        res = Path.split_parent(self.root)
        expected = (self.root, "")
        self.assertEqual(res, expected)

    def test_split_parent_with_empty_path(self):
        res = Path.split_parent("")
        expected = ("", "")
        self.assertEqual(res, expected)

    def test_split_parent_with_file(self):
        dirname = "test"
        filename = "fileA"
        res = Path.split_parent(self.create_path(self.root,dirname,filename))
        expected = (self.create_path(self.root, dirname), filename)
        self.assertEqual(res, expected)

    def test_split_parent_with_dir(self):
        parent = "test"
        dirname = "dirtest"
        res = Path.split_parent(self.create_path(self.root,parent,dirname))
        expected = (self.create_path(self.root,parent), dirname)
        self.assertEqual(res, expected)

    def test_split_parent_with_relative_path(self):
        parent = "test"
        dirname = "dirtest"
        res = Path.split_parent(self.create_path(parent,dirname))
        expected = (parent, dirname)
        self.assertEqual(res, expected)

    def test_split_parent_with_path_containing_spaces(self):
        parent = "Dir with spaces"
        dirname= "NormalDir"
        res = Path.split_parent(self.create_path(self.root, parent, dirname))
        expected = (self.create_path(self.root,parent), dirname)
        self.assertEqual(res, expected)

    #======================= TESTS ON Directory =======================#

    def test_read_file_can_read_a_file(self):
        root = self.create_basic_filesystem()

        dir1 = Directory(root)("Dir1")
        self.assertIsNotNone(dir1.read_file("File1"))

    def test_read_file_fails_silently_by_default(self):
        root = self.create_basic_filesystem()

        dir1 = Directory(root)("Dir1")
        self.assertIsNone(dir1.read_file("FileXXXX"))

    def test_read_file_fails_with_right_exception_if_indicated(self):
        root = self.create_basic_filesystem()

        dir1 = Directory(root)("Dir1")
        with self.assertRaises(FileNotFoundError):
            dir1.read_file("FileXXXX", raiseException=True)

    def test_create_directory_if_not_exists_returns_True_if_directory_already_exists(self):
        root = self.create_basic_filesystem()
        self.assertTrue(os.path.exists("Dir1") and os.path.isdir("Dir1"))
        self.assertTrue(root.create_directory_if_not_exists("Dir1"))

    def test_create_directory_if_not_exists_returns_False_if_file_exists_with_dirname(self):
        root = self.create_basic_filesystem()
        self.assertFalse(root.create_directory_if_not_exists("FileInRoot"))

    def test_create_directory_if_not_exists_with_no_confirm_creates_dir(self):
        root = self.create_basic_filesystem()
        dirname = "NewDir"
        self.assertFalse(os.path.exists(dirname))
        self.assertTrue(root.create_directory_if_not_exists(dirname, directory_creation_confirm=False))
        self.assertTrue(os.path.exists(dirname))

    def test_create_directory_if_not_exists_with_confirm_creates_dir(self):
        root = self.create_basic_filesystem()
        dirname = "NewDir"

        self.assertFalse(os.path.exists(dirname))
        self.assertTrue(root.create_directory_if_not_exists(dirname))
        self.assertTrue(os.path.exists(dirname))

    def test_create_directory_if_not_exists_does_not_create_dir_if_user_doesnt_want_to(self):
        root = self.create_basic_filesystem()
        dirname = "NewDir"

        with components.get("Console") as c:
            c.confirm = lambda question, default=None: False

            self.assertFalse(os.path.exists(dirname))
            self.assertFalse(root.create_directory_if_not_exists(dirname))
            self.assertFalse(os.path.exists(dirname))
