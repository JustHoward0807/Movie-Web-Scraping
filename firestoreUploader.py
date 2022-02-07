import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('firebase-admin.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def deleteDoc():
    i = 0
    sum = 0
    movies = "movies"
    for movie in movies:
        get_all_doc = db.collection(movie).stream()
        for doc in get_all_doc:
            if (i < len(doc.id)):
                db.collection(movie).document(doc.id).delete()
                print(f'id: ${doc.id} has been deleted')
                sum += 1
    print(f'total deleted: {sum}')
    
    
def uploadFirestore(movie_id,
                movie_cn_name,
                 movie_en_name,
                movie_rating,
                imdb_rating,
                movie_duration,
                 movie_category_list,
                release_movie_time,
                 trailer_video_URL,
                 movie_poster,
                movie_photos_list,
                 movie_introduction,
               actor_list):
    
    # Document with auto generated id
    doc_ref = db.collection(movie_id).document()


    # Give the values
    doc_ref.set({
       "movie_id": movie_id,
                "movie_cn_name": movie_cn_name,
                "movie_en_name": movie_en_name,
                "movie_rating": movie_rating,
                "movie_imdb_rating": imdb_rating,
                "movie_duration": movie_duration,
                "movie_category": movie_category_list,
                "release_movie_time": release_movie_time,
                "movie_trailer": trailer_video_URL,
                "movie_poster": movie_poster,
                "movie_photos": movie_photos_list,
                "movie_introduction": movie_introduction,
                "actors": actor_list,
    })
    