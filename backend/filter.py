
# database of keywords for each element
ELEMENT_KEYWORDS = {
    "Land Use": ["rural", "land use", "distance", "zoning", "slope", "development", "agriculture", "urban", "reserve", "line", "boundary", "buffer", "ordinance", "gateway", "road", "building"],
    "Circulation": ["circulation", "travel", "transportation", "route", "traffic", "pedestrian", "vehic", "rider", "flexible", "parking", "bike", "trail", "connection", "transit", "walk", "shuttle"],
    "Safety": ["safety", "evacuation", "fire", "wildfire", "emergency", "danger", "hazard", "fuel", "flood", "dam", "tank", "landslide", "voltage", "electric", "displace", "care", "shelter", "storm", "geolog", "fault", "seismic", "liquefaction", "landslide", "safe", "respond", "operat", "assist", "leak"],
    "Wildfire": ["emergency", "evacuat", "fire", "hazard", "disaster", "fuel", "flood", "resistant", "equipment", "suppression", "hydrant", "defensible", "preserv", "protection", "sprinkler", "danger", "gas", "ignition"],
    "Noise": ["noise", "sensitive", "exposure", "generat", "barrier", "sound", "separat", "reduction", "NLR"],
    "Housing": ["housing", "residential", "apartments", "dwelling", "family", "story", "unit", "density", "affordable", "rent", "condo", "income", "loan", "living", "habita", "homeless", "shelter"],
    
    # Add more categories & keywords as needed
    "Agriculture": ["agriculture", "farming", "crops", "farm"]
}


def tag_policy_element(text):
    text_lower = text.lower()
    tags = []
    for element, keywords in ELEMENT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(element)
    return tags if tags else ["Other"]


