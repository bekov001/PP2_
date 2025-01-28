movies = [
    {"name": "Usual Suspects", "imdb": 7.0, "category": "Thriller"},
    {"name": "Hitman", "imdb": 6.3, "category": "Action"},
    {"name": "Dark Knight", "imdb": 9.0, "category": "Adventure"},
    {"name": "The Help", "imdb": 8.0, "category": "Drama"},
    {"name": "The Choice", "imdb": 6.2, "category": "Romance"},
    {"name": "Colonia", "imdb": 7.4, "category": "Romance"},
    {"name": "Love", "imdb": 6.0, "category": "Romance"},
    {"name": "Bride Wars", "imdb": 5.4, "category": "Romance"},
    {"name": "AlphaJet", "imdb": 3.2, "category": "War"},
    {"name": "Ringing Crime", "imdb": 4.0, "category": "Crime"},
    {"name": "Joking muck", "imdb": 7.2, "category": "Comedy"},
    {"name": "What is the name", "imdb": 9.2, "category": "Suspense"},
    {"name": "Detective", "imdb": 7.0, "category": "Suspense"},
    {"name": "Exam", "imdb": 4.2, "category": "Thriller"},
    {"name": "We Two", "imdb": 7.2, "category": "Romance"}
]


def is_above_5_5(movie):
    return movie["imdb"] > 5.5


def movies_above_5_5(movies_list):
    return [movie for movie in movies_list if movie["imdb"] > 5.5]


def movies_by_category(movies_list, category):
    return [movie for movie in movies_list if movie["category"] == category]


def average_imdb_score(movies_list):
    if not movies_list:
        return 0
    total_score = sum(movie["imdb"] for movie in movies_list)
    return total_score / len(movies_list)


def average_imdb_score_by_category(movies_list, category):
    category_movies = movies_by_category(movies_list, category)
    return average_imdb_score(category_movies)





print(is_above_5_5(movies[0]))  
print(movies_above_5_5(movies))  
print(movies_by_category(movies, "Romance"))  
print(average_imdb_score(movies))  
print(average_imdb_score_by_category(movies, "Romance"))  