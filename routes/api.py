from flask import Blueprint, request, session, jsonify, redirect
import requests
from data.db_session import create_session
from data.user_film import UserFilm
from data.films import Film

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/favorites/<int:film_id>', methods=['POST', 'DELETE'])
def add_to_favorites(film_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Необходимо войти в систему'}), 401

    db_sess = create_session()
    try:
        if request.method == 'DELETE':
            user_film = db_sess.query(UserFilm).filter(
                UserFilm.user_id == session['user_id'],
                UserFilm.film_id == film_id
            ).first()
            if user_film:
                db_sess.delete(user_film)
                db_sess.commit()
            return jsonify({'success': True})

        data = request.get_json()
        status = data.get('status', 'like')

        film = db_sess.query(Film).get(film_id)
        if not film:
            return jsonify({'success': False, 'error': 'Фильм не найден'}), 404

        user_film = db_sess.query(UserFilm).filter(
            UserFilm.user_id == session['user_id'],
            UserFilm.film_id == film_id
        ).first()

        if user_film:
            user_film.status = status
        else:
            user_film = UserFilm(
                user_id=session['user_id'],
                film_id=film_id,
                status=status
            )
            db_sess.add(user_film)

        db_sess.commit()
        return jsonify({'success': True})
    finally:
        db_sess.close()

@api_bp.route('/remove_favorite/<login>/<int:film_id>', methods=['GET'])
def remove_favorite(login, film_id):
    if 'user_id' not in session:
        return redirect('/')
    if 'login' not in session or session['login'] != login:
        return redirect('/')

    db_sess = create_session()
    try:
        user_film = db_sess.query(UserFilm).filter(
            UserFilm.user_id == session['user_id'],
            UserFilm.film_id == film_id
        ).first()
        if user_film:
            db_sess.delete(user_film)
            db_sess.commit()
        return redirect(f'/profile/{login}')
    finally:
        db_sess.close()

@api_bp.route('/api/user_films', methods=['GET'])
def get_user_films():
    if 'user_id' not in session:
        return jsonify([])

    db_sess = create_session()
    try:
        user_films = db_sess.query(UserFilm).filter(
            UserFilm.user_id == session['user_id']
        ).all()
        result = [{'film_id': uf.film_id, 'status': uf.status} for uf in user_films]
        return jsonify(result)
    finally:
        db_sess.close()

@api_bp.route('/api/get_recommendations', methods=['GET'])
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        filters = session.get('filters', {})
        selected_genres = filters.get('genres', '')
        selected_rating = filters.get('rating', 'any')
        selected_years = filters.get('year', 'all')

        response = requests.get(
            'http://127.0.0.1:5001/api/recommendations',
            params={'user_id': session['user_id']},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('recommendations'):
                db_sess = create_session()
                try:
                    recommended_ml_ids = data['recommendations']
                    user_films = db_sess.query(UserFilm).filter(
                        UserFilm.user_id == session['user_id']
                    ).all()
                    excluded_film_ids = {uf.film_id for uf in user_films}

                    chunk_size = 500
                    all_films = []
                    for i in range(0, len(recommended_ml_ids), chunk_size):
                        chunk = recommended_ml_ids[i:i + chunk_size]
                        films_chunk = db_sess.query(Film).filter(
                            Film.ml_id.in_(chunk)
                        ).all()
                        all_films.extend(films_chunk)

                    film_dict = {film.ml_id: film for film in all_films}
                    result = []
                    for ml_id in recommended_ml_ids:
                        film = film_dict.get(ml_id)
                        if not film or film.id in excluded_film_ids:
                            continue

                        if selected_genres:
                            film_genre_ids = [str(i.id) for i in film.genres]
                            if not any(i in selected_genres for i in film_genre_ids):
                                continue

                        if selected_rating != 'any':
                            try:
                                min_rating = float(selected_rating)
                                if film.rating < min_rating:
                                    continue
                            except ValueError:
                                pass

                        if selected_years != 'all':
                            try:
                                start, end = map(int, selected_years.split('-'))
                                if not (start <= film.release_year <= end):
                                    continue
                            except ValueError:
                                pass

                        genres = [{'id': g.id, 'name': g.name} for g in film.genres]
                        result.append({
                            'id': film.id,
                            'ml_id': film.ml_id,
                            'name': film.name,
                            'poster': film.poster,
                            'rating': film.rating,
                            'release_year': film.release_year,
                            'description': film.description,
                            'genres': genres
                        })

                    return jsonify({
                        'user_id': session['user_id'],
                        'recommendations': result,
                        'total': len(result)
                    })
                finally:
                    db_sess.close()
            else:
                return jsonify({
                    'user_id': session['user_id'],
                    'recommendations': [],
                    'message': data.get('message', 'No recommendations')
                })
        else:
            return jsonify({'error': 'Не удалось получить рекомендации'}), 500

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Превышено время ожидания сервера', 'recommendations': []}), 200
    except requests.exceptions.ConnectionError:
        return jsonify(
            {'error': 'Сервис рекомендаций недоступен. Пожалуйста, запустите rec.py и обновите страницу.',
             'recommendations': []}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'recommendations': []}), 200

@api_bp.route('/api/film/<int:film_id>', methods=['GET'])
def get_film_details(film_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db_sess = create_session()
    try:
        film = db_sess.query(Film).get(film_id)
        if not film:
            return jsonify({'error': 'Фильм не найден'}), 404
        genres = [{'id': g.id, 'name': g.name} for g in film.genres]
        return jsonify({
            'id': film.id,
            'name': film.name,
            'poster': film.poster,
            'description': film.description,
            'rating': film.rating,
            'release_year': film.release_year,
            'genres': genres
        })
    finally:
        db_sess.close()
