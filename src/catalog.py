from __future__ import annotations

from typing import Any

OFFLINE_MOVIES: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Inception",
        "release_date": "2010-07-16",
        "director": "Christopher Nolan",
        "genres": ["Science Fiction", "Thriller"],
        "vote_average": 8.4,
        "overview": (
            "A skilled extractor who steals secrets through shared dreams is "
            "offered a chance to erase his past by planting an idea instead."
        ),
    },
    {
        "id": 2,
        "title": "Interstellar",
        "release_date": "2014-11-07",
        "director": "Christopher Nolan",
        "genres": ["Science Fiction", "Drama", "Adventure"],
        "vote_average": 8.7,
        "overview": (
            "Explorers travel through a wormhole in space in an attempt to secure "
            "humanity's future."
        ),
    },
    {
        "id": 3,
        "title": "Arrival",
        "release_date": "2016-11-11",
        "director": "Denis Villeneuve",
        "genres": ["Science Fiction", "Drama", "Mystery"],
        "vote_average": 7.9,
        "overview": (
            "A linguist works with the military to communicate with mysterious "
            "visitors who have arrived across the world."
        ),
    },
    {
        "id": 4,
        "title": "Parasite",
        "release_date": "2019-05-30",
        "director": "Bong Joon Ho",
        "genres": ["Drama", "Thriller", "Comedy"],
        "vote_average": 8.5,
        "overview": (
            "A struggling family gradually enters the household of a wealthy family "
            "with unexpected consequences."
        ),
    },
    {
        "id": 5,
        "title": "The Dark Knight",
        "release_date": "2008-07-18",
        "director": "Christopher Nolan",
        "genres": ["Action", "Crime", "Drama"],
        "vote_average": 9.0,
        "overview": (
            "Batman faces a criminal mastermind whose campaign of chaos tests the "
            "limits of justice in Gotham City."
        ),
    },
    {
        "id": 6,
        "title": "Spirited Away",
        "release_date": "2001-07-20",
        "director": "Hayao Miyazaki",
        "genres": ["Animation", "Fantasy", "Adventure"],
        "vote_average": 8.6,
        "overview": (
            "A young girl enters a world ruled by spirits and must find the courage "
            "to rescue her parents and return home."
        ),
    },
    {
        "id": 7,
        "title": "Mad Max: Fury Road",
        "release_date": "2015-05-15",
        "director": "George Miller",
        "genres": ["Action", "Adventure", "Science Fiction"],
        "vote_average": 8.1,
        "overview": (
            "In a ruined wasteland, a drifter and a rebel warrior join forces to "
            "escape a tyrant and his army."
        ),
    },
    {
        "id": 8,
        "title": "The Grand Budapest Hotel",
        "release_date": "2014-03-28",
        "director": "Wes Anderson",
        "genres": ["Comedy", "Drama", "Adventure"],
        "vote_average": 8.1,
        "overview": (
            "A devoted concierge and his lobby-boy protege become entangled in a "
            "family fortune and a rapidly changing Europe."
        ),
    },
    {
        "id": 9,
        "title": "Blade Runner 2049",
        "release_date": "2017-10-06",
        "director": "Denis Villeneuve",
        "genres": ["Science Fiction", "Drama", "Mystery"],
        "vote_average": 8.0,
        "overview": (
            "A replicant officer uncovers a secret that sends him searching for a former "
            "detective who disappeared decades earlier."
        ),
    },
    {
        "id": 10,
        "title": "Ex Machina",
        "release_date": "2015-04-10",
        "director": "Alex Garland",
        "genres": ["Science Fiction", "Drama", "Thriller"],
        "vote_average": 7.7,
        "overview": (
            "A programmer is invited to evaluate the consciousness of an advanced "
            "artificial intelligence in an isolated research facility."
        ),
    },
    {
        "id": 11,
        "title": "Her",
        "release_date": "2013-12-18",
        "director": "Spike Jonze",
        "genres": ["Romance", "Science Fiction", "Drama"],
        "vote_average": 8.0,
        "overview": (
            "A lonely writer develops an unexpected relationship with an intelligent "
            "operating system designed to meet his needs."
        ),
    },
    {
        "id": 12,
        "title": "The Matrix",
        "release_date": "1999-03-31",
        "director": "The Wachowskis",
        "genres": ["Science Fiction", "Action"],
        "vote_average": 8.7,
        "overview": (
            "A hacker discovers that the world he knows is a simulated reality and joins "
            "a rebellion against its machine rulers."
        ),
    },
    {
        "id": 13,
        "title": "Moonlight",
        "release_date": "2016-10-21",
        "director": "Barry Jenkins",
        "genres": ["Drama"],
        "vote_average": 7.4,
        "overview": (
            "A young man confronts identity, family, and intimacy across three defining "
            "chapters of his life in Miami."
        ),
    },
    {
        "id": 14,
        "title": "Whiplash",
        "release_date": "2014-10-10",
        "director": "Damien Chazelle",
        "genres": ["Drama", "Music"],
        "vote_average": 8.5,
        "overview": (
            "An ambitious jazz drummer is pushed to his limits by an exacting instructor "
            "at an elite music conservatory."
        ),
    },
    {
        "id": 15,
        "title": "Get Out",
        "release_date": "2017-02-24",
        "director": "Jordan Peele",
        "genres": ["Horror", "Mystery", "Thriller"],
        "vote_average": 7.8,
        "overview": (
            "A visit to meet his girlfriend's family leads a young photographer into a "
            "disturbing conspiracy."
        ),
    },
    {
        "id": 16,
        "title": "Knives Out",
        "release_date": "2019-11-27",
        "director": "Rian Johnson",
        "genres": ["Mystery", "Comedy", "Crime"],
        "vote_average": 7.9,
        "overview": (
            "A detective investigates a wealthy novelist's death among a family full of "
            "conflicting stories and motives."
        ),
    },
    {
        "id": 17,
        "title": "The Social Network",
        "release_date": "2010-10-01",
        "director": "David Fincher",
        "genres": ["Drama", "History"],
        "vote_average": 7.8,
        "overview": (
            "The creation of a social network becomes a story of ambition, friendship, "
            "ownership, and competing lawsuits."
        ),
    },
    {
        "id": 18,
        "title": "Everything Everywhere All at Once",
        "release_date": "2022-03-25",
        "director": "Daniel Kwan and Daniel Scheinert",
        "genres": ["Science Fiction", "Action", "Comedy"],
        "vote_average": 7.8,
        "overview": (
            "A stressed laundromat owner is pulled into a multiverse-spanning adventure "
            "that tests her relationships and sense of self."
        ),
    },
    {
        "id": 19,
        "title": "Princess Mononoke",
        "release_date": "1997-07-12",
        "director": "Hayao Miyazaki",
        "genres": ["Animation", "Fantasy", "Adventure"],
        "vote_average": 8.3,
        "overview": (
            "A cursed prince becomes caught between an industrial settlement and the "
            "gods of a threatened forest."
        ),
    },
    {
        "id": 20,
        "title": "Spider-Man: Into the Spider-Verse",
        "release_date": "2018-12-14",
        "director": "Bob Persichetti, Peter Ramsey, and Rodney Rothman",
        "genres": ["Animation", "Action", "Adventure"],
        "vote_average": 8.4,
        "overview": (
            "A Brooklyn teenager discovers his powers and meets heroes from parallel "
            "dimensions while learning what it means to be Spider-Man."
        ),
    },
    {
        "id": 21,
        "title": "Dune",
        "release_date": "2021-10-22",
        "director": "Denis Villeneuve",
        "genres": ["Science Fiction", "Adventure", "Drama"],
        "vote_average": 8.0,
        "overview": (
            "A gifted heir travels to a dangerous desert world where political conflict "
            "and control of a vital resource shape his destiny."
        ),
    },
    {
        "id": 22,
        "title": "Sicario",
        "release_date": "2015-10-02",
        "director": "Denis Villeneuve",
        "genres": ["Crime", "Drama", "Thriller"],
        "vote_average": 7.7,
        "overview": (
            "An FBI agent joins a covert task force whose methods blur legal and moral "
            "lines along the United States-Mexico border."
        ),
    },
    {
        "id": 23,
        "title": "The Godfather",
        "release_date": "1972-03-24",
        "director": "Francis Ford Coppola",
        "genres": ["Crime", "Drama"],
        "vote_average": 9.2,
        "overview": (
            "The reluctant son of a crime-family patriarch is drawn into the organization "
            "and transformed by power, loyalty, and violence."
        ),
    },
    {
        "id": 24,
        "title": "Paddington 2",
        "release_date": "2018-01-12",
        "director": "Paul King",
        "genres": ["Comedy", "Adventure", "Family"],
        "vote_average": 7.8,
        "overview": (
            "A generous bear searches for the thief of a treasured pop-up book and wins "
            "over an unexpected community along the way."
        ),
    },
]


