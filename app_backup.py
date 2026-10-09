import streamlit as st
from PIL import Image, ImageStat, ImageFilter
from dotenv import load_dotenv
import os
import urllib.parse
import urllib.request
import json
import re

load_dotenv()

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")

def identify_plant_with_plantnet(image_file):
    try:
        image_file.seek(0)

        url = "https://my-api.plantnet.org/v2/identify/all"

        query_params = urllib.parse.urlencode({
            "api-key": PLANTNET_API_KEY
        })

        image_data = image_file.read()

        boundary = "----PhantomCropDoctorBoundary"

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="images"; filename="plant.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode() + image_data + (
            f"\r\n--{boundary}\r\n"
            f'Content-Disposition: form-data; name="organs"\r\n\r\n'
            f"leaf\r\n"
            f"--{boundary}--\r\n"
        ).encode()

        request = urllib.request.Request(
            f"{url}?{query_params}",
            data=body,
            method="POST",
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())

        if result.get("results"):
            best = result["results"][0]

            species = best.get("species", {})

            return {
                "name": species.get("scientificNameWithoutAuthor", "Unknown"),
                "common_name": (
                    species.get("commonNames", ["Unknown"])[0]
                    if species.get("commonNames")
                    else "Unknown"
                ),
                "score": round(best.get("score", 0) * 100, 1)
            }

        return None

    except Exception as e:
        return {
            "error": str(e)
        }


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Phantom Symptom Crop Doctor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LANGUAGE DATA
# ============================================================

LANGUAGES = {
    "English": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "Simple plant health guidance for everyone",
    },
    "Hindi": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "हर किसी के लिए आसान पौधा स्वास्थ्य सहायता",
    },
    "Kannada": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "ಎಲ್ಲರಿಗೂ ಸುಲಭವಾದ ಸಸ್ಯ ಆರೋಗ್ಯ ಸಹಾಯ",
    },
    "Tamil": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "அனைவருக்கும் எளிய தாவர ஆரோக்கிய உதவி",
    },
    "Telugu": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "అందరికీ సులభమైన మొక్కల ఆరోగ్య సహాయం",
    },
    "Malayalam": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "എല്ലാവർക്കും എളുപ്പമുള്ള സസ്യ ആരോഗ്യ സഹായം",
    },
    "Marathi": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "प्रत्येकासाठी सोपी वनस्पती आरोग्य मदत",
    },
    "Bengali": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "সবার জন্য সহজ গাছের স্বাস্থ্য সহায়তা",
    },
    "Gujarati": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "દરેક માટે સરળ છોડ આરોગ્ય સહાય",
    },
    "Punjabi": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "ਹਰ ਕਿਸੇ ਲਈ ਆਸਾਨ ਪੌਦਾ ਸਿਹਤ ਸਹਾਇਤਾ",
    },
    "Urdu": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "ہر کسی کے لیے آسان پودوں کی صحت کی مدد",
    },
    "Odia": {
        "title": "🌱 Phantom Symptom Crop Doctor",
        "subtitle": "ସମସ୍ତଙ୍କ ପାଇଁ ସହଜ ଉଦ୍ଭିଦ ସ୍ୱାସ୍ଥ୍ୟ ସହାୟତା",
    },
}


# ============================================================
# PLANT DATABASE
# All lists are sorted alphabetically automatically.
# ============================================================

PLANT_CATEGORIES = {
    "🏠 Home Plants": [
        "Aloe Vera",
        "Areca Palm",
        "Boston Fern",
        "Fiddle Leaf Fig",
        "Jade Plant",
        "Lucky Bamboo",
        "Money Plant",
        "Peace Lily",
        "Philodendron",
        "Pothos",
        "Rubber Plant",
        "Snake Plant",
        "Spider Plant",
        "ZZ Plant",
    ],

    "🚜 Farming Plants": [
        "Barley",
        "Chickpea",
        "Coffee",
        "Cotton",
        "Groundnut",
        "Lentil",
        "Maize",
        "Millet",
        "Mustard",
        "Rice",
        "Soybean",
        "Sugarcane",
        "Sunflower",
        "Tea",
        "Wheat",
    ],

    "🍎 Fruit Plants": [
        "Apple",
        "Banana",
        "Grapes",
        "Guava",
        "Jackfruit",
        "Lemon",
        "Mango",
        "Muskmelon",
        "Orange",
        "Papaya",
        "Pineapple",
        "Pomegranate",
        "Sapota",
        "Strawberry",
        "Sweet Lime",
        "Watermelon",
    ],

    "🌸 Flowering Plants": [
        "Bougainvillea",
        "Chrysanthemum",
        "Dahlia",
        "Geranium",
        "Hibiscus",
        "Jasmine",
        "Lavender",
        "Lotus",
        "Marigold",
        "Orchid",
        "Petunia",
        "Rose",
        "Sunflower",
        "Tulip",
    ],

    "🥬 Vegetable Plants": [
        "Beans",
        "Beetroot",
        "Bitter Gourd",
        "Bottle Gourd",
        "Brinjal",
        "Cabbage",
        "Capsicum",
        "Carrot",
        "Cauliflower",
        "Chilli",
        "Cucumber",
        "Okra",
        "Peas",
        "Potato",
        "Pumpkin",
        "Radish",
        "Spinach",
        "Tomato",
    ],

    "🦋 Exotic Plants": [
        "Alocasia",
        "Anthurium",
        "Begonia",
        "Bird of Paradise",
        "Bromeliad",
        "Calathea",
        "Croton",
        "Ficus Bonsai",
        "Fittonia",
        "Japanese Maple",
        "Monstera",
        "Philodendron",
        "Pitcher Plant",
        "String of Pearls",
        "Venus Flytrap",
    ],
}

