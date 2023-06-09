import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
# from fuzzywuzzy import fuzz, process
import os


class CollaborativeRecommender:

    def __init__(self, ratings: pd.DataFrame, userid, titleid, ratingid, highestRating: int) -> None:
        self.putDataset(ratings, userid, titleid, ratingid, highestRating)
        self.correlationMatrix = pd.DataFrame()

    def saveCorrelationMatrix(self, filename='default-dataset'):
        self.correlationMatrix.to_pickle(filename)

    def loadCorrelationMatrix(self, filename='default-dataset'):
        if (os.path.isfile(filename)):
            self.correlationMatrix = pd.read_pickle(filename)
        else:
            pass

    def putDataset(self, ratings: pd.DataFrame, userid, titleid, ratingid, highestRating: int):
        self.ratings = ratings
        self.userid = userid
        self.titleid = titleid
        self.ratingid = ratingid
        self.highestRating = highestRating

    def putPrefs(self, listOfMovieRatings):
        self.moviePrefs = listOfMovieRatings

    def getRatingsByUserId(self):
        # debugging
        self.ratings = self.ratings.groupby(
            self.userid).filter(lambda x: len(x) >= 500)
        self.ratingsByUserId = self.ratings.pivot_table(
            index=self.userid, columns=self.titleid, values=self.ratingid).dropna(thresh=10, axis='columns').fillna(0, axis=1)
        return self.ratingsByUserId

    def getCorrelationMatrix(self, ratingByUserId: pd.DataFrame):
        self.correlationMatrix = ratingByUserId.corr(method='pearson')
        return self.correlationMatrix

    def getSimilarToMovie(self, movie_name, rating):
        if self.correlationMatrix.empty:
            similar_ratings = self.getCorrelationMatrix(
                self.getRatingsByUserId()
            )[movie_name]*(rating-float(self.highestRating)/2)
        else:
            similar_ratings = self.correlationMatrix[movie_name]*(
                rating-float(self.highestRating)/2)
        similar_ratings = similar_ratings.sort_values(ascending=False)
        return similar_ratings

    def getSimilarToMovies(self):
        similar_movies = pd.DataFrame()
        similar_movies = pd.concat([self.getSimilarToMovie(
            movie, rating) for movie, rating in self.moviePrefs],  axis=1, ignore_index=True)
        similar_movies = similar_movies.sum(
            'columns').sort_values(ascending=False).head(20)
        return similar_movies

    def find_closest_matches(self, query):
        matches = []
        limit = 0
        print(self.getRatingsByUserId().columns)
        for moviez in self.getRatingsByUserId().columns.tolist():
            # print(query.lower(), moviez.lower())
            limit += 1
            if query.lower() in moviez.lower():
                matches.append(moviez)
            if limit > 3500:
                break
        return matches


def preprocessMovies():
    ratings = pd.read_csv('./CSV/movies-dataset/movie_ratings.csv')
    movies = pd.read_csv('./CSV/movies-dataset/movies.csv')
    ratings = pd.merge(movies, ratings) .drop(['genres', 'timestamp'], axis=1)
    return ratings


def preprocessBooks():
    ratings = pd.read_csv('./CSV/books-dataset/Ratings.csv')
    books = pd.read_csv('./CSV/books-dataset/Books.csv', low_memory=False)
    bookratin = pd.merge(books, ratings)[
        ['ISBN', 'Book-Title', 'User-ID', 'Book-Rating']]
    # print(bookratin[bookratin.duplicated(['ISBN', 'User-ID'])])
    return bookratin


def test():
    # # make sure to preprocess the movie and book datasets
    movieratings = preprocessMovies()
    bookratings = preprocessBooks()
    # print(bookratings.head(20))
    # print(movieratings.head(20))
    recommender = CollaborativeRecommender(
        movieratings, 'userId', 'title', 'rating', 5)
    bookrecom = CollaborativeRecommender(
        bookratings, 'User-ID', 'Book-Title', 'Book-Rating', 10)
    recommender.loadCorrelationMatrix()
    testprefs = [("Shawshank Redemption, The (1994)", 5), ("Alice in Wonderland (2010)",
                                                           1), ("Aliens (1986)", 1), ("2001: A Space Odyssey (1968)", 2)]
    bookprefs = [["Winter Solstice", 8]]
    bookrecom.putPrefs(bookprefs)
    recommender.putPrefs(testprefs)
    toitles = recommender.getRatingsByUserId().columns.tolist()
    # print(toitles)

    # print(bookrecom.getSimilarToMovies())
    # print(fuzz.ratio("shawshank redemption", "Red"))
    # save the trained correlation matrix
    recommender.saveCorrelationMatrix()
    print(bookrecom.find_closest_matches("pr"))
