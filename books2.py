from fastapi import FastAPI, Path, Query, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Book:
    def __init__(self, id: int, title: str, author: str, description: str, rating: int, published_date: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None)
    title: str = Field(min_length=1, max_length=50)
    author: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=200)
    rating: int = Field(..., ge=0, le=5)
    published_date: int = Field(..., ge=1900, le=2024)

BOOKS = [
    Book(1, "title one", "author one", "description one", 5, 2020),
    Book(2, "title two", "author two", "description two", 4, 2019),
    Book(3, "title three", "author three", "description three", 3, 2021),
    Book(4, "title four", "author four", "description four", 5, 2018),
    Book(5, "title five", "author five", "description five", 4, 2020),
    Book(6, "title six", "author two", "description six", 3, 2019)
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(rating: int = Query(..., ge=0, le=5)):
    books_by_rating = [book for book in BOOKS if book.rating == rating]
    return books_by_rating

@app.get("/books/pub_date/{date}", status_code=status.HTTP_200_OK)
async def read_books_by_date(date: int = Path(gt=1900, le=2024)):
    books_by_date = [book for book in BOOKS if book.published_date == date]
    return books_by_date

@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    BOOKS.append(find_book_id(new_book))

@app.put("/books/update_books", status_code=status.HTTP_200_OK)
async def update_book(book: BookRequest):
    book_change = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = Book(**book.model_dump())
            book_change = True
            return {"message": "Book updated successfully"}
    if not book_change:
        raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/delete_books", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Query(gt=0)):
    book_delete = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            del BOOKS[i]
            book_delete = True
            return {"message": "Book deleted successfully"}
    if not book_delete:
        raise HTTPException(status_code=404, detail="Book not found")

def find_book_id(new_book: Book):
    if len(BOOKS) == 0:
        new_book.id = 1
    else:
        new_book.id = BOOKS[-1].id + 1
    return new_book
