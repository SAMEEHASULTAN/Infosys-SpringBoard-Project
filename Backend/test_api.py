import requests

# Your RapidAPI key is already set
RAPIDAPI_KEY = "c908487722msh9e501e6608da515p131ed5jsnb57983055943"

print(f"Testing JSearch API with key: {RAPIDAPI_KEY[:10]}...")

url = "https://jsearch.p.rapidapi.com/search"

querystring = {
    "query": "Python Developer in India",
    "page": "1",
    "num_pages": "1"
}

headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com"
}

try:
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API working! Found {len(data.get('data', []))} jobs")
        if data.get('data'):
            first_job = data['data'][0]
            print(f"\n📌 Sample job:")
            print(f"   Title: {first_job.get('job_title')}")
            print(f"   Company: {first_job.get('employer_name')}")
            print(f"   Location: {first_job.get('job_city')}, {first_job.get('job_country')}")
            print(f"   Apply URL: {first_job.get('job_apply_link')}")
        else:
            print("No jobs found in response")
    else:
        print(f"❌ API error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")