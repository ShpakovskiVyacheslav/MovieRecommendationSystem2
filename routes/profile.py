from flask import Blueprint, render_template, request, redirect, session
import random
import math
import os
from data import create_session, User, Film, FilmGenre, UserFilm
from config import Config

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/<login>', methods=['GET', 'POST'])
def profile(login):
    if 'login' not in session or session['login'] != login:
        return redirect('/')

    db_sess = create_session()
    try:
        user = db_sess.query(User).filter(User.login == login).first()
        if not user:
            return "Пользователь не найден", 404

        if request.method == 'POST' and 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = f"{login}_{random.randint(1000, 9999)}.jpg"
                file.save(os.path.join(Config.UPLOADS_DIR, filename))

                old_avatar = user.avatar
                if old_avatar:
                    old_path = os.path.join(Config.UPLOADS_DIR, old_avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                user.avatar = filename
                db_sess.commit()
                return redirect(f'/profile/{login}')

        page_liked = request.args.get('page_liked', 1, type=int)
        page_not_interested = request.args.get('page_not_interested', 1, type=int)
        per_page = 15

        genres_str = request.args.get('genres', '')
        selected_genres = [g.strip() for g in genres_str.split(',') if g.strip()]
        selected_rating = request.args.get('rating', 'any')
        selected_years = request.args.get('year', 'all')

        favorite_films_query = db_sess.query(Film).join(UserFilm).filter(
            UserFilm.user_id == user.id,
            UserFilm.status == 'like'
        ).order_by(Film.rating.desc().nullslast())
        liked_count_total = favorite_films_query.count()

        not_interested_films_query = db_sess.query(Film).join(UserFilm).filter(
            UserFilm.user_id == user.id,
            UserFilm.status == 'not_interested'
        ).order_by(Film.rating.desc().nullslast())
        not_interested_count_total = not_interested_films_query.count()

        if selected_genres:
            favorite_films_query = favorite_films_query.join(FilmGenre).filter(
                FilmGenre.genre_id.in_(selected_genres)
            ).order_by(Film.rating.desc().nullslast())
            not_interested_films_query = not_interested_films_query.join(FilmGenre).filter(
                FilmGenre.genre_id.in_(selected_genres)
            ).order_by(Film.rating.desc().nullslast())

        if selected_rating != "any":
            favorite_films_query = favorite_films_query.filter(
                Film.rating >= float(selected_rating)
            ).order_by(Film.rating.desc().nullslast())
            not_interested_films_query = not_interested_films_query.filter(
                Film.rating >= float(selected_rating)
            ).order_by(Film.rating.desc().nullslast())

        if selected_years != "all":
            start_year, end_year = map(int, selected_years.split('-'))
            favorite_films_query = favorite_films_query.filter(
                Film.release_year.between(start_year, end_year)
            ).order_by(Film.rating.desc().nullslast())
            not_interested_films_query = not_interested_films_query.filter(
                Film.release_year.between(start_year, end_year)
            ).order_by(Film.rating.desc().nullslast())

        total_pages_liked = math.ceil(liked_count_total / per_page) if liked_count_total > 0 else 1
        favorite_films = favorite_films_query.offset((page_liked - 1) * per_page).limit(per_page).all()

        total_pages_not_interested = math.ceil(
            not_interested_count_total / per_page) if not_interested_count_total > 0 else 1
        not_interested_films = not_interested_films_query.offset((page_not_interested - 1) * per_page).limit(
            per_page).all()

        return render_template('profile.html',
                               login=login,
                               user=user,
                               liked_count_total=liked_count_total,
                               not_interested_count_total=not_interested_count_total,
                               favorite_films=favorite_films,
                               not_interested_films=not_interested_films,
                               page_liked=page_liked,
                               total_pages_liked=total_pages_liked,
                               page_not_interested=page_not_interested,
                               total_pages_not_interested=total_pages_not_interested,
                               selected_rating=selected_rating,
                               selected_years=selected_years,
                               selected_genres=genres_str)
    finally:
        db_sess.close()
