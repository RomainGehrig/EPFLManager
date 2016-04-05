import os
import random
import logging
import unittest
import itertools

import pyfakefs.fake_filesystem_unittest as fakefs

from epflmanager.coursehandler import CourseHandler, SemesterNotFound, CourseNotFound
from epflmanager.io.fileorganizer import Directory
from epflmanager.io.specialdirs import SemesterDir, CourseDir, CourseNotLinkedWithMoodle
import epflmanager.components as components

from components import initialize_components

logger = logging.getLogger(__name__)

class CourseHandlerTest(fakefs.TestCase):

    def setUp(self):
        initialize_components()
        self.ch = components.get("CourseHandler")
        self.setUpPyfakefs()

    def tearDown(self):
        pass

    @property
    def root(self):
        # TODO Windows compatibility
        return "/"

    def random_semesters(self, n):
        """ Return a list of n randomly chosen semesters """
        assert(0 <= n <= len(self.all_semesters))
        import random

        selected = []

        remaining = set(self.all_semesters)
        for i in range(n):
            sem = random.choice(list(remaining))
            selected.append(sem)
            remaining.remove(sem)

        sorted_semesters = { s: i for i,s in enumerate(self.all_semesters) }
        selected.sort(key=lambda s: sorted_semesters[s])
        return selected

    @property
    def all_semesters(self):
        return ["BA1","BA2","BA3","BA4","BA5","BA6",
                "MA1","MA2","MA3","MA4"]

    def courses_for_semester(self, semester, n=2):
        return [ "%sCourse%d" % (semester, i) for i in range(1, n+1) ]

    def create_course_tree(self, course_name, semester_name, with_moodle=True, with_site_url=True):
        path = os.getcwd()
        os.chdir(semester_name)

        os.mkdir(course_name)
        os.chdir(course_name)

        if with_site_url:
            self.fs.CreateFile("site.url", contents="http://google.com/?course_name=%s Google\n http://example.com example" % course_name)

        if with_moodle:
            self.fs.CreateFile(".moodle.%s" % course_name, contents="[course]\ncourse_name = %s\nmoodle_id = %d" % (course_name, 100))

        # create some file/dir
        self.fs.CreateFile("File%s" % course_name)
        os.mkdir("Dir%s" % course_name)

        os.chdir(path)

    def create_classic_epfl_hierarchy(self, semesters=None, course_gen=None):
        """ Create the following file tree:

            EPFL
             ├─ BA3
             │   ├─ schedule.png
             │   ├─ BA3Course1
             │   │   ├─ site.url
             │   │   ├─ .moodle.BA3Course1
             │   │   ├─ File1
             │   │   └─ Dir1
             │   └─ BA3Course2
             │       ├─ site.url
             │       ├─ .moodle.BA3Course2
             │       ├─ File2
             │       └─ Dir2
             ├─ BA4
             │   ├─ schedule.png
             │   ├─ BA4Course1
             │   │   ├─ site.url
             │   │   ├─ .moodle.BA4Course1
             │   │   ├─ File1
             │   │   └─ Dir1
             │   └─ BA4Course2
             │       ├─ site.url
             │       ├─ .moodle.BA4Course2
             │       ├─ File2
             │       └─ Dir2
             └─ MA1
                 ├─ schedule.png
                 ├─ MA1Course1
                 │   ├─ site.url
                 │   ├─ .moodle.MA1Course1
                 │   ├─ File1
                 │   └─ Dir1
                 └─ MA1Course2
                     ├─ site.url
                     ├─ .moodle.MA1Course2
                     ├─ File2
                     └─ Dir2

        Return the root as a Directory for convenience
        """
        if course_gen is None:
            course_gen = itertools.repeat(3)
        if semesters is None:
            # some bachelor and some master dirs
            semesters = self.random_semesters(3)

        logger.info("Creating semesters %s" % ','.join(semesters))

        for semester in semesters:
            os.mkdir(semester)
            os.chdir(semester)
            self.fs.CreateFile("schedule.png")
            os.chdir("..")

            for course_name in self.courses_for_semester(semester,next(course_gen)):
                self.create_course_tree(course_name,semester)

        return Directory(self.root)(".")

    def test_semesters_lists_all_existing_semesters(self):
        rsemesters = self.random_semesters(4)
        self.create_classic_epfl_hierarchy(semesters=rsemesters)

        semesters = {SemesterDir(self.root)(s) for s in rsemesters }
        with self.ch:
            found_semesters = self.ch.semesters()

        self.assertSetEqual(set(found_semesters), semesters)

    def test_get_course_with_no_semester_given_use_latest_semester(self):
        root = self.create_classic_epfl_hierarchy()
        with self.ch:
            sem = self.ch.latest_semester()
            courses = self.ch.courses(sem)
            for c in courses:
                self.assertEqual(self.ch.get_course(c.name), c)

    def test_courses_with_no_semester_given_use_latest_semester(self):
        root = self.create_classic_epfl_hierarchy()
        with self.ch:
            sem = self.ch.latest_semester()
            courses = self.ch.courses()
            expected_courses = self.ch.courses(sem)
            self.assertSetEqual(set(courses), set(expected_courses))

    def test_get_course_throws_exception_when_no_course_is_found(self):
        root = self.create_classic_epfl_hierarchy()
        with self.ch:
            with self.assertRaises(CourseNotFound):
                self.ch.get_course("NONEXISTING")

    def test_get_semesters_fails_with_exception_on_inexisting_semester(self):
        with self.ch:
            with self.assertRaises(SemesterNotFound):
                self.ch.get_semester("NONEXISTING")

    def test_latest_semester_raises_exception_when_no_semester_exists(self):
        with self.ch:
            with self.assertRaises(SemesterNotFound):
                self.ch.latest_semester()

    def test_semesters_does_not_list_inexisting_semesters(self):
        rsemesters = self.random_semesters(4)
        self.create_classic_epfl_hierarchy(semesters=rsemesters)
        non_existing_semesters = set(self.all_semesters).difference(set(rsemesters))
        semesters = {SemesterDir(self.root)(s) for s in non_existing_semesters }

        with self.ch:
            # The intersection of the existing and non existing semesters must be the empty set
            self.assertSetEqual(set(), set(self.ch.semesters()).intersection(semesters))

    def test_semesters_return_empty_list_if_nothing_exists(self):
        with self.ch:
            self.assertListEqual(self.ch.semesters(),[])

    def test_is_semester_dir_returns_True_for_all_valid_semesters(self):
        for s in self.all_semesters:
            self.assertTrue(self.ch.is_semester_dir(s))

    def test_sorted_semesters_returns_the_correct_order(self):
        rsemesters = self.random_semesters(4)
        self.create_classic_epfl_hierarchy(semesters=rsemesters)

        with self.ch:
            sorted_semesters = [s.name for s in self.ch.sorted_semesters()]

        self.assertListEqual(rsemesters, sorted_semesters)

    def test_latest_semester_is_the_latest(self):
        rsemesters = self.random_semesters(4)
        self.create_classic_epfl_hierarchy(semesters=rsemesters)

        with self.ch:
            latest_semester = self.ch.latest_semester()

        self.assertEqual(rsemesters[-1], latest_semester.name)

    def test_courses_returns_every_courses(self):
        rsemesters = self.random_semesters(4)
        cycles = [1,4,2]
        self.create_classic_epfl_hierarchy(semesters=rsemesters,course_gen=itertools.cycle(cycles))

        with self.ch:
            ns = itertools.cycle(cycles)
            for (s,sname) in zip(self.ch.sorted_semesters(), rsemesters):
                courses = self.ch.courses(semester=s)
                self.assertSetEqual(set(c.name for c in courses), set(self.courses_for_semester(sname,next(ns))))

    def test_get_course_retrieve_existing_course(self):
        rsemesters = self.random_semesters(4)
        cycles = [1,4,2]
        self.create_classic_epfl_hierarchy(semesters=rsemesters,course_gen=itertools.cycle(cycles))

        with self.ch:
            ns = itertools.cycle(cycles)
            for s in self.ch.sorted_semesters():
                for c in self.courses_for_semester(s.name, next(ns)):
                    self.assertEqual(c, self.ch.get_course(c,s).name)

    def create_course_and_assert_existence(self, course_name, semester, expected_result=True):
        with self.ch:
            semester = self.ch.get_semester(semester)
            creation_success = self.ch.add_course(course_name, semester=semester)
            self.assertTrue(creation_success == expected_result)
            semester_path = semester.fullpath()
            self.assertTrue(os.path.isdir(os.path.join(semester_path, course_name)) == creation_success)

    def test_add_course_with_no_semester_given_should_create_in_latest_semester(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        course_name = "NEWCOURSE1"
        with self.ch:
            semester = self.ch.latest_semester()
            creation_success = self.ch.add_course(course_name)
            self.assertTrue(creation_success)
            self.assertIsNotNone(self.ch.get_course(course_name, semester))

    def test_add_course_fails_if_file_with_same_name_exists(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        self.create_course_and_assert_existence("schedule.png", random.choice(self.all_semesters), False)

    def test_add_course_create_course_in_right_semester(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        self.create_course_and_assert_existence("NewCourse1",random.choice(self.all_semesters))

    def test_add_course_returns_True_when_course_already_exists(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        semester = random.choice(self.all_semesters)
        self.create_course_and_assert_existence("NewCourse1",semester)
        self.create_course_and_assert_existence("NewCourse1",semester)

    def test_add_course_returns_False_a_file_has_the_same_name(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        semester = random.choice(self.all_semesters)
        self.create_course_and_assert_existence("schedule.png",semester,False)

    def test_moodle_id_for_course_acts_according_to_file_existence(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        semester_name = random.choice(self.all_semesters)
        course_name1 = "NewCourse1"
        course_name2 = "NewCourse2"
        self.create_course_tree(course_name1, semester_name, with_moodle=True)
        self.create_course_tree(course_name2, semester_name, with_moodle=False)

        with self.ch:
            semester = self.ch.get_semester(semester_name)
            course1 = self.ch.get_course(course_name1, semester)
            self.assertIsNotNone(self.ch.moodle_id_for_course(course1))
            course2 = self.ch.get_course(course_name2, semester)
            with self.assertRaises(CourseNotLinkedWithMoodle):
                self.ch.moodle_id_for_course(course2)

    def test_link_course_with_moodle(self):
        root = self.create_classic_epfl_hierarchy(semesters=self.all_semesters)
        semester_name = random.choice(self.all_semesters)
        course_name1 = "NewCourse1"
        course_name2 = "NewCourse2"
        self.create_course_tree(course_name1, semester_name, with_moodle=True)
        self.create_course_tree(course_name2, semester_name, with_moodle=False)

        with self.ch:
            semester = self.ch.get_semester(semester_name)
            course1 = self.ch.get_course(course_name1, semester)
            oldMoodleID = self.ch.moodle_id_for_course(course1)
            self.assertIsNotNone(oldMoodleID)
            self.ch.link_course_with_moodle(course1, oldMoodleID + "1")
            newMoodleID = self.ch.moodle_id_for_course(course1)
            self.assertNotEqual(oldMoodleID, newMoodleID)

            course2 = self.ch.get_course(course_name2, semester)
            with self.assertRaises(CourseNotLinkedWithMoodle):
                self.ch.moodle_id_for_course(course2)

            newMoodleID2 = 1000
            self.ch.link_course_with_moodle(course2, newMoodleID2)
            self.assertEquals(self.ch.moodle_id_for_course(course2), str(newMoodleID2))
