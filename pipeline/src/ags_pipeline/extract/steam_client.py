
import requests
import pandas as pd
import time
import random
from typing import List, Dict, Any, Optional

class SteamClient:
	"""
	Simple Steam API client for fetching app list, app details, and reviews.
	Returns pandas DataFrames for in-notebook exploration.
	"""
	APPLIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
	APPDETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={appId}&cc=US&l=en"
	REVIEWS_URL = "https://store.steampowered.com/appreviews/{appId}?json=1&filter=recent&language=all&num_per_page={count}"

	def __init__(self, session: Optional[requests.Session] = None, delay: float = 0.5):
		self.session = session or requests.Session()
		self.delay = delay  # seconds between requests

	def get_all_apps(self) -> pd.DataFrame:
		resp = self.session.get(self.APPLIST_URL)
		resp.raise_for_status()
		data = resp.json()
		apps = data.get("applist", {}).get("apps", [])
		df = pd.DataFrame(apps)
		return df

	def get_app_details(self, app_ids: List[int]) -> pd.DataFrame:
		rows = []
		for app_id in app_ids:
			url = self.APPDETAILS_URL.format(appId=app_id)
			try:
				resp = self.session.get(url)
				resp.raise_for_status()
				data = resp.json()
				app_data = data.get(str(app_id), {})
				if app_data.get("success") and "data" in app_data:
					row = app_data["data"]
					row["steam_appid"] = app_id
					rows.append(row)
			except Exception:
				pass
			time.sleep(self.delay)
		return pd.DataFrame(rows)

	def get_reviews(self, app_id: int, count: int = 100) -> pd.DataFrame:
		url = self.REVIEWS_URL.format(appId=app_id, count=count)
		try:
			resp = self.session.get(url)
			resp.raise_for_status()
			data = resp.json()
			reviews = data.get("reviews", [])
			rows = []
			for r in reviews:
				row = {
					"recommendationid": r.get("recommendationid"),
					"author_steamid": r.get("author", {}).get("steamid"),
					"review": r.get("review"),
					"votes_up": r.get("votes_up"),
					"votes_funny": r.get("votes_funny"),
					"voted_up": r.get("voted_up"),
					"timestamp_created": r.get("timestamp_created"),
					"language": r.get("language"),
					"app_id": app_id
				}
				rows.append(row)
			return pd.DataFrame(rows)
		except Exception:
			return pd.DataFrame([])

	def sample_apps_with_details(self, n: int = 100, seed: int = 42) -> pd.DataFrame:
		"""Get a random sample of n apps with details."""
		all_apps = self.get_all_apps()
		all_apps = all_apps[all_apps["name"].str.len() > 2]  # filter out empty names
		sample = all_apps.sample(n=n, random_state=seed)
		details = self.get_app_details(sample["appid"].tolist())
		return details
