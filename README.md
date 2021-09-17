# Cinema Search

Cinema Search is a full stack python project that pulls movie data from https://www.themoviedb.org/?language=en-US. The application allows you to browse and build
your own watch list that can be exported to a file and saved locally.

## Deployed

This project is deployed here- http://springboard-cinema-search.herokuapp.com/

## Flow

Users are greeted with a form to signup. Once you're logged in you will be redirected to a screen showing a list of the current popular movies. There are also 
buttons to redirect to any upcoming and top rated movies. Movie cards are displayed 20 per page and more can be viewed using the pagination. If the user has any
specific film in mind there is a search bar as well. Once a movie card is clicked it takes you to a new page that displays information about that movie and provides
similar movies below that info. Movies can be added and removed from a user's list. This list can be exported and saved for future use.

## Features
- Authentication (passwords hashed with bcrypt)
- Pagination
- CRUD functionality
- Ability to export list data to a txt file
- Search functionality
- Form Validation

## Technologies
- Flask
- SQLAlchemy ORM
- PostgresQL
- WTForms
- Jinja
