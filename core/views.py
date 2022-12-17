from django.shortcuts import render
from decouple import config
from core.forms import SearchForm
import requests as req

# Create your views here.


def home(request):
    return render(request, 'core/core.html')


def search(request):
    if request.method == 'POST':
        search = SearchForm(request.POST)
        if search.is_valid():
            search_terms = search.cleaned_data['search_terms']
            city = search.cleaned_data['city']
            print("\n\n################ USER SEARCHED FOR SOMETHING ################")
            print("They searched for {} in {}".format(search_terms, city))

            linkedin_results = linkedin(search_terms, city)
            indeed_results = indeed(search_terms, city)
            # parse the JSON data and consolidate into 1 JSON object so
            # parsing in the template will be easier
            consolidated_data = {}
            id = 0
            for job in linkedin_results:
                tmp = {
                    'job_title': linkedin_results[job]['job_title'],
                    'city': linkedin_results[job]['job_location'],
                    'company_name': linkedin_results[job]['company_name'],
                    'link': linkedin_results[job]['linkedin_job_url_cleaned'],
                    'date_posted': linkedin_results[job]['posted_date'],
                    'source': 'Linkedin'
                }
                consolidated_data[id] = tmp
                id += 1
            for job in indeed_results:
                tmp = {
                    'job_title': indeed_results[job]['job_title'],
                    'city': indeed_results[job]['location'],
                    'company_name': indeed_results[job]['company_name'],
                    'link': indeed_results[job]['url'],
                    'date_posted': indeed_results[job]['date'],
                    'source': 'Indeed'
                }
                consolidated_data[id] = tmp
                id += 1
            context = {
                "consolidated_data": consolidated_data
            }
            return render(request, "core/results.html", context)
    else:
        return render(request, 'core/search.html', {'search_form': SearchForm})


def linkedin(terms, city):
    """
    Searches the LinkedIn API through rapidAPI for the users specified search terms.
    """
    linkedin_url = "https://linkedin-jobs-search.p.rapidapi.com/"
    linkedin_payload = {
        "search_terms": terms,
        "location": city,
        "page": "1"
    }
    linkedin_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config('RAPID_API_KEY'),
        "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com"
    }
    api_response = req.request(
        "POST", linkedin_url, json=linkedin_payload, headers=linkedin_headers)
    api_dict = convert_api_response_to_dict(api_response)
    return api_dict


def indeed(terms, city):
    """
    Searches the Indeed API through rapidAPI for the users specified search terms.
    """
    indeed_url = "https://indeed11.p.rapidapi.com/"

    indeed_payload = {
        "search_terms": terms,
        "location": city,
        "page": "1"
    }
    indeed_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config('RAPID_API_KEY'),
        "X-RapidAPI-Host": "indeed11.p.rapidapi.com"
    }
    api_response = req.request(
        "POST", indeed_url, json=indeed_payload, headers=indeed_headers)
    api_dict = convert_api_response_to_dict(api_response)
    return api_dict


def convert_api_response_to_dict(lst):
    """
    Converts the api responses from a list of dictionaries to a string containing a
    dictionary of dictionaries so they can be handled using json.loads()
    """
    res_dict = {}
    id = 0
    for item in lst:
        res_dict[id] = item
        id += 1
    print(res_dict)
    return res_dict
