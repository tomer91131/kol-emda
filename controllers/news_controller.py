from models.news_model import NewsModel

class NewsController:
    def __init__(self):
        self.model = NewsModel()

    def get_game_triplets(self):
        """Get recent triplets for the news guessing game"""
        return self.model.get_recent_triplets()

    def get_news_comparison(self, limit=10):
        """Get triplets for the news comparison display"""
        return self.model.get_triplets_for_display(limit)

    def check_game_answer(self, triplet_id, selected_source, actual_source):
        """Check if the user's guess is correct"""
        return selected_source == actual_source 