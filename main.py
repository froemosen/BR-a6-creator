import os
import time
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A6
from reportlab.platypus import SimpleDocTemplate, Image

# Rate limiting settings
SEARCH_DELAY_SECONDS = 5  # Adjust this value as needed
MAX_REQUESTS_PER_MINUTE = 10  # Adjust this value as needed
request_counter = 0
last_request_time = time.time()

def google_image_search(query, num_results=1):
    global request_counter
    global last_request_time
    
    site = "site:br.dk"
    query = f"{site} {query}"
    
    search_results = list(search(query, num_results=num_results*10))
    
    # Limit the results to the desired number
    search_results = search_results[:num_results]
    
    for result in search_results:
        if result.startswith("https://www.br.dk"):
            image_url = extract_image_url(result)
            if image_url:
                image_path = download_image(image_url)
                create_pdf_with_image(image_path)
                break
        # Check rate limiting and adjust delay
        request_counter += 1
        if request_counter >= MAX_REQUESTS_PER_MINUTE:
            current_time = time.time()
            elapsed_time = current_time - last_request_time
            if elapsed_time < 60:
                sleep_time = 60 - elapsed_time + 1
                print(f"Rate limit reached. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                last_request_time = time.time()
                request_counter = 0
            else:
                last_request_time = current_time
                request_counter = 0

def extract_image_url(page_url):
    try:
        response = requests.get(page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and 'src' in img_tag.attrs:
                return img_tag['src']
    except Exception as e:
        print(f"Error extracting image URL: {e}")
    return None

def download_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            filename = os.path.basename(image_url)
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded as {filename}")
            return filename
        else:
            print(f"Failed to download image: Status code {response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def create_pdf_with_image(image_path):
    if image_path:
        output_pdf_path = "output.pdf"
        doc = SimpleDocTemplate(output_pdf_path, pagesize=A6, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)

        story = []
        
        img = Image(image_path, width=A6[0], height=A6[1])
        story.append(img)
        
        doc.build(story)
        print(f"PDF with the image has been created as {output_pdf_path}")

if __name__ == "__main__":
    user_input = input("Enter a search query: ")
    num_results = 1  # You can change this number to get more results if needed
    google_image_search(user_input, num_results)
