# Scrap internet library
Scrap Internet Library is a single console script that allows you to download books from [https://tululu.org/](https://tululu.org/) library. The books will be saved in *.txt* format to the */books* folder, which will be created in the script's root directory. Along with the books, all related book covers will be saved in the */images* directory.

## How to install

### Installation
Python3 should be already installed

You need **4** additional libraries: lxml, BeautifulSoup, requests, pathvalidate.

To install them use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
As described above, scripts give you possibility to download books.
Script have 2 arguments *start_id* and *end_id*, to give to you control how many books you want download. By default, it's set to *1 to 10*.
All error will be in *error.log* file

Example:
```bash
python3 main.py 10 60
```

## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).