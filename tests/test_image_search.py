# Standard Modules
from pathlib import Path
from PIL import Image

# Internal Packages
from src.utils.state import model
from src.utils.constants import web_directory
from src.search_type import image_search
from src.utils.helpers import resolve_absolute_path
from src.utils.rawconfig import ContentConfig, SearchConfig


# Test
# ----------------------------------------------------------------------------------------------------
def test_image_search_setup(content_config: ContentConfig, search_config: SearchConfig):
    # Act
    # Regenerate image search embeddings during image setup
    image_search_model = image_search.setup(content_config.image, search_config.image, regenerate=True)

    # Assert
    assert len(image_search_model.image_names) == 3
    assert len(image_search_model.image_embeddings) == 3


def test_image_metadata(content_config: ContentConfig):
    "Verify XMP Description and Subjects Extracted from Image"
    # Arrange
    expected_metadata_image_name_pairs = [
        (["Billi Ka Bacha.", "Cat", "Grass"], "kitten_park.jpg"),
        (["Pasture.", "Horse", "Dog"], "horse_dog.jpg"),
        (["Guinea Pig Eating Celery.", "Rodent", "Whiskers"], "guineapig_grass.jpg")]

    test_image_paths = [
        Path(content_config.image.input_directories[0] / image_name[1])
        for image_name in expected_metadata_image_name_pairs
    ]

    for expected_metadata, test_image_path in zip(expected_metadata_image_name_pairs, test_image_paths):
        # Act
        actual_metadata = image_search.extract_metadata(test_image_path)

        # Assert
        for expected_snippet in expected_metadata[0]:
            assert expected_snippet in actual_metadata


# ----------------------------------------------------------------------------------------------------
def test_image_search(content_config: ContentConfig, search_config: SearchConfig):
    # Arrange
    output_directory = resolve_absolute_path(web_directory)
    model.image_search = image_search.setup(content_config.image, search_config.image, regenerate=False)
    query_expected_image_pairs = [("kitten", "kitten_park.jpg"),
                                  ("horse and dog in a farm", "horse_dog.jpg"),
                                  ("A guinea pig eating grass", "guineapig_grass.jpg")]

    # Act
    for query, expected_image_name in query_expected_image_pairs:
        hits = image_search.query(
            query,
            count = 1,
            model = model.image_search)

        results = image_search.collate_results(
            hits,
            model.image_search.image_names,
            output_directory=output_directory,
            image_files_url='/static/images',
            count=1)

        actual_image_path = output_directory.joinpath(Path(results[0].entry).name)
        actual_image = Image.open(actual_image_path)
        expected_image = Image.open(content_config.image.input_directories[0].joinpath(expected_image_name))

        # Assert
        assert expected_image == actual_image

    # Cleanup
    # Delete the image files copied to results directory
    actual_image_path.unlink()
