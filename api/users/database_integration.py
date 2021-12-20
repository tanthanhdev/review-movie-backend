from django.shortcuts import render
from api.products.models import *
from api.reviews.models import *
from api.users.models import *
import requests

def update_database(tables, start, end):
    api_key = 'b9a976cfaf1c85914a33eaa27fdee1be'
    print(tables)
    tablesLength = len(tables)
    for index in range(tablesLength):
        if tables[index] == "products" or tables[index] == "all":
            # Products
            if start and end:
                for i in range(int(start), int(end)+1):
                    product = Product()
                    resProduct = requests.request('GET', 'https://api.themoviedb.org/3/movie/{product_id}?api_key={api_key}&language=en-US'.format(product_id=i, api_key=api_key))
                    data = resProduct.json()
                    try:
                        if data["success"] == False:
                            continue
                    except:
                        pass
                    for key in data:
                        if key == 'genres' or key == 'production_companies' or key == 'production_countries' or key == 'spoken_languages' or key == 'belongs_to_collection':
                            #belongs_to_collection: current time we disable this feature
                            continue
                        setattr(product, key, data[key])
                    setattr(product, "domain", "https://www.themoviedb.org/t/p/w1920_and_h800_multi_faces")
                    product.save()
                    # # Reviews
                    resReviews = requests.request('GET', 'https://api.themoviedb.org/3/movie/{review_id}/reviews?api_key={api_key}&language=en-US&page=1'.format(review_id=i, api_key=api_key))
                    dataReviews = resReviews.json()
                    try:
                        if dataReviews["success"] == False:
                            continue
                    except:
                        pass
                    if dataReviews['total_pages']:
                        for k2 in range(dataReviews['total_pages']):
                            print(k2+1)
                    try:
                        if dataReviews['results']:
                            reviewLength = len(dataReviews['results'])
                            for f in range(reviewLength):
                                review = Review.objects.filter(id_temp=dataReviews['results'][f]['id'])
                                if not review:
                                    review =  Review()
                                    for key in dataReviews['results'][f]:
                                        if key == 'author_details':
                                            setattr(review, key, dataReviews['results'][f][key]['rating'])
                                        else:
                                            if key == 'id':
                                                setattr(review, 'id_temp', dataReviews['results'][f][key])
                                            else:
                                                setattr(review, key, dataReviews['results'][f][key])
                                    setattr(review, 'status', 'Active')
                                    setattr(review, 'product_id', i)
                                    review.save()
                    except: pass
                    # Videos
                    resVideos = requests.request('GET', 'https://api.themoviedb.org/3/movie/{video_id}/videos?api_key={api_key}&language=en-US&page=1'.format(video_id=i, api_key=api_key))
                    dataVideos = resVideos.json()
                    try:
                        if dataVideos["success"] == False:
                            continue
                    except:
                        pass
                    try:
                        if dataVideos['results']:
                            videoLength = len(dataVideos['results'])
                            for f in range(videoLength+1):
                                video = Video.objects.filter(id_temp=dataVideos['results'][f]['id'])
                                if not video:
                                    video =  Video()
                                    for key in dataVideos['results'][f]:
                                        if key == 'id':
                                            setattr(video, 'id_temp', dataVideos['results'][f][key])
                                        else:
                                            setattr(video, key, dataVideos['results'][f][key])
                                    setattr(video, 'product_id', i)
                                    setattr(video, "domain", "https://www.themoviedb.org/video/play?key=")
                                    video.save()
                    except: pass
                    try:
                        if data['genres']:
                            genresLength = len(data['genres'])
                            for y in range(genresLength):
                                genre = Genre.objects.get(id=int(data['genres'][y]['id']))
                                product.genre.add(genre)
                    except: pass
                    try:
                        if data['production_companies']:
                            companiesLength = len(data['production_companies'])
                            for z in range(companiesLength):
                                try:
                                    company = Company.objects.get(id=int(data['production_companies'][z]['id']))
                                except:
                                    resCompany = requests.request('GET', 'https://api.themoviedb.org/3/company/{company_id}?api_key={api_key}'.format(company_id=data['production_companies'][z]['id'], api_key=api_key))
                                    company = Company()
                                    dataCompany = resCompany.json()
                                    try:
                                        if dataCompany["success"] == False:
                                            continue
                                    except:
                                        pass
                                    for key in dataCompany:
                                        setattr(company, key, dataCompany[key])
                                    company.save()
                                product.company.add(company)
                    except: pass
                    try:
                        if data['production_countries']:
                            genresLength = len(data['production_countries'])
                            for g in range(genresLength):
                                country = Country.objects.get(english_name=data['production_countries'][g]['name']
                                                        , iso_3166_1=data['production_countries'][g]['iso_3166_1'])
                                product.country.add(country)
                    except: pass
                    try:
                        if data['spoken_languages']:
                            languagesLength = len(data['spoken_languages'])
                            for h in range(languagesLength):
                                language = Language.objects.get(english_name=data['spoken_languages'][h]['english_name']
                                                               , name=data['spoken_languages'][h]['name']
                                                        , iso_639_1=data['spoken_languages'][h]['iso_639_1'])
                                product.language.add(language)
                    except: pass
                    # Get the cast and crew for a movie.
                    resCredits = requests.request('GET', 'https://api.themoviedb.org/3/movie/{product_id}/credits?api_key={api_key}&language=en-US'.format(product_id=i, api_key=api_key))
                    data = resCredits.json()
                    try:
                        if data["success"] == False:
                            continue
                    except:
                        pass
                    try:
                        if data["cast"]:
                            castLength = len(data["cast"])
                            for h in range(castLength):
                                cast = Cast()
                                for key in data["cast"][h]:
                                    setattr(cast, key, data["cast"][h][key])
                                setattr(cast, "domain", "https://www.themoviedb.org/t/p/w138_and_h175_face")
                                cast.save()
                                product.cast.add(cast)
                    except: pass
                    try:         
                        if data["crew"]:
                            crewLength = len(data["crew"])
                            for h in range(crewLength):
                                crew = Crew()
                                for key in data["crew"][h]:
                                    setattr(crew, key, data["crew"][h][key])
                                setattr(crew, "domain", "https://www.themoviedb.org/t/p/w138_and_h175_face")
                                crew.save()   
                                product.crew.add(crew)
                    except: pass
                    
                    
                    
        if tables[index] == "genres" or tables[index] == "all":
            # Genres primary
            resGenre = requests.request('GET', 'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US'.format(api_key=api_key))
            data = resGenre.json()
            length = len(data['genres'])
            for i in range(length):
                genre = Genre()
                for key in data['genres'][i]:        
                    setattr(genre, key, data['genres'][i][key])
                genre.save()   
        if tables[index] == "companies" or tables[index] == "all":
            # Companies
            if start and end:
                for i in range(int(start), int(end)):
                    resCompany = requests.request('GET', 'https://api.themoviedb.org/3/company/{company_id}?api_key={api_key}'.format(company_id=i, api_key=api_key))
                    company = Company()
                    data = resCompany.json()
                    try:
                        if data["success"] == False:
                            continue
                    except:
                        pass
                    for key in data:
                        setattr(company, key, data[key])
                    company.save()
        if tables[index] == "countries" or tables[index] == "all":
            #Countries
            resCountries = requests.request('GET', 'https://api.themoviedb.org/3/configuration/countries?api_key={api_key}'.format(api_key=api_key))
            data = resCountries.json()
            countriesLength = len(data)
            for i in range(countriesLength):
                country = Country()
                for key in data[i]:
                    setattr(country, key, data[i][key])
                country.save()
        if tables[index] == "languages" or tables[index] == "all":
            #Languages
            resLanguages = requests.request('GET', 'https://api.themoviedb.org/3/configuration/languages?api_key={api_key}'.format(api_key=api_key))
            data = resLanguages.json()
            languagesLength = len(data)
            for i in range(languagesLength):
                language = Language()
                for key in data[i]:
                    setattr(language, key, data[i][key])
                language.save()
                    
            
    history = History.objects.create()
    history.save()
            

if __name__ == '__main__':
    update_database()
                            