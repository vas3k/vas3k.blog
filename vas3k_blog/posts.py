from dataclasses import dataclass

DEFAULT_LIST_ITEMS_PER_PAGE = 30


@dataclass
class PostTypeConfig:
    name: str = "Посты"
    list_items_per_page: int = DEFAULT_LIST_ITEMS_PER_PAGE
    card_template: str = "posts/cards/horizontal.html",
    list_template: str = "posts/lists/layout.html",
    show_template: str = "posts/full/layout.html"


POST_TYPES: dict[str, PostTypeConfig] = {
    "blog": PostTypeConfig(
        name="Блог",
        list_items_per_page=30,
        card_template="posts/cards/horizontal.html",
        list_template="posts/lists/blog.html",
        show_template="posts/full/blog.html",
    ),
    "notes": PostTypeConfig(
        name="Заметки",
        list_items_per_page=50,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/notes.html",
        show_template="posts/full/notes.html",
    ),
    "world": PostTypeConfig(
        name="Путешествия",
        list_items_per_page=30,
        card_template="posts/cards/horizontal.html",
        list_template="posts/lists/blog.html",
        show_template="posts/full/blog.html",
    ),
    "challenge": PostTypeConfig(
        name="Поисковые челленджи",
        list_items_per_page=30,
        card_template="posts/cards/horizontal.html",
        list_template="posts/lists/blog.html",
        show_template="posts/full/legacy/challenge.html",
    ),
    "gallery": PostTypeConfig(
        name="Галлерея",
        list_items_per_page=30,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/blog.html",
        show_template="posts/full/legacy/gallery.html",
    ),
    "inside": PostTypeConfig(
        name="Вастрик.Инсайд",
        list_items_per_page=30,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/notes.html",
        show_template="posts/full/notes.html",
    ),
    "365": PostTypeConfig(
        name="Заметки",
        list_items_per_page=50,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/notes.html",
        show_template="posts/full/notes.html",
    ),
}


def post_config_by_type(post_type):
    if post_type in POST_TYPES:
        return POST_TYPES[post_type]
    else:
        return PostTypeConfig()


INDEX_PAGE_BEST_POSTS = [
    "quantum_computing",
    "computational_photography",
    "machine_learning",
    "team",
    "touchbar",
    "blockchain",
]
