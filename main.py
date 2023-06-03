import argparse
import logging
import os
import sys
import time

from requests import get
from requests import HTTPError, ConnectionError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from dataclasses import dataclass

MAX_RETRIES = 3
RETRY_DELAY = 2


@dataclass
class BookDetails:
    title: str
    author: str
    cover_link: str
    comments: list[str]
    book_genres: list[str]


def check_for_redirect(response):
    if response.history:
        raise HTTPError("The request was redirected.")


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Download books from https://tululu.org/")
    parser.add_argument("start_id", nargs='?', default=1, type=int, help="Specify start id book (dafault = 1)")
    parser.add_argument("end_id", nargs='?', default=10, type=int, help="Specify end id book (dafault = 10)")
    args = parser.parse_args()
    return args


def download_image(book: BookDetails, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = get(book.cover_link)
    response.raise_for_status()
    filename = os.path.basename(book.cover_link)
    _, extension = os.path.splitext(filename)
    with open(f'{folder}{book.title}{extension}', 'wb') as file:
        file.write(response.content)


def download_txt(response, book: BookDetails, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    sanitized_book_name = sanitize_filename(book.title)
    with open(f'{folder}{sanitized_book_name}.txt', 'w') as file:
        file.write(response.text)


def fetch_book_response(url, book_id, param_key='id'):
    if param_key == 'id':
        payload = {
            'id': book_id
        }
        response = get(url, params=payload)
    else:
        response = get(f'{url}/b{book_id}/')
    response.raise_for_status()
    check_for_redirect(response)
    return response


def fetch_book_details(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_header = soup.find('h1').text.split('::')
    book_cover_link = soup.find('div', class_='bookimage').find('img')['src']
    book_cover_link = urljoin(response.url, book_cover_link)
    book_comments_soup = soup.find_all('div', class_='texts')
    book_genres_soup = soup.find('span', class_='d_book').find_all('a')

    book_details = BookDetails(
        title=book_header[0].strip(),
        author=book_header[1].strip(),
        cover_link=book_cover_link,
        comments=[book_comment.find('span').text for book_comment in book_comments_soup],
        book_genres=[book_genre.text for book_genre in book_genres_soup]
    )

    return book_details


def download_book():
    response = fetch_book_response(book_url, str(book_id))
    book_details = fetch_book_details(
        fetch_book_response(
            book_page_url,
            book_id,
            'b'
        )
    )
    download_txt(response, book_details)
    download_image(book_details)


if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    book_url = 'https://tululu.org/txt.php'
    book_page_url = 'https://tululu.org'

    args = get_arguments()

    total_books = args.end_id - args.start_id
    processed_books = 0

    for book_id in range(args.start_id, args.end_id):
        retries = 0

        try:
            download_book()
        except HTTPError as err:
            logging.error(f"Error fetching book {book_id}: {err}")
        except ConnectionError as err:
            while retries < MAX_RETRIES:
                retries += 1
                logging.error(f"Connection error: {err}. Retrying in {RETRY_DELAY} seconds")
            try:
                download_book()
                break
            except (HTTPError, ConnectionError) as err:
                if retries == MAX_RETRIES:
                    error_message = f"Failed to fetch book {book_id} after {MAX_RETRIES} retries."
                    logging.error(error_message)
                    sys.exit(error_message)

                time.sleep(RETRY_DELAY)

        processed_books += 1
        percentage = (processed_books / total_books) * 100
        progress_string = f"Progress: {percentage:.2f}% "
        sys.stdout.write("\r" + progress_string)
        sys.stdout.flush()
    print()