for category in PLANT_CATEGORIES:
    PLANT_CATEGORIES[category] = sorted(
        PLANT_CATEGORIES[category],
        key=lambda x: x.lower()
    )


ALL_PLANTS = sorted(
    [
        plant
        for plants in PLANT_CATEGORIES.values()
        for plant in plants
    ],
    key=lambda x: x.lower()
)


# ============================================================
# SYMPTOMS
# ============================================================

SYMPTOMS = [
    "🟡 Yellow leaves",
    "🟤 Brown spots",
    "⚪ White powder",
    "🥀 Wilting",
    "🕳️ Holes in leaves",
    "🌀 Curled leaves",
    "⚫ Black spots",
    "📉 Stunted growth",
    "🍂 Leaf dropping",
    "🌿 Pale leaves",
    "💧 Water-soaked patches",
    "🌱 Weak new growth",
]


# ============================================================
# LOCATION / WEATHER FUNCTIONS
# ============================================================

def get_location_data(place_name):

    """
    Uses Open-Meteo's public geocoding service to convert a place
    name into coordinates.

    No API key is required.
    """

    try:

        encoded = urllib.parse.quote(place_name)

        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={encoded}&count=1&language=en&format=json"
        )

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "PhantomCropDoctor/1.0"}
        )

        with urllib.request.urlopen(request, timeout=5) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        if not data.get("results"):
            return None

        result = data["results"][0]

        return {
            "name": result.get("name", place_name),
            "country": result.get("country", ""),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
        }

    except Exception:
        return None


def get_environment_data(latitude, longitude):

    """
    Retrieves current environmental information from Open-Meteo.
    """

    try:

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            "&current="
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m,"
            "weather_code"
            "&hourly=precipitation"
            "&timezone=auto"
        )

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "PhantomCropDoctor/1.0"}
        )

        with urllib.request.urlopen(request, timeout=5) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        current = data.get("current", {})

        return {
            "temperature": current.get(
                "temperature_2m",
                25
            ),

            "humidity": current.get(
                "relative_humidity_2m",
                60
            ),

            "rainfall": current.get(
                "precipitation",
                0
            ),

            "wind": current.get(
                "wind_speed_10m",
                10
            ),

            "weather_code": current.get(
                "weather_code",
                1
            ),
        }

    except Exception:

        return {
            "temperature": 25,
            "humidity": 60,
            "rainfall": 0,
            "wind": 10,
            "weather_code": 1,
        }


