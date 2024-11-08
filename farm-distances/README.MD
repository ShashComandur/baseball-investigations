# Farm Distances (In Progress)

### Intro
This is a quick visualization I worked on, where I wanted to calculate the distances between minor league affiliate teams in a given MLB organization. I had this idea after learning that all of the Atlanta Braves' affiliate teams are in the state of Georgia, which got me thinking about how it probably benefits callups from the minors to not have to travel as much (marginal as it may be).

### Goal
Create a visualization of the spatial distribution of MLB/MiLB stadiums and see what we can learn from it.

### Method
I initially tried building a scraper to get the stadium address data from the MLB and MiLB websites, but this proved to be a bit cumbersome. I instead tried using the [MLB Stats API](https://statsapi.mlb.com/api/v1/), which has tables related to teams across all of MLB/MiLB. 

While it is probably more reasonable of an approach to do all of this in one language or stack, I thought it would be a good idea to connect different services together to jog my memory (and get some practice with) on how they intertwine.

The Python script `farm-distances-2024.py` grabs the data from the API, destructures, filters, and the stores it in a local PostgreSQL database. I did this because of the natural foreign key relation between the schemas as given by the API (this did not end up being particularly useful, but maybe it will for a future project ¯\\_(ツ)_/¯). The data was then ported into Tableau to create the visualization!

### Result
The result is the following visualization, published [here](https://public.tableau.com/shared/KM2YDXXXF?:display_count=n&:origin=viz_share_link). One major flaw with this visualization is the quality of the data! I expected venue information pulled from MLB's API to be completely up to date for 2024, but many rows in this database are simply null or out of date. The lack of lat/long coordinate data was a specific issue for this visualization, as only 88 of the 325 total venues used in 2024 had it.  