import os
from requests import get
from requests import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def download_image(book_details, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = get(book_details['cover_link'])
    response.raise_for_status()
    filename = os.path.basename(book_details['cover_link'])
    _, extension = os.path.splitext(filename)
    with open(f'{folder}{book_details["title"]}{extension}', 'wb') as file:
        file.write(response.content)


def download_txt(response, book_details, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    sanitized_book_name = sanitize_filename(book_details['title'])
    with open(f'{folder}{sanitized_book_name}.txt', 'w') as file:
        file.write(response.text)


def fetch_book_details(book_id):
    url = 'https://tululu.org'
    response = get(f'{url}/b{book_id}')

    soup = BeautifulSoup(response.text, 'lxml')
    book_header = soup.find('h1').text.split('::')
    book_cover = soup.find('div', class_='bookimage').find('img')['src']
    book_cover = urljoin('https://tululu.org', book_cover)
    book_comments_soup = soup.find_all('div', class_='texts')

    book_details = {
        'title': book_header[0].strip(),
        'author': book_header[1].strip(),
        'cover_link': book_cover,
        'comments': [book_comment.find('span').text for book_comment in book_comments_soup]
    }
    return book_details


def check_for_redirect(response):
    if response.history:
        raise HTTPError("The request was redirected.")


def fetch_book(url, book_id):
    payload = {
        'id': book_id
    }
    response = get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    book_details = fetch_book_details(book_id)
    download_txt(response, book_details)
    download_image(book_details)


if __name__ == "__main__":
    url = 'https://tululu.org/txt.php'

    for book_id in range(1, 11):
        try:
            fetch_book(url, str(book_id))
        except HTTPError as err:
            print(err)
