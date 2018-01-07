class User:

    def __init__(self, state, tracker):
        self.state = state
        self.indexes = {tracker : {}}
        self.pages = {tracker : {}}
        self.movies = None
        self.reviews = None
        self.review_indexes = {}
        self.page = 1
        self.tracker = tracker
        self.genre = None
        self.category = None
        self.searching_movies = True
        self.imdb_id = None
        self.current_title = None
        self.reviews_provider = None
        self.review_pages = {}
        self.reviews_group = None
        self.wiki_content = None
        self.wiki_keyboard_markup = None
