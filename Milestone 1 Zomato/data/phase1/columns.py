"""Hugging Face dataset column names and canonical field mapping."""

# ManikaSaini/zomato-restaurant-recommendation (verified via HF datasets-server)
HF_NAME = "name"
HF_AREA = "location"
HF_CITY = "listed_in(city)"
HF_CUISINES = "cuisines"
HF_RATE = "rate"
HF_COST = "approx_cost(for two people)"
HF_URL = "url"
HF_ADDRESS = "address"
HF_REST_TYPE = "rest_type"
HF_VOTES = "votes"
HF_DISH_LIKED = "dish_liked"
HF_LISTED_TYPE = "listed_in(type)"

REQUIRED_SOURCE_COLUMNS = (HF_NAME, HF_CUISINES, HF_RATE)
