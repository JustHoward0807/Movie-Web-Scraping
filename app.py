from os import error
import secrets
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime


page = 1
movie_photos_list = []
actor_dic = {}
actor_list = []
area_28_list = []
area_8_list = []
sumList = []
area = [8,28]
jsonFilePath = 'movie_output.json'
now = datetime.now()
current_time = now.strftime('%Y-%m-%d')


base_source = requests.get(
    f'https://movies.yahoo.com.tw/movie_intheaters.html').text
soup = BeautifulSoup(base_source, 'lxml')
number_box = soup.find('div', class_='page_numbox')
li_number = number_box.find_all('li')
for pages in li_number:
    source = requests.get(
        f'https://movies.yahoo.com.tw/movie_intheaters.html?page={page}').text
    soup = BeautifulSoup(source, 'lxml')
    page_number = pages.text.replace('‹', '').replace(
        '上一頁', '').replace('下一頁', '').replace('›', '')

    # According to the length of the page number to decide how many times the loop will execute
    # //TODO:Remove the list varaibles
    for pagenum in range(len(page_number)):
        page += 1
        movies = soup.find('ul', class_='release_list')
        moviesli = movies.find_all('li')
        for movie in moviesli:
            # ------------------------------------------------

            movie_id = movie.find('a', class_='gabtn')[
                'href'].split('/')[4].split('-')[-1]
            print(f'Movie id is: {movie_id.strip()}')

            # ------------------------------------------------
            movie_cn_name = movie.find('div', class_='release_movie_name').a.text.replace(
                ' ', '').replace('\n', '')
            print(f'Movie name is: {movie_cn_name.strip()}')
            # ------------------------------------------------

            movie_en_name = movie.find('div', class_='en').text.strip()
            # print(f'Movie english name is: {movie_en_name}')

            # ------------------------------------------------

            movie_poster = movie.find(
                'div', class_='release_foto').a.img['src']
            # print(f'Movie poster: {movie_poster.strip()}')

            # ------------------------------------------------

            release_movie_time = movie.find(
                'div', class_='release_movie_time').text.split('：')[-1].replace(' ', '')
            # print(f'Movie release time is: {release_movie_time.strip()}')

            # ------------------------------------------------

            movie_introduction = movie.find(
                'div', class_='release_text').span.text.replace(' ', '').replace('\n', '')
            # print(f'Movie introduction is: {movie_introduction.strip()}')

            # ------------------------------------------------
            # For Movie Detail Information (Actors, Ratings, photos, etc...)
            info_source = requests.get(
                f'https://movies.yahoo.com.tw/movieinfo_main/{movie_id}').text
            info_soup = BeautifulSoup(info_source, 'lxml')
            try:
                movie_rating = info_soup.find(
                    'div', class_='score_num count').text
                print(f'Movie rating is: {movie_rating.strip()}')
            except Exception as e:
                print(f'Something happened with movie rating: {e}')
                pass

            # ------------------------------------------------
            # Movie Photos
            photo_source = requests.get(
                f'https://movies.yahoo.com.tw/movieinfo_photos.html/id={movie_id}').text
            photo_soup = BeautifulSoup(photo_source, 'lxml')
            photo_pic = photo_soup.find('div', class_='pic')
            try:
                photo_table = photo_pic.find_all('div', class_='td')
            except Exception:
                photo_table = None
                pass
            if photo_table != None:
                for photo in photo_table:
                    movie_photos = photo.find('img')['src']
                    if movie_photos != None:
                        movie_photos_list.append(movie_photos)
            else:
                print('Movie photos are empty')
                movie_photo_list = []
            # print(movie_photos_list)

            # ------------------------------------------------
            # Movie Actors Pics and Names
            actor_main = info_soup.find('div', class_='l_box have_arbox _c')
            actor_ul = actor_main.find(
                'ul', class_='trailer_list alist starlist')

            try:
                actor_name = actor_ul.find_all('div', class_='actor_inner')
                actor_img = actor_ul.find_all('div', class_='fotoinner')

                for name, img in zip(actor_name, actor_img):
                    actor_names = name.find('h2').text.split(" ")[0]
                    actor_photos = img.find('img')['src']
                    if (actor_photos == '/build/images/noavatar.jpg'):
                        actor_photos = ""

                    if actor_names != '' or None:
                        actor_en1_name = name.find('h2').text.replace(
                            '\n', "").split(" ")[-2]
                        actor_en2_name = name.find('h2').text.replace(
                            '\n', "").split(" ")[-1]
                        if (actor_en1_name != ""):
                            actor_en_name = f'{actor_en1_name} {actor_en2_name}'
                        else:
                            actor_en_name = actor_en2_name
                        actor_dic = {
                            "actor_cn_name": actor_names,
                            "actor_en_name": actor_en_name,
                            "actor_photos": actor_photos
                        }

                        actor_list.append(actor_dic)

                # print(actor_list)

            except Exception as e:
                # print(e)
                actor_list = [{}]

            # ------------------------------------------------
            # Movies Trailer URL

            # Get trailer url
            trailer = info_soup.find(
                'div', class_='maincontent ga_trailer movie_intro')
            trailer2 = trailer.find('div', class_='movie_tab')
            trailer_url = trailer2.find_all('a', class_='gabtn')[1]['href']

            # Get video from the trailer url
            trailer_source = requests.get(trailer_url).text
            trailer_soup = BeautifulSoup(trailer_source, 'lxml')
            # trailer_video = trailer_soup.find('div', class_='informbox _c notice')
            trailer_video = trailer_soup.find('div', class_='l_box_inner_20')

            try:
                trailer_video_URL = trailer_video.find_all('a')[0]['href']
                ## trailer_video_iframe = trailer_video.find('iframe')['src'].split('?')[0]

            except Exception as e:
                print(f'Something wrong with the trailer part: {e}')
                trailer_video_URL = 'No Trailer'
                # try:
                #     trailer_video_URL = trailer_video.find_all('a')[0]['href']
                # except Exception:
                #     trailer_video_URL = 'No Trailer'

            # ------------------------------------------------
            # Movie Location and Times
            for area_id in area:
                headers = {
                    'User-Agent': '{secrets.User_agent}',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://movies.yahoo.com.tw/movietime_result.html/id={movie_id}',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'keep-alive',
                    'TE': 'Trailers',
                }

                params = (
                    ('movie_id', movie_id),
                    ('date', current_time),
                    ('area_id', area_id),
                )

                response = requests.get('https://movies.yahoo.com.tw/ajax/pc/get_schedule_by_movie',
                                        headers=headers, params=params, cookies=secrets.cookies)
                view = response.json()['view']
                movie_theater_sp = BeautifulSoup(view, 'lxml')
                # movie_theater = movie_theater_sp.find_all('ul')
                # TODO: Enhance the logic without too much reptition
                for location, play_time in zip(movie_theater_sp.find_all('li', class_='adds'), movie_theater_sp.find_all('div', class_='input_picker jq_input_picker')):
                    match area_id:
                        case 8:
                            if(location.a.text and play_time.text.split() != None):
                                area_8 = {location.a.text: play_time.text.split()}
                                area_8_list.append(area_8)
                                print('新北市')
                            continue
                        case 28:
                            if(location.a.text and play_time.text.split() != None):
                                area_28 = {location.a.text: play_time.text.split()}
                                area_28_list.append(area_28)
                                print('台北市')
                            continue
                        case _:
                            print('Something happened at location and play_time')
                            break
            # ------------------------------------------------
            # Write the data into json format
            sumDic = {
                "movie_id": movie_id,
                "movie_cn_name": movie_cn_name,
                "movie_en_name": movie_en_name,
                "movie_rating": movie_rating,
                "release_movie_time": release_movie_time,
                "movie_trailer": trailer_video_URL,
                "movie_poster": movie_poster,
                "movie_photos": movie_photos_list,
                "movie_introduction": movie_introduction,
                "actors": actor_list,
                "locations_with_movietimes": {
                    '8': {
                        'location': '新北市',
                        'theater': area_8_list
                        },
                    '28': {
                        'location': '台北市', 
                        'theater': area_28_list
                        }
                    
                    
                    
                    }
            }

            sumList.append(sumDic)
            print(sumList)
            movie_photos_list = []
            actor_list = []
            area_28_list = []
            area_8_list = []
with open(jsonFilePath, 'w', encoding="utf-8-sig") as jsonFile:
    e = json.dumps(sumList, ensure_ascii=False, indent=4)
    jsonFile.write(e)