# Seeded demo interactions keep the collaborative pipeline reproducible and offline.
# They are deliberately labelled as fixtures rather than presented as real user data.
DEMO_RATINGS: dict[str, dict[int, float]] = {
    "sci-fi-explorer": {
        1: 5,
        2: 5,
        3: 5,
        4: 1,
        6: 2,
        9: 5,
        10: 4,
        11: 4,
        12: 5,
        16: 2,
        21: 4,
        24: 1,
    },
    "action-fan": {1: 4, 3: 3, 5: 5, 7: 5, 11: 1, 12: 5, 13: 2, 17: 2, 18: 4, 20: 5, 21: 4, 22: 4},
    "drama-lover": {2: 4, 3: 5, 4: 5, 7: 2, 12: 2, 13: 5, 14: 5, 15: 2, 17: 4, 20: 2, 23: 5, 24: 3},
    "mystery-fan": {2: 2, 3: 5, 4: 4, 6: 2, 9: 5, 10: 4, 13: 2, 15: 5, 16: 5, 20: 2, 22: 4, 23: 4},
    "animation-fan": {
        5: 2,
        6: 5,
        7: 3,
        8: 4,
        10: 2,
        14: 2,
        18: 4,
        19: 5,
        20: 5,
        21: 3,
        22: 1,
        24: 5,
    },
    "crime-buff": {2: 2, 4: 5, 5: 5, 6: 1, 8: 3, 11: 2, 15: 4, 16: 5, 17: 4, 19: 1, 22: 5, 23: 5},
    "indie-viewer": {3: 5, 4: 5, 5: 2, 7: 2, 8: 5, 10: 4, 11: 5, 12: 2, 13: 5, 14: 5, 17: 4, 21: 2},
    "adventure-fan": {
        2: 5,
        4: 2,
        6: 5,
        7: 5,
        8: 4,
        11: 2,
        13: 1,
        17: 2,
        19: 5,
        20: 5,
        21: 5,
        24: 4,
    },
    "thoughtful-tech": {
        1: 5,
        3: 5,
        6: 2,
        7: 2,
        9: 5,
        10: 5,
        11: 5,
        12: 4,
        15: 2,
        17: 5,
        18: 4,
        24: 2,
    },
    "family-night": {
        5: 2,
        6: 5,
        8: 4,
        10: 2,
        15: 1,
        16: 4,
        18: 4,
        19: 5,
        20: 5,
        21: 3,
        22: 1,
        24: 5,
    },
    "thriller-fan": {1: 4, 4: 5, 5: 5, 6: 1, 8: 2, 9: 4, 10: 5, 13: 2, 15: 5, 19: 1, 22: 5, 23: 4},
    "eclectic": {1: 3, 2: 4, 5: 4, 6: 5, 8: 5, 10: 3, 13: 4, 14: 2, 16: 5, 18: 5, 22: 2, 23: 5},
}
