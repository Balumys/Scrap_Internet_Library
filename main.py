import os
from requests import get
from requests import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(response, book_details, folder='books/'):
    sanitized_book_name = sanitize_filename(book_details['title'])
    with open(f'book/{sanitized_book_name}.txt', 'w') as file:
        file.write(response.text)
        file.close()


def fetch_book_details(book_id):
    url = 'https://tululu.org'
    response = get(f'{url}/b{book_id}')
    soup = BeautifulSoup(response.text, 'lxml')
    book_header = soup.find('h1').text.split('::')
    book_details = {
        'title': book_header[0].strip(),
        'author': book_header[1].strip()
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


if __name__ == "__main__":
    folder_name = "book"
    url = 'https://tululu.org/txt.php'

    os.makedirs(folder_name, exist_ok=True)

    for book_id in range(1, 11):
        try:
            fetch_book(url, str(book_id))
        except HTTPError as err:
            print(err)
