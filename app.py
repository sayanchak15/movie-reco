
from flask import Flask, render_template, request, session, make_response, Response, url_for, redirect
import pickle
import numpy as np
import pandas as pd
import heapq

app = Flask(__name__)



@app.route("/")
def home():
   movies = pd.read_pickle('movies')
   images_2 = []
   movie_names = []
   for i in range(80):
      images_2.append(str(i)+".jpg")
      movie_names.append(movies.Title[i])
   return render_template("index.html", images = images_2, movie_names = movie_names)


# @app.route('/images',  methods=['POST'])
# def images_page():
#    # image1 = "1.jpg"
#    # image2 = "2.jpg"
#    images = []
#    for i in range(13):
#       images.append(str(i)+".jpg")
#    print(images)
#    return render_template("images.html", images = images)

@app.route('/system1', methods = ['GET', 'POST'])
def system1():

   input_genre = request.form['genre']
   movies = pd.read_pickle('movies')
   # users = pd.read_pickle('users')
   ratings = pd.read_pickle('ratings')

   # input_genre = 'Romance'
   min_views = 500
   min_rating = 3
   mid = np.array(movies.MovieID[movies["Genres"].str.contains(input_genre)])
   g_all_movie = ratings.loc[ratings['MovieID'].isin(mid)]
   gg = g_all_movie.groupby('MovieID')
   print("here2 ")
   ## get movies over 1000 views
   best_count = (gg["Rating"].count().sort_values() > min_views)
   ## get average rating of them
   final_list = np.array(best_count.index[best_count == True])
   gg1 = ratings.loc[ratings.MovieID.isin(final_list)].groupby('MovieID')
   # best_count1 = (gg1['Rating'].mean().sort_values() > 4.0)
   df2 = pd.DataFrame(gg1['Rating'].mean().sort_values())
   df3 = pd.merge(movies, df2, on='MovieID')
   pop_movie_df = df3.loc[df3.Rating > min_rating]
   x = pop_movie_df.sort_values(by="Rating", ascending=False)["MovieID"][:10]
   images = []
   movie_names = []
   for i in list(x):
      images.append(str(i)+".jpg")
      movie_names.append(list(movies[movies.MovieID == i]["Title"]).pop())
   print(images,movie_names)
   return render_template("system1.html", images = images, movie_names = movie_names)


@app.route('/system2', methods = ['GET', 'POST'])
def system2():
   movies = pd.read_pickle('movies')
   inp = request.form.getlist('rating')
   # im = request.form.getlist('mid')
   # mid = np.array([i[:-4] for i in im])
   # print("Rating", inp)
   # print("mid", mid)
   similarity_matrix = np.load('sim_matrix.npy')
   input_ratings = np.array(inp)
   input_ratings = input_ratings.astype(np.float)
   # mid = mid.astype(np.float)
   N = 2
   
   rated_movies = movies.iloc[np.nonzero(input_ratings)]["MovieID"].values
   final_list = []
   for _, reco_movie, title,_,_ in movies.head(1000).itertuples():
      score = 0
      Dr = 0
      candi = []
      if reco_movie in rated_movies:
         continue
      else: 
         for index, rating in enumerate(input_ratings):
               if rating >= 0.000001:       
                  rated_movie = movies.iloc[index]["MovieID"]
                  candi.append((reco_movie, similarity_matrix[rated_movie][reco_movie], rating, rated_movie ))
                  n_candi = heapq.nlargest(N, candi, key=lambda t: t[1])
               
               else: continue
      print(n_candi)
      for _,i, j,_ in n_candi:
         Dr += i
         score += i*j
   #     print(score/Dr, reco_movie, title)
      final_list.append((score/Dr, reco_movie, title))

   system2_list = heapq.nlargest(10, final_list, key=lambda t: t[0])
   images = []
   movie_names = []
   for _,movieID,title in system2_list:
      images.append(str(movieID)+".jpg")
      movie_names.append(title)
   print(images,movie_names)
   
   return render_template("system2.html", images = images, movie_names = movie_names)




if __name__ == '__main__':
    app.run(debug=True)