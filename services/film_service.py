from sqlalchemy import case, func


def build_film_query(db_sess, query, selected_genres, selected_rating, selected_years):
    """Построение запроса для поиска фильмов"""
    from data.films import Film
    from data.film_genre import FilmGenre

    base_query = db_sess.query(Film).order_by(Film.rating.desc().nullslast())

    if query:
        lower_query = query.lower()
        relevance = case(
            (func.lower(Film.name) == lower_query, 0),
            (func.lower(Film.name).like(f"{lower_query}%"), 1),
            else_=2
        )
        base_query = db_sess.query(Film).filter(
            func.lower(Film.name).like(f"%{lower_query}%")
        ).order_by(relevance, Film.rating.desc().nullslast())

    if selected_genres:
        base_query = base_query.join(FilmGenre).filter(
            FilmGenre.genre_id.in_(selected_genres)
        ).order_by(Film.rating.desc().nullslast())

    if selected_rating != "any":
        base_query = base_query.filter(
            Film.rating >= float(int(selected_rating))
        ).order_by(Film.rating.desc().nullslast())

    if selected_years != "all":
        start_year, end_year = map(int, selected_years.split('-'))
        base_query = base_query.filter(
            Film.release_year.between(start_year, end_year)
        ).order_by(Film.rating.desc().nullslast())

    return base_query
