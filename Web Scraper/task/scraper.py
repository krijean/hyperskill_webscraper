import requests
import string
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define the base URL of the page to scrape
base_url = "https://www.nature.com"

# Get user inputs for number of pages and article type
num_pages = int(input("Enter the number of pages to search: "))
article_type = input("Enter the type of articles to search for: ")

# Loop through each page
for page_num in range(1, num_pages+1):
    # Define the URL of the page to scrape
    page_url = urljoin(base_url, f"/nature/articles?sort=PubDate&year=2020&page={page_num}")

    # Send a GET request to the URL
    r = requests.get(page_url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(r.content, "html.parser")

    # Create a directory for the current page
    page_dir = f"Page_{page_num}"
    os.makedirs(page_dir, exist_ok=True)

    # Find all article elements on the page
    articles = soup.find_all("article")

    # Loop through each article
    for article in articles:
        # Get the article type
        article_type_elem = article.find("span", {"data-test": "article.type"})
        if article_type_elem is not None:
            article_type_text = article_type_elem.text.strip()

            # Check if the article type matches the user input
            if article_type_text == article_type:
                # Get the link to the article
                link = article.find("a", {"data-track-action": "view article"})
                article_url = urljoin(base_url, link["href"].replace('/nature/', ''))

                # Send a GET request to the article URL
                article_r = requests.get(article_url)

                # Parse the HTML content of the article using BeautifulSoup
                article_soup = BeautifulSoup(article_r.content, "html.parser")

                # Get the article title
                article_title = link.text.strip()

                # Replace whitespaces and special characters in the article title with underscores

                article_title = article_title.replace("’", "")
                article_title = article_title.translate(str.maketrans("", "", string.punctuation))
                article_title = article_title.replace(" ", "_")

                # Get the article body
                article_body_elem = article_soup.find("p", {"class": "article__teaser"})
                if article_body_elem is not None:
                    article_body = article_body_elem.text.strip()

                    # Save the article to a file
                    with open(os.path.join(page_dir, article_title + ".txt"), "wb") as f:
                        f.write(bytes(article_body, 'utf-8'))

                    print(f"Saved article '{article_title}' to {page_dir}")
                else:
                    print(f"Could not find article body for article '{article_title}' in {page_dir}")
            else:
                print(f"Skipping article with type '{article_type_text}' in {page_dir}")
        else:
            print(f"Could not find article type in {page_dir}")
