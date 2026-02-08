import axios from 'axios';

const TMDB_API_KEY = process.env.TMDB_API_KEY;
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';

export const fetchMovieDetails = async (movieId) => {
    try {
        const response = await axios.get(`${TMDB_BASE_URL}/movie/${movieId}`, {
            params: {
                api_key: TMDB_API_KEY,
                language: 'en-US'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching movie details:', error);
        throw error;
    }
};

export const searchMovies = async (query) => {
    try {
        const response = await axios.get(`${TMDB_BASE_URL}/search/movie`, {
            params: {
                api_key: TMDB_API_KEY,
                query: query,
                language: 'en-US',
                page: 1,
                include_adult: false
            }
        });
        return response.data.results;
    } catch (error) {
        console.error('Error searching movies:', error);
        throw error;
    }
};

export const fetchPopularMovies = async () => {
    try {
        const response = await axios.get(`${TMDB_BASE_URL}/movie/popular`, {
            params: {
                api_key: TMDB_API_KEY,
                language: 'en-US',
                page: 1
            }
        });
        return response.data.results;
    } catch (error) {
        console.error('Error fetching popular movies:', error);
        throw error;
    }
};