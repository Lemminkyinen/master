import unittest

import models as m


class TestRoverModel(unittest.TestCase):
    def test_cameras_perseverance(self):
        rover = m.Rover("perseverance")
        self.assertEqual(
            rover.get_cameras(),
            [
                "edl_rucam",
                "edl_rdcam",
                "edl_ddcam",
                "edl_pucam1",
                "edl_pucam2",
                "navcam_left",
                "navcam_right",
                "mcz_right",
                "mcz_left",
                "front_hazcam_left_a",
                "front_hazcam_right_a",
                "rear_hazcam_left",
                "rear_hazcam_right",
                "skycam",
                "sherloc_watson",
            ],
        )

    def test_cameras_curiosity(self):
        rover = m.Rover("curiosity")
        self.assertEqual(
            rover.get_cameras(),
            ["fhaz", "rhaz", "navcam", "mast", "chemcam", "mahli", "mardi", "navcam"],
        )


if __name__ == "__main__":
    unittest.main()
