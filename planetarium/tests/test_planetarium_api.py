import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import (
    AstronomyShow, ShowSession, PlanetariumDome, ShowTheme,
)
from planetarium.serializers import (
    AstronomyShowListSerializer, AstronomyShowDetailSerializer,
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def detail_url(astronomy_show_id: int):
    return reverse(
        "planetarium:astronomyshow-detail", args=[astronomy_show_id]
    )


def sample_astronomy_show(**params):
    defaults = {
        "title": "Sample show",
        "description": "Sample description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_show_theme(**params):
    defaults = {
        "name": "Moon",
    }
    defaults.update(params)

    return ShowTheme.objects.create(**defaults)


def sample_show_session(**params):
    planetarium_dome = PlanetariumDome.objects.create(
        name="Blue", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "astronomy_show": None,
        "planetarium_dome": planetarium_dome,
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


def image_upload_url(astronomy_show_id):
    """Return URL for recipe image upload"""
    return reverse(
        "planetarium:astronomyshow-upload-image", args=[astronomy_show_id]
    )


class AstronomyShowImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.astronomy_show = sample_astronomy_show()
        self.genre = sample_show_theme()
        self.show_session = sample_show_session(
            astronomy_show=self.astronomy_show
        )

    def tearDown(self):
        self.astronomy_show.image.delete()

    def test_upload_image_to_astronomy_show(self):
        """Test uploading an image to astronomy show"""
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.astronomy_show.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.astronomy_show.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.astronomy_show.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_astronomy_show_list(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "show_themes": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(title="Title")
        self.assertFalse(astronomy_show.image)

    def test_image_url_is_shown_on_astronomy_show_detail(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.astronomy_show.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_astronomy_show_list(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_show_session_detail(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(SHOW_SESSION_URL)

        self.assertIn("astronomy_show_image", res.data[0].keys())


class UnauthenticatedPlanetariumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlanetariumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="T1e2S3t4"
        )
        self.client.force_authenticate(self.user)

    def test_list_astronomy_show(self):
        sample_astronomy_show()

        result = self.client.get(ASTRONOMY_SHOW_URL)
        astronomy_shows = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_astronomy_show_filter_by_show_themes(self):
        show_theme1 = sample_show_theme(name="test_theme1")
        show_theme2 = sample_show_theme(name="test_theme2")

        astronomy_show1 = sample_astronomy_show(title="test_title1")
        astronomy_show2 = sample_astronomy_show(title="test_title2")
        astronomy_show_without_themes = sample_astronomy_show(
            title="test_title_without_theme"
        )

        astronomy_show1.show_themes.add(show_theme1)
        astronomy_show2.show_themes.add(show_theme2)

        result = self.client.get(
            ASTRONOMY_SHOW_URL,
            {"show_themes": f"{show_theme1.id}, {show_theme2.id}"}
        )

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)
        serializer3 = AstronomyShowListSerializer(
            astronomy_show_without_themes
        )

        self.assertIn(serializer1.data, result.data)
        self.assertIn(serializer2.data, result.data)
        self.assertNotIn(serializer3.data, result.data)

    def test_astronomy_show_filter_by_title(self):
        astronomy_show1 = sample_astronomy_show(title="test_title1")
        astronomy_show2 = sample_astronomy_show(title="test_title2")

        result = self.client.get(
            ASTRONOMY_SHOW_URL,
            {"titles": f"{astronomy_show1.id}, {astronomy_show2.id}"}
        )

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)

        self.assertIn(serializer1.data, result.data)
        self.assertIn(serializer2.data, result.data)

    def test_retrieve_astronomy_show_detail(self):
        astronomy_show = sample_astronomy_show(title="test_title")
        show_theme = sample_show_theme(name="test_name")

        astronomy_show.show_themes.add(show_theme)

        url = detail_url(astronomy_show.id)
        result = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(astronomy_show)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "astronomy_show",
            "description": "description",
        }

        result = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlanetariumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="admintest@user.com",
            password="A1d2M3i4N5",
            is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_create_astronomy_show(self):
        payload = {
            "title": "astronomy_show",
            "description": "description",
        }

        result = self.client.post(ASTRONOMY_SHOW_URL, payload)
        astronomy_show = AstronomyShow.objects.get(id=result.data["id"])

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(astronomy_show, key))

    def test_create_astronomy_show_with_unnecessary_fields(self):
        show_theme = sample_show_theme(name="show_theme")
        payload = {
            "title": "astronomy_show",
            "description": "description",
            "show_themes": [show_theme.id],
        }

        result = self.client.post(ASTRONOMY_SHOW_URL, payload)
        astronomy_show = AstronomyShow.objects.get(id=result.data["id"])
        show_themes = astronomy_show.show_themes.all()

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertIn(show_theme, show_themes)

    def test_delete_astronomy_show_not_allowed(self):
        astronomy_show = sample_astronomy_show()
        url = detail_url(astronomy_show.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