def weather_from_code(code):

    if code == 0:
        return "☀️ Clear"

    if code in [1, 2, 3]:
        return "⛅ Partly Cloudy"

    if code in [45, 48]:
        return "🌫️ Foggy"

    if code in [51, 53, 55, 56, 57]:
        return "🌦️ Drizzle"

    if code in [61, 63, 65, 66, 67]:
        return "🌧️ Rainy"

    if code in [71, 73, 75, 77]:
        return "❄️ Snowy"

    if code in [80, 81, 82]:
        return "🌧️ Rain Showers"

    if code in [95, 96, 99]:
        return "⛈️ Thunderstorm"

    return "🌤️ Variable"


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_leaf_image(image):

    """
    Lightweight visual analysis.

    IMPORTANT:
    This is not a trained disease-recognition model.
    It looks for visual patterns such as:
    - green foliage
    - yellow areas
    - brown areas
    - dark/black areas
    - pale/white areas

    These visual findings form approximately 60% of the
    prototype's assessment.
    """

    image = image.convert("RGB")

    image = image.resize((150, 150))

    pixels = list(image.getdata())

    total = len(pixels)

    green = 0
    yellow = 0
    brown = 0
    dark = 0
    pale = 0
    red_brown = 0

    for r, g, b in pixels:

        # Green
        if (
            g > r * 1.05
            and g > b * 1.05
            and g > 50
        ):
            green += 1

        # Yellow
        if (
            r > 120
            and g > 110
            and b < 100
            and r > b * 1.4
        ):
            yellow += 1

        # Brown
        if (
            r > 70
            and r > g * 1.15
            and g > b * 1.15
            and b < 100
        ):
            brown += 1

        # Dark
        if (
            r < 60
            and g < 60
            and b < 60
        ):
            dark += 1

        # Pale / white
        if (
            r > 190
            and g > 190
            and b > 190
        ):
            pale += 1

        # Red/brown damage
        if (
            r > 100
            and r > g * 1.3
            and r > b * 1.3
        ):
            red_brown += 1

    green_ratio = green / total
    yellow_ratio = yellow / total
    brown_ratio = brown / total
    dark_ratio = dark / total
    pale_ratio = pale / total
    red_ratio = red_brown / total

    visual_findings = []

    if yellow_ratio > 0.08:

        visual_findings.append(
            "Visible yellowing detected"
        )

    if brown_ratio > 0.06:

        visual_findings.append(
            "Brown/discoloured areas detected"
        )

    if dark_ratio > 0.12:

        visual_findings.append(
            "Dark areas detected"
        )

    if pale_ratio > 0.25:

        visual_findings.append(
            "Large pale/light areas detected"
        )

    if red_ratio > 0.08:

        visual_findings.append(
            "Reddish/brown colour variation detected"
        )

    if green_ratio > 0.45:

        visual_findings.append(
            "Healthy-looking green foliage is prominent"
        )

    return {
        "green": green_ratio,
        "yellow": yellow_ratio,
        "brown": brown_ratio,
        "dark": dark_ratio,
        "pale": pale_ratio,
        "red": red_ratio,
        "findings": visual_findings,
    }


# ============================================================
# VISUAL DIAGNOSIS
# ============================================================

def image_based_diagnosis(visual):

    findings = []

    visual_score = 100

    yellow = visual["yellow"]
    brown = visual["brown"]
    dark = visual["dark"]
    pale = visual["pale"]
    green = visual["green"]

    if yellow > 0.08:

        visual_score -= 18

        findings.append(
            "The image shows noticeable yellowing, which can be associated "
            "with nutrient imbalance, watering stress or natural leaf ageing."
        )

    if brown > 0.06:

        visual_score -= 20

        findings.append(
            "Brown/discoloured regions are visible and may indicate "
            "leaf stress, physical damage or disease-related spotting."
        )

    if dark > 0.12:

        visual_score -= 15

        findings.append(
            "A relatively high amount of dark area is visible in the image."
        )

    if pale > 0.25:

        visual_score -= 10

        findings.append(
            "The image contains substantial pale areas, which can occur "
            "with lighting effects, chlorosis or stressed foliage."
        )

    if green > 0.45:

        visual_score += 5

        findings.append(
            "A substantial amount of green foliage is visible."
        )

    visual_score = max(
        30,
        min(100, visual_score)
    )

    if (
        yellow > 0.08
        and brown > 0.06
    ):

        primary = (
            "Possible leaf stress involving yellowing and "
            "discolouration"
        )

    elif brown > 0.08:

        primary = (
            "Possible leaf-spot or physical-stress pattern"
        )

    elif yellow > 0.10:

        primary = (
            "Possible yellowing/chlorosis or watering-related stress"
        )

    elif dark > 0.15:

        primary = (
            "Possible dark-spot or damaged-leaf pattern"
        )

    elif green > 0.45:

        primary = (
            "Mostly healthy-looking foliage with no strong "
            "visual stress pattern"
        )

    else:

        primary = (
            "Possible mild plant stress; clearer leaf imagery "
            "may improve the assessment"
        )

    return visual_score, primary, findings


# ============================================================
# COMPLETE DIAGNOSIS
# ============================================================

