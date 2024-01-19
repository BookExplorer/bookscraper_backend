import pytest
from utils import scrape_gr_author


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://www.goodreads.com/author/show/13199.Alain_de_Botton",
            "Zurich, Switzerland",
        ),
        ("https://www.goodreads.com/author/show/6062267.Yaniv_Shimony", None),
    ],
)
def test_scrape_gr_author(url: str, expected: None | str):
    assert scrape_gr_author(url) == expected
