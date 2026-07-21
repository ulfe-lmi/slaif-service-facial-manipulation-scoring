from types import SimpleNamespace

import cv2
import numpy as np

from slaif_fms.preprocessing import AuthorCropper, decode_image, landmark_crop_box


def test_landmark_crop_box_matches_author_margin() -> None:
    landmarks = np.asarray([[10, 20], [50, 100]])
    assert landmark_crop_box(landmarks, frame_width=100, frame_height=120) == (
        5,
        10,
        55,
        110,
    )


def test_landmark_crop_box_clips_to_frame() -> None:
    landmarks = np.asarray([[1, 2], [99, 98]])
    assert landmark_crop_box(landmarks, frame_width=100, frame_height=100) == (
        0,
        0,
        100,
        100,
    )


class FakeShape:
    def __init__(self, points: list[tuple[int, int]]):
        self.points = points
        self.num_parts = len(points)

    def part(self, index: int):
        x, y = self.points[index]
        return SimpleNamespace(x=x, y=y)


def test_cropper_selects_largest_landmark_area() -> None:
    rectangles = ["small", "large"]
    shapes = {
        "small": FakeShape([(20, 20), (30, 30)]),
        "large": FakeShape([(10, 10), (70, 90)]),
    }
    cropper = AuthorCropper(
        predictor_path=None,  # type: ignore[arg-type]
        detector=lambda _image, _upsample: rectangles,
        predictor=lambda _image, rectangle: shapes[rectangle],
    )
    outcome = cropper.crop(np.zeros((100, 100, 3), dtype=np.uint8))
    assert outcome.detected_faces == 2
    assert outcome.box_xyxy == (2, 0, 78, 100)
    assert outcome.image_rgb is not None
    assert outcome.image_rgb.shape == (100, 76, 3)


def test_decode_image_uses_opencv_rgb() -> None:
    bgr = np.zeros((4, 5, 3), dtype=np.uint8)
    bgr[:, :] = (10, 20, 30)
    ok, encoded = cv2.imencode(".png", bgr)
    assert ok
    rgb = decode_image(encoded.tobytes(), max_pixels=100)
    assert rgb.shape == (4, 5, 3)
    assert rgb[0, 0].tolist() == [30, 20, 10]
