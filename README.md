# Netflix-EDA
An exploratory data analysis of Netflix Movies and Tv shows to understand the evolution of their catalogue
# Netflix Titles: Exploratory Data Analysis

An exploratory analysis of **8,807 Netflix titles** (6,131 movies and 2,676 TV shows) covering catalogue growth, release freshness, seasonality, country and genre mix, content ratings, runtimes, credits, and description language.

The analysis answers eight business-style questions and ends with a findings summary and a list of limitations.

**Tools:** Python · pandas · NumPy · matplotlib · seaborn · SciPy · scikit-learn (stop-word list)

**Scope:** the dataset lists *what is in the catalogue and when it was added*. It has no viewing or popularity data, so findings describe catalogue composition, not what people watch.

---

## Key findings

1. **Mostly movies, mostly recent.** 69.6% of titles are movies, and 70.6% were released in 2015 or later.
2. **Additions peaked in 2019** at 2,016 titles and eased to 1,879 in 2020 (2021 data runs only to 25 Sept).
3. **Q4 is the busiest season for additions.** October to December account for 30.8% of a year's additions (25% if even); February is the quietest month at 6.2%.
4. **The catalogue is ageing.** Titles that were 10+ years old at the time they were added rose from 8.2% of additions in 2016 to 22.0% in 2021.
5. **US-centred, but with distinct national profiles.** The US appears on 46% of titles that list a country. India's catalogue is 92% movies, while South Korea (74%) and Japan (63%) are mostly TV shows.
6. **Drama (3,190 titles) and Comedy (2,255) lead the genres.** TV-MA is the most common rating, and adult ratings make up 46.7% of movies and 42.9% of TV shows. TV has more kids' content (17.4% vs 7.2%).
7. **The median movie runs 98 minutes** and **67% of TV shows have a single season.**
8. **Credits are long-tailed:** 79.5% of credited directors appear on exactly one title.

![Catalogue growth](images/01_catalogue_growth.png)

![Countries](images/04_countries.png)

![Genre mix by country](images/06_genre_by_country.png)

![Ratings](images/07_ratings.png)

---

## Data preparation

The raw file is fairly tidy, so cleaning is conservative:

3 Louis C.K. specials have their runtime (`'74 min'`) in the `rating` column and a blank `duration`: Moved to `duration`; rating left missing
`date_added` stored as text: Parsed to datetime; added `added_year`, `added_month`
`duration` mixes minutes and seasons: Split into numeric `duration_min` (movies) and `n_seasons` (TV)
`NR` and `UR` both mean not rated: Merged to `Not Rated`; added `rating_group` (Kids, Older kids / family, Teens, Adults)
7 country strings end in a stray comma: Stripped; added `primary_country`, `n_countries`
Multi-valued genres: Added `primary_genre`, `n_genres`; the notebook maps movie/TV genre labels to one scheme
Real gaps in `director` (30%), `country` (9%), `cast` (9%): **Kept as missing**, not imputed
14 titles added before their release year: **Kept**: genuine pre-release listings

---

## Repository structure

```
netflix-eda/
├── data/
│   ├── raw/netflix_titles.csv
│   └── processed/netflix_titles_clean.csv
├── notebooks/01_eda.ipynb      # full analysis with outputs and charts
├── src/clean_netflix.py        # cleaning + feature engineering
├── images/                     # charts exported from the notebook
├── requirements.txt
└── README.md
```

## How to run

```bash
git clone https://github.com/imisibanjo/Netflix-EDA.git
cd netflix-eda
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/clean_netflix.py                 # writes data/processed/netflix_titles_clean.csv
jupyter notebook notebooks/01_eda.ipynb
```

---


## Limitations

* No viewing, popularity, or revenue data in the file.
* The data is a **2021 snapshot**: titles added and later removed are missing, so early years look smaller than they were and growth is probably overstated. 2021 is a partial year (to 25 Sept).
* Country, genre, director and cast are multi-valued, so counts are *appearances* and shares can sum to more than 100%.
* Missingness is not random (director is blank for most TV shows), so credit rankings reflect listed credits only.
* The genre mapping (merging movie and TV labels, dropping geographic tags) is a judgment call.

## Possible next steps

* Join viewership or IMDb ratings to move from catalogue composition to performance.
* Cluster titles on description text (TF-IDF) to find themes the genre tags miss.
* Build a small dashboard (Streamlit or Power BI) on the cleaned file.