def generate_diagnosis(
    visual,
    symptoms,
    category,
    plant,
    temperature,
    humidity,
    rainfall,
    wind,
    soil,
    soil_moisture,
    soil_ph,
    sunlight,
    aqi
):

    visual_score, visual_primary, visual_findings = (
        image_based_diagnosis(visual)
    )

    # --------------------------------------------------------
    # CONTEXT / SYMPTOM SCORE
    # --------------------------------------------------------

    context_score = 100

    context_findings = []

    # Symptoms only have 40% influence.

    if "🟡 Yellow leaves" in symptoms:

        context_score -= 10

        context_findings.append(
            "Yellowing was also selected as an observed symptom."
        )

    if "🟤 Brown spots" in symptoms:

        context_score -= 12

        context_findings.append(
            "Brown spots were selected as an observed symptom."
        )

    if "⚪ White powder" in symptoms:

        context_score -= 15

        context_findings.append(
            "White powder-like growth was selected as a symptom."
        )

    if "🥀 Wilting" in symptoms:

        context_score -= 12

        context_findings.append(
            "Wilting was selected as an observed symptom."
        )

    if "🕳️ Holes in leaves" in symptoms:

        context_score -= 10

        context_findings.append(
            "Leaf holes may indicate pest activity."
        )

    if "🌀 Curled leaves" in symptoms:

        context_score -= 8

        context_findings.append(
            "Leaf curling can occur with pests, heat or watering stress."
        )

    if "⚫ Black spots" in symptoms:

        context_score -= 12

        context_findings.append(
            "Black spots may be associated with leaf damage or disease."
        )

    if "📉 Stunted growth" in symptoms:

        context_score -= 8

        context_findings.append(
            "Stunted growth may indicate environmental or nutritional stress."
        )

    # --------------------------------------------------------
    # ENVIRONMENT
    # --------------------------------------------------------

    if temperature > 35:

        context_score -= 6

        context_findings.append(
            "High temperature may increase heat stress."
        )

    if temperature < 10:

        context_score -= 5

        context_findings.append(
            "Low temperature may slow plant growth."
        )

    if humidity > 85:

        context_score -= 5

        context_findings.append(
            "Very high humidity can increase fungal risk."
        )

    if humidity < 25:

        context_score -= 4

        context_findings.append(
            "Very dry air can increase moisture loss."
        )

    if rainfall > 50:

        context_score -= 4

        context_findings.append(
            "Recent rainfall may increase moisture-related stress."
        )

    if wind > 35:

        context_score -= 3

        context_findings.append(
            "Strong winds can increase physical and moisture stress."
        )

    if soil_moisture > 85:

        context_score -= 6

        context_findings.append(
            "Very wet soil may increase root and fungal problems."
        )

    if soil_moisture < 20:

        context_score -= 6

        context_findings.append(
            "Very dry soil may contribute to water stress."
        )

    if soil_ph < 5:

        context_score -= 4

        context_findings.append(
            "Strongly acidic soil can affect nutrient availability."
        )

    if soil_ph > 8:

        context_score -= 4

        context_findings.append(
            "Highly alkaline soil can affect nutrient availability."
        )

    if sunlight < 3:

        context_score -= 4

        context_findings.append(
            "Low sunlight can reduce plant growth."
        )

    if aqi > 200:

        context_score -= 3

        context_findings.append(
            "Poor air quality may contribute to environmental stress."
        )

    context_score = max(
        30,
        min(100, context_score)
    )

    # --------------------------------------------------------
    # 60 : 40 FUSION
    # --------------------------------------------------------

    final_score = (
        visual_score * 0.60
        +
        context_score * 0.40
    )

    final_score = round(final_score)

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if final_score >= 85:

        status = "🟢 Low Risk"

    elif final_score >= 70:

        status = "🟡 Mild Stress"

    elif final_score >= 50:

        status = "🟠 Needs Attention"

    else:

        status = "🔴 High Attention"

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = 65

    if len(visual["findings"]) >= 2:
        confidence += 8

    if len(symptoms) >= 2:
        confidence += 5

    if visual["green"] > 0.45:
        confidence += 5

    confidence = min(
        92,
        confidence
    )

    # --------------------------------------------------------
    # SOLUTIONS
    # --------------------------------------------------------

    solutions = []

    solutions.append(
        "Check the plant and its surrounding leaves carefully for the same visible pattern."
    )

    if visual["yellow"] > 0.08:

        solutions.append(
            "Check the soil before watering. If the soil is already wet, allow the "
            "root zone to dry appropriately instead of adding more water."
        )

    elif visual["brown"] > 0.06:

        solutions.append(
            "Remove severely damaged leaves with clean tools and keep affected "
            "foliage from touching healthy plants."
        )

    elif visual["dark"] > 0.12:

        solutions.append(
            "Inspect the dark areas closely for spots, insects or physical damage."
        )

    else:

        solutions.append(
            "Continue normal care while monitoring new leaves for changes."
        )

    solutions.append(
        "Check that the plant is receiving suitable sunlight for its species."
    )

    solutions.append(
        "Inspect the underside of leaves and stems for insects or eggs."
    )

    solutions.append(
        "Improve airflow around the plant and avoid unnecessary wetting of foliage."
    )

    solutions.append(
        "Monitor the plant for the next few days and compare new growth with "
        "the affected leaves."
    )

    # Category-specific advice

    if category == "🚜 Farming Plants":

        solutions.append(
            "Inspect nearby crop plants because pests or disease can spread through a field."
        )

    elif category == "🏠 Home Plants":

        solutions.append(
            "Check that the pot has drainage holes and that excess water is not collecting below it."
        )

    elif category == "🦋 Exotic Plants":

        solutions.append(
            "Compare the plant's temperature, humidity and light conditions with "
            "the requirements of its particular species."
        )

    elif category == "🍎 Fruit Plants":

        solutions.append(
            "Check both leaves and developing fruit for similar damage."
        )

    elif category == "🥬 Vegetable Plants":

        solutions.append(
            "Inspect young leaves and stems regularly because early pest damage "
            "can spread quickly."
        )

    elif category == "🌸 Flowering Plants":

        solutions.append(
            "Remove severely damaged flowers and monitor new buds for recurring symptoms."
        )

    # --------------------------------------------------------
    # PREVENTION
    # --------------------------------------------------------

    prevention = [
        "Water according to the plant's needs rather than on a fixed schedule alone.",
        "Give the plant appropriate sunlight.",
        "Keep enough space between plants for good airflow.",
        "Remove dead or severely diseased plant material.",
        "Inspect leaves regularly for early signs of pests.",
        "Keep gardening tools clean.",
        "Use suitable drainage for the plant.",
    ]

    # --------------------------------------------------------
    # DIAGNOSIS TEXT
    # --------------------------------------------------------

    if visual_primary.startswith("Mostly healthy"):

        diagnosis = (
            f"The image looks relatively healthy overall. "
            f"The selected symptoms and environmental conditions should still "
            f"be monitored because early plant stress can be subtle."
        )

    else:

        diagnosis = (
            f"The strongest visual pattern is: {visual_primary}. "
            f"The environmental information and selected symptoms were used "
            f"as supporting evidence."
        )

    return {
        "score": final_score,
        "visual_score": visual_score,
        "context_score": context_score,
        "status": status,
        "confidence": confidence,
        "diagnosis": diagnosis,
        "visual_findings": visual_findings,
        "context_findings": context_findings,
        "solutions": solutions,
        "prevention": prevention,
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ App Settings")

language = st.sidebar.selectbox(
    "🌍 Language",
    list(LANGUAGES.keys())
)

T = LANGUAGES[language]

st.sidebar.divider()

st.sidebar.subheader("📍 Your Plant's Location")

location_input = st.sidebar.text_input(
    "Search for a place",
    placeholder="e.g. Bengaluru, Mysuru, Delhi..."
)

if location_input:

    location = get_location_data(
        location_input
    )

    if location:

        st.session_state["location"] = location

        st.sidebar.success(
            f"📍 {location['name']}, {location['country']}"
        )

        st.sidebar.caption(
            f"{location['latitude']:.4f}, "
            f"{location['longitude']:.4f}"
        )

    else:

        st.sidebar.error(
            "Couldn't find that place. Try a nearby city or town."
        )

else:

    if "location" not in st.session_state:

        st.session_state["location"] = {
            "name": "Bengaluru",
            "country": "India",
            "latitude": 12.9716,
            "longitude": 77.5946
        }

    st.sidebar.caption(
        "Enter your farm, home or garden location above."
    )


location = st.session_state["location"]

st.sidebar.divider()

st.sidebar.subheader("🌿 Plant Search")

plant_search = st.sidebar.text_input(
    "Search plant name",
    placeholder="Try: mango, rose, tomato..."
)

if plant_search:

    matching_plants = [
        plant
        for plant in ALL_PLANTS
        if plant_search.lower() in plant.lower()
    ]

    if matching_plants:

        selected_plant = st.sidebar.selectbox(
            "Matching plants",
            matching_plants
        )

        selected_category = next(
            category
            for category, plants in PLANT_CATEGORIES.items()
            if selected_plant in plants
        )

    else:

        st.sidebar.warning(
            "No matching plant found."
        )

        selected_category = st.sidebar.selectbox(
            "Plant Category",
            list(PLANT_CATEGORIES.keys())
        )

        selected_plant = st.sidebar.selectbox(
            "Plant",
            PLANT_CATEGORIES[selected_category]
        )

else:

    selected_category = st.sidebar.selectbox(
        "Plant Category",
        list(PLANT_CATEGORIES.keys())
    )

    selected_plant = st.sidebar.selectbox(
        "Plant",
        PLANT_CATEGORIES[selected_category]
    )


# ============================================================
# LOCATION-BASED ENVIRONMENT
# ============================================================

environment = get_environment_data(
    location["latitude"],
    location["longitude"]
)

default_temperature = float(
    environment["temperature"]
)

default_humidity = int(
    environment["humidity"]
)

default_rainfall = float(
    environment["rainfall"]
)

default_wind = float(
    environment["wind"]
)

default_weather = weather_from_code(
    environment["weather_code"]
)


# ============================================================
# MAIN HEADER
# ============================================================

st.title(T["title"])

st.subheader(T["subtitle"])

st.write(
    "📷 Upload a photo. Tell us a little about your plant. "
    "We'll combine the visual information with your plant's environment "
    "to create an easy-to-understand assessment."
)

st.divider()


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.header("📷 1. Show Us Your Plant")

uploaded_file = st.file_uploader(
    "Upload a clear photo of the affected leaf or plant",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    plant_result = identify_plant_with_plantnet(uploaded_file)

    if plant_result and "error" not in plant_result:
        st.success(
            f"🌱 Plant identified: {plant_result['common_name']} "
            f"({plant_result['name']}) — "
            f"{plant_result['score']}% match"
        )
    elif plant_result and "error" in plant_result:
        st.warning("Plant identification could not be completed.")

    image_col, details_col = st.columns([1, 2])

    with image_col:

        st.image(
            image,
            caption="Your plant photo",
            width=260
        )

    with details_col:

        st.success(
            "✅ Plant image uploaded!"
        )

        st.markdown(
            f"""
            **Plant:** {selected_plant}

            **Category:** {selected_category}

            **Location:** {location['name']}, {location['country']}
            """
        )

        st.caption(
            "The image is the primary source of the visual assessment."
        )

else:

    st.info(
        "📸 A clear photo of the affected leaf gives the app the best chance "
        "of spotting visible patterns."
    )


st.divider()


# ============================================================
# ENVIRONMENT MODE
# ============================================================

st.header("🌦️ 2. Growing Conditions")

environment_mode = st.radio(
    "How much information would you like to provide?",
    [
        "😊 Easy",
        "🔬 Detailed"
    ],
    horizontal=True
)


# ============================================================
# EASY ENVIRONMENT
# ============================================================

if environment_mode == "😊 Easy":

    st.caption(
        "Don't worry about technical measurements. "
        "The app automatically uses your location to fill in useful information."
    )

    easy1, easy2, easy3 = st.columns(3)

    with easy1:

        st.metric(
            "📍 Location",
            location["name"]
        )

    with easy2:

        st.metric(
            "🌡️ Temperature",
            f"{default_temperature:.1f} °C"
        )

    with easy3:

        st.metric(
            "💧 Air Humidity",
            f"{default_humidity}%"
        )

    easy_weather = st.selectbox(
        "🌤️ What does the weather feel like?",
        [
            default_weather,
            "☀️ Sunny",
            "⛅ Cloudy",
            "🌧️ Rainy",
            "🥵 Very Hot",
            "🥶 Cold",
        ]
    )

    watering = st.selectbox(
        "💦 How does the soil usually feel?",
        [
            "Not sure",
            "Dry",
            "Slightly moist",
            "Moist",
            "Very wet"
        ]
    )

    sunlight_easy = st.selectbox(
        "☀️ How much sunlight does the plant get?",
        [
            "Not sure",
            "Very little",
            "A few hours",
            "Most of the day",
            "Strong direct sunlight"
        ]
    )

    aqi_easy = "Automatically estimated from location"

    soil_moisture = {
        "Not sure": 50,
        "Dry": 20,
        "Slightly moist": 40,
        "Moist": 60,
        "Very wet": 85
    }[watering]

    sunlight_map = {
        "Not sure": 6,
        "Very little": 2,
        "A few hours": 4,
        "Most of the day": 7,
        "Strong direct sunlight": 9
    }

    sunlight = sunlight_map[
        sunlight_easy
    ]

    soil_ph = 6.5

    rainfall = default_rainfall

    wind = default_wind

    aqi = 75


# ============================================================
# DETAILED ENVIRONMENT
# ============================================================

else:

    st.caption(
        "Detailed mode lets experienced farmers or gardeners adjust "
        "the automatically detected values."
    )

    d1, d2, d3 = st.columns(3)

    with d1:

        temperature = st.number_input(
            "🌡️ Temperature (°C)",
            min_value=-10.0,
            max_value=60.0,
            value=default_temperature,
            step=0.5
        )

        humidity = st.slider(
            "💧 Humidity (%)",
            0,
            100,
            default_humidity
        )

    with d2:

        rainfall = st.number_input(
            "🌧️ Recent rainfall (mm)",
            min_value=0.0,
            max_value=1000.0,
            value=default_rainfall,
            step=1.0
        )

        wind = st.slider(
            "💨 Wind speed (km/h)",
            0,
            150,
            int(default_wind)
        )

    with d3:

        aqi = st.number_input(
            "🌫️ Air Quality Index",
            min_value=0,
            max_value=500,
            value=75
        )

        sunlight = st.slider(
            "☀️ Sunlight (hours/day)",
            0.0,
            16.0,
            6.0,
            step=0.5
        )

    soil = st.selectbox(
        "🌱 Soil type",
        [
            "Loamy",
            "Clay",
            "Sandy",
            "Black Soil",
            "Red Soil",
            "Alluvial Soil",
            "Laterite Soil"
        ]
    )

    soil_moisture = st.slider(
        "💦 Soil moisture (%)",
        0,
        100,
        50
    )

    soil_ph = st.slider(
        "🧪 Soil pH",
        3.0,
        10.0,
        6.5,
        step=0.1
    )


# ============================================================
# SYMPTOMS
# ============================================================

st.divider()

st.header("🩺 3. Anything You Notice?")

st.caption(
    "These are supporting clues only. Don't worry if you're unsure — "
    "the photo carries more weight in the assessment."
)

symptoms = st.multiselect(
    "Select anything that looks unusual:",
    SYMPTOMS
)


# ============================================================
# DIAGNOSIS BUTTON
# ============================================================

st.divider()

diagnose = st.button(
    "🔍 Analyze My Plant",
    use_container_width=True
)


if diagnose:

    if not uploaded_file:

        st.error(
            "📷 Please upload a plant photo first."
        )

        st.stop()

    # --------------------------------------------------------
    # EASY MODE DEFAULTS
    # --------------------------------------------------------

    if environment_mode == "😊 Easy":

        temperature = default_temperature

        humidity = default_humidity

        soil = "Not specified"

    # --------------------------------------------------------
    # IMAGE ANALYSIS
    # --------------------------------------------------------

    visual = analyze_leaf_image(
        image
    )

    # --------------------------------------------------------
    # DIAGNOSIS
    # --------------------------------------------------------

    result = generate_diagnosis(
        visual=visual,
        symptoms=symptoms,
        category=selected_category,
        plant=selected_plant,
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall,
        wind=wind,
        soil=soil,
        soil_moisture=soil_moisture,
        soil_ph=soil_ph,
        sunlight=sunlight,
        aqi=aqi
    )

    st.session_state["diagnosis"] = result


# ============================================================
# RESULTS
# ============================================================

if "diagnosis" in st.session_state:

    result = st.session_state["diagnosis"]

    st.divider()

    st.header("🩺 4. Your Plant Health Report")

    # --------------------------------------------------------
    # TOP STATUS CARDS
    # --------------------------------------------------------

    card1, card2, card3, card4 = st.columns(4)

    with card1:

        st.metric(
            "🌱 Health Score",
            f"{result['score']}/100"
        )

    with card2:

        st.metric(
            "📷 Visual Score",
            f"{result['visual_score']}/100"
        )

    with card3:

        st.metric(
            "🌦️ Context Score",
            f"{result['context_score']}/100"
        )

    with card4:

        st.metric(
            "🎯 Confidence",
            f"{result['confidence']}%"
        )

    st.progress(
        result["score"] / 100
    )

    # --------------------------------------------------------
    # DIAGNOSIS FLOW
    # --------------------------------------------------------

    st.subheader("🔄 How Phantom Crop Doctor Reached This Result")

    flow1, flow2, flow3, flow4, flow5 = st.columns(5)

    with flow1:

        st.info(
            "📷\n\n"
            "**PHOTO**\n\n"
            "Visual leaf patterns"
        )

    with flow2:

        st.info(
            "🌿\n\n"
            "**PLANT**\n\n"
            f"{selected_plant}"
        )

    with flow3:

        st.info(
            "🌦️\n\n"
            "**ENVIRONMENT**\n\n"
            f"{location['name']}"
        )

    with flow4:

        st.info(
            "🩺\n\n"
            "**SYMPTOMS**\n\n"
            f"{len(symptoms)} selected"
        )

    with flow5:

        st.success(
            "🌱\n\n"
            "**RESULT**\n\n"
            f"{result['status']}"
        )

    # --------------------------------------------------------
    # WEIGHT VISUALIZATION
    # --------------------------------------------------------

    st.subheader("⚖️ Assessment Balance")

    st.write(
        "The prototype deliberately gives the uploaded image more influence "
        "than manually selected symptoms."
    )

    st.progress(
        0.60
    )

    st.write(
        "📷 **Visual image assessment — 60%**"
    )

    st.progress(
        0.40
    )

    st.write(
        "🌦️ **Environment + symptoms + plant context — 40%**"
    )

    # --------------------------------------------------------
    # MAIN DIAGNOSIS
    # --------------------------------------------------------

    st.subheader("🔬 What We Found")

    st.success(
        result["diagnosis"]
    )

    # --------------------------------------------------------
    # VISUAL FINDINGS
    # --------------------------------------------------------

    st.subheader("📷 What the Photo Shows")

    if result["visual_findings"]:

        for finding in result["visual_findings"]:

            st.write(
                f"🔎 {finding}"
            )

    else:

        st.write(
            "No strong visual abnormality pattern was detected."
        )

    # --------------------------------------------------------
    # SUPPORTING FINDINGS
    # --------------------------------------------------------

    st.subheader("🌦️ Supporting Information")

    if result["context_findings"]:

        for finding in result["context_findings"]:

            st.write(
                f"• {finding}"
            )

    else:

        st.write(
            "The selected environmental information did not add "
            "a strong additional risk signal."
        )

    # --------------------------------------------------------
    # ENVIRONMENT DASHBOARD
    # --------------------------------------------------------

    st.subheader("🌍 Your Plant's Environment")

    environment_table = {
        "Location": [
            f"{location['name']}, {location['country']}"
        ],
        "Temperature": [
            f"{temperature:.1f} °C"
        ],
        "Humidity": [
            f"{humidity}%"
        ],
        "Weather": [
            default_weather
        ],
        "Sunlight": [
            f"{sunlight} hours/day"
        ],
        "Rainfall": [
            f"{rainfall:.1f} mm"
        ],
        "Wind": [
            f"{wind:.1f} km/h"
        ],
        "Air Quality": [
            f"{aqi}"
        ],
        "Soil": [
            soil
        ],
        "Soil Moisture": [
            f"{soil_moisture}%"
        ],
        "Soil pH": [
            f"{soil_ph:.1f}"
        ],
    }

    st.table(
        environment_table
    )

    # --------------------------------------------------------
    # STEP BY STEP SOLUTION
    # --------------------------------------------------------

    st.subheader("🛠️ What Should You Do?")

    for index, step in enumerate(
        result["solutions"],
        start=1
    ):

        step_col1, step_col2 = st.columns(
            [1, 8]
        )

        with step_col1:

            st.markdown(
                f"### {index}"
            )

        with step_col2:

            st.write(
                step
            )

        st.divider()

    # --------------------------------------------------------
    # PREVENTION
    # --------------------------------------------------------

    st.subheader("🛡️ Keep It Healthy")

    prevention_cols = st.columns(2)

    for index, tip in enumerate(
        result["prevention"]
    ):

        with prevention_cols[
            index % 2
        ]:

            st.success(
                f"🌱 {tip}"
            )

    # --------------------------------------------------------
    # FINAL VISUAL SUMMARY
    # --------------------------------------------------------

    st.subheader("📊 Complete Assessment")

    summary_col1, summary_col2 = st.columns(
        [1, 1]
    )

    with summary_col1:

        st.markdown(
            f"""
            ### 🌱 Plant

            **{selected_plant}**

            **Category:** {selected_category}

            **Location:** {location['name']}

            **Overall Status**

            ## {result['status']}
            """
        )

    with summary_col2:

        st.markdown(
            "### 🧠 Assessment Breakdown"
        )

        st.write(
            f"📷 **Photo analysis:** {result['visual_score']}/100"
        )

        st.progress(
            result["visual_score"] / 100
        )

        st.write(
            f"🌦️ **Supporting information:** {result['context_score']}/100"
        )

        st.progress(
            result["context_score"] / 100
        )

    st.divider()

    # --------------------------------------------------------
    # FINAL FLOW
    # --------------------------------------------------------

    st.subheader("🌱 Your Plant's Journey")

    journey = [
        ("📷", "Photo", "Visual patterns detected"),
        ("🌿", "Plant", selected_plant),
        ("📍", "Location", location["name"]),
        ("🌦️", "Environment", "Conditions evaluated"),
        ("🧠", "Assessment", "60 : 40 visual/context fusion"),
        ("🛠️", "Action", "Step-by-step care plan"),
    ]

    for icon, title, description in journey:

        j1, j2, j3 = st.columns(
            [1, 2, 6]
        )

        with j1:

            st.markdown(
                f"## {icon}"
            )

        with j2:

            st.markdown(
                f"**{title}**"
            )

        with j3:

            st.write(
                description
            )

    st.divider()

    st.caption(
        "⚠️ Phantom Symptom Crop Doctor is a prototype plant-health assistant. "
        "Its current visual analysis uses image characteristics rather than a "
        "trained disease-classification model, so results should be treated "
        "as preliminary guidance."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌱 Phantom Symptom Crop Doctor • "
    "Making plant health easier for everyone"
)