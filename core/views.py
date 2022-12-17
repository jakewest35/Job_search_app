from django.shortcuts import render
from decouple import config
from core.forms import SearchForm
import requests as req
import json

# Create your views here.


def home(request):
    return render(request, "core/core.html")


def search(request):
    if request.method == "POST":
        search = SearchForm(request.POST)
        if search.is_valid():
            search_terms = search.cleaned_data["search_terms"]
            city = search.cleaned_data["city"]
            print("\n\n################ USER SEARCHED FOR SOMETHING ################")
            print("They searched for {} in {}".format(search_terms, city))

            linkedin_results = linkedin(search_terms, city)
            indeed_results = indeed(search_terms, city)
            # Consolidate the data into 1 dictionary so parsing on the front end
            # will be easier
            consolidated_data = consolidate(linkedin_results, indeed_results)
            context = {
                "consolidated_data": consolidated_data
            }
            return render(request, "core/results.html", context)
    else:
        return render(request, "core/search.html", {"search_form": SearchForm})


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
        "X-RapidAPI-Key": config("RAPID_API_KEY"),
        "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com"
    }
    api_response = req.request(
        "POST", linkedin_url, json=linkedin_payload, headers=linkedin_headers)
    parsed = api_response.json()
    api_dict = {}
    id = 0
    for job in parsed:
        tmp = {
            "job_title": job["job_title"],
            "city": job["job_location"],
            "company_name": job["company_name"],
            "link": job["linkedin_job_url_cleaned"],
            "date_posted": job["posted_date"],
            "source": "Linkedin"
        }
        api_dict[id] = tmp
        id += 1
    print("linkedin Finished")
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
        "X-RapidAPI-Key": config("RAPID_API_KEY"),
        "X-RapidAPI-Host": "indeed11.p.rapidapi.com"
    }
    api_response = req.request(
        "POST", indeed_url, json=indeed_payload, headers=indeed_headers)
    parsed = api_response.json()
    print(parsed)
    api_dict = {}
    id = 0
    for job in parsed:
        tmp = {
            "job_title": job["job_title"],
            "city": job["location"],
            "company_name": job["company_name"],
            "link": job["url"],
            "date_posted": job["date"],
            "source": "Indeed"
        }
        api_dict[id] = tmp
        id += 1
    print("indeed Finished")
    return api_dict


def consolidate(lst1, lst2):
    """
    Converts the api responses from a list of dictionaries to a string containing a
    dictionary of dictionaries so they can be handled using json.loads()
    """
    res_dict = {}
    id = 0
    for item in lst1:
        tmp = {
            "job_title": lst1[item]["job_title"],
            "city": lst1[item]["city"],
            "company_name": lst1[item]["company_name"],
            "link": lst1[item]["link"],
            "date_posted": lst1[item]["date_posted"],
            "source": lst1[item]["source"]
        }
        res_dict[id] = tmp
        id += 1
    for item in lst2:
        tmp = {
            "job_title": lst2[item]["job_title"],
            "city": lst2[item]["city"],
            "company_name": lst2[item]["company_name"],
            "link": lst2[item]["link"],
            "date_posted": lst2[item]["date_posted"],
            "source": lst2[item]["source"]
        }
        res_dict[id] = tmp
        id += 1
    return res_dict
