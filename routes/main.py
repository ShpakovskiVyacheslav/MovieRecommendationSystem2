from flask import Blueprint, render_template, request, redirect, session
import math
from data import create_session, User
from services.film_service import build_film_query

main_bp = Blueprint('main', __name__)

@main_bp.route('/main/<login>', methods=['GET'])
def main_page(login):
    if 'login' not in session or session['login'] != login:
        return redirect('/')

    db_sess = create_session()
    try:
        user = db_sess.query(User).filter(User.login == login).first()
        if not user:
            return "Пользователь не найден", 404

        query = request.args.get('query', '')
        page = request.args.get('page', 1, type=int)
        per_page = 15

        genres_str = request.args.get('genres', '')
        selected_genres = [g.strip() for g in genres_str.split(',') if g.strip()]
        selected_rating = request.args.get('rating', 'any')
        selected_years = request.args.get('year', 'all')

        session['filters'] = {
            'genres': genres_str,
            'rating': selected_rating,
            'year': selected_years
        }

        base_query = build_film_query(db_sess, query, selected_genres, selected_rating, selected_years)

        total_films = base_query.count()
        total_pages = math.ceil(total_films / per_page) if total_films > 0 else 1
        films = base_query.offset((page - 1) * per_page).limit(per_page).all()

        return render_template('main.html',
                               login=login,
                               username=user.username,
                               query=query,
                               avatar_url=user.avatar,
                               films=films,
                               page=page,
                               rating=selected_rating,
                               year=selected_years,
                               genres=genres_str,
                               total_pages=total_pages,
                               total_films=total_films)
    finally:
        db_sess.close()
