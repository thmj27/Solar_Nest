"""Sizing engine. All formulas are here so they are easy to explain.

1. Appliance energy (kWh/day) = quantity x watts x hours / 1000
2. Daily demand = sum of appliances x average occupancy %
3. Solar kW needed = demand / (peak sun hours x performance ratio)
   (performance ratio ~0.75 covers heat, dust, wiring and inverter losses)
4. Roof limit = roof area / m2 per kW (about 10 m2 per kW)
5. Battery kWh = demand x night share x backup days / (depth of discharge x efficiency)
6. Cost = (solar kW x price/kW + battery kWh x price/kWh) x (1 + balance-of-system %)
7. Savings/month = energy solar actually supplies x grid tariff x 30
8. CO2 saved/year = solar energy used x grid emission factor
All of these are ESTIMATES for planning, not an engineering design."""
import math

# Average peak sun hours per day (approximate, planning-level values)
STATES = {
    "Andhra Pradesh": (5.6, ["Visakhapatnam", "Vijayawada", "Tirupati", "Araku Valley"]),
    "Kerala": (4.9, ["Munnar", "Wayanad", "Kochi", "Thekkady"]),
    "Karnataka": (5.5, ["Coorg", "Chikmagalur", "Hampi", "Gokarna"]),
    "Tamil Nadu": (5.5, ["Ooty", "Kodaikanal", "Pondicherry", "Coimbatore"]),
    "Goa": (5.3, ["Panaji", "Palolem", "Candolim"]),
    "Rajasthan": (6.2, ["Jaisalmer", "Udaipur", "Jaipur", "Pushkar"]),
    "Himachal Pradesh": (4.8, ["Manali", "Kasol", "Dharamshala", "Shimla"]),
    "Uttarakhand": (4.9, ["Rishikesh", "Mussoorie", "Nainital", "Auli"]),
    "Meghalaya": (4.2, ["Shillong", "Cherrapunji", "Dawki"]),
    "Sikkim": (4.3, ["Gangtok", "Pelling", "Lachung"]),
    "Maharashtra": (5.4, ["Lonavala", "Mahabaleshwar", "Alibag", "Nashik"]),
    "Odisha": (5.4, ["Puri", "Gopalpur", "Koraput"]),
}
MONTH_FACTORS = [0.95, 1.0, 1.05, 1.05, 1.0, 0.8, 0.75, 0.8, 0.85, 0.9, 0.9, 0.9]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DEFAULT_SETTINGS = {
    "performance_ratio": 0.75, "depth_of_discharge": 0.8, "battery_efficiency": 0.9,
    "roof_m2_per_kw": 10, "cost_per_kw": 55000, "cost_per_kwh_battery": 18000,
    "bos_percent": 15, "grid_tariff": 8, "co2_kg_per_kwh": 0.82,
}


def validate(inp):
    """Return a list of friendly error messages (empty list = OK)."""
    errs = []
    if inp.get("state") not in STATES or inp.get("city") not in STATES.get(inp.get("state"), (0, []))[1]:
        errs.append("Please choose a state and city.")
    try:
        if not 1 <= int(inp["rooms"]) <= 200: errs.append("Rooms must be between 1 and 200.")
        if not 1 <= int(inp["guests"]) <= 1000: errs.append("Guests must be between 1 and 1000.")
        if float(inp["roof_area"]) < 5: errs.append("Roof area must be at least 5 m².")
        if float(inp["budget"]) < 0: errs.append("Budget cannot be negative.")
        if not 10 <= float(inp["occupancy"]) <= 100: errs.append("Occupancy must be 10-100%.")
        if not 0 <= float(inp["night_share"]) <= 100: errs.append("Night usage must be 0-100%.")
        if not 0 <= float(inp["backup_days"]) <= 3: errs.append("Backup days must be 0-3.")
    except (KeyError, ValueError, TypeError):
        errs.append("Some details are missing or not numbers.")
    apps = inp.get("appliances") or []
    if not apps: errs.append("Select at least one appliance.")
    for a in apps:
        try:
            if not (0 < int(a["qty"]) <= 500): errs.append(f"{a['name']}: quantity must be 1-500.")
            if not (0 < float(a["watts"]) <= 10000): errs.append(f"{a['name']}: watts must be 1-10000.")
            if not (0 < float(a["hours"]) <= 24): errs.append(f"{a['name']}: hours must be 0-24.")
        except (KeyError, ValueError, TypeError):
            errs.append("An appliance has a missing or invalid value.")
    return errs


def _round_up(x, step): return math.ceil(x / step - 1e-9) * step


def compute(inp, s=None):
    s = {**DEFAULT_SETTINGS, **(s or {})}
    psh = STATES[inp["state"]][0]
    occ = float(inp["occupancy"]) / 100
    night = float(inp["night_share"]) / 100
    breakdown = []
    for a in inp["appliances"]:
        kwh = int(a["qty"]) * float(a["watts"]) * float(a["hours"]) / 1000 * occ
        breakdown.append({"name": a["name"], "kwh": round(kwh, 2)})
    demand = sum(b["kwh"] for b in breakdown)
    daily_yield = psh * s["performance_ratio"]            # kWh per kW per day
    needed_kw = demand / daily_yield
    max_kw = float(inp["roof_area"]) / s["roof_m2_per_kw"]
    solar_kw = max(1.0, _round_up(min(needed_kw, max_kw), 0.5))
    if solar_kw > max_kw + 0.01 and needed_kw > max_kw: solar_kw = max(0.5, math.floor(max_kw * 2) / 2)
    battery = _round_up(demand * night * float(inp["backup_days"]) / (s["depth_of_discharge"] * s["battery_efficiency"]), 0.5) if float(inp["backup_days"]) > 0 else 0
    cost = (solar_kw * s["cost_per_kw"] + battery * s["cost_per_kwh_battery"]) * (1 + s["bos_percent"] / 100)
    generated = solar_kw * daily_yield
    used = min(demand, generated)
    coverage = used / demand if demand else 0
    monthly_saving = used * s["grid_tariff"] * 30
    annual_saving = sum(monthly_saving * f for f in MONTH_FACTORS) * 1.0
    payback = cost / annual_saving if annual_saving else 0
    co2_t = used * 365 * s["co2_kg_per_kwh"] / 1000

    # hourly profile: demand split between day (6-18h) and night; solar is a bell curve 6-18h
    day_h = [h for h in range(24) if 6 <= h < 18]
    bell = [math.sin(math.pi * (h - 6 + 0.5) / 12) for h in day_h]
    solar_h = [round(generated * bell[day_h.index(h)] / sum(bell), 2) if h in day_h else 0 for h in range(24)]
    demand_h = [round(demand * ((1 - night) / 12 if h in day_h else night / 12), 2) for h in range(24)]

    warnings = []
    if needed_kw > max_kw: warnings.append(f"Your roof fits about {max_kw:.1f} kW but your demand needs about {needed_kw:.1f} kW. The plan is limited by roof space, so solar covers {coverage*100:.0f}% of your demand. Consider reducing heavy appliances (AC, water heaters) or adding ground-mounted panels.")
    if float(inp["budget"]) and cost > float(inp["budget"]): warnings.append(f"The estimated cost (₹{cost:,.0f}) is above your budget (₹{float(inp['budget']):,.0f}). You could reduce backup days, cut high-use appliances, or phase the installation.")
    if not float(inp["backup_days"]): warnings.append("No battery included: the property will rely on the grid at night.")
    top = max(breakdown, key=lambda b: b["kwh"])
    reasons = [
        f"Energy demand: about {demand:.1f} kWh/day, mostly from {top['name']} ({top['kwh']:.1f} kWh).",
        f"Solar availability: {inp['city']}, {inp['state']} gets roughly {psh} peak sun hours/day, so each kW of panels yields about {daily_yield:.1f} kWh/day.",
        f"Roof space: {inp['roof_area']} m² can host up to about {max_kw:.1f} kW.",
        f"Battery backup: {float(inp['night_share']):.0f}% of your use is at night; {battery:g} kWh covers {inp['backup_days']} day(s) of that safely (80% usable).",
        f"Budget: estimated ₹{cost:,.0f}" + (f" against your ₹{float(inp['budget']):,.0f} budget." if float(inp['budget']) else "."),
    ]
    rec = (f"Based on your estimated daily energy consumption of {demand:.1f} kWh, available roof area, location and budget, "
           f"we recommend approximately a {solar_kw:g} kW solar system with a {battery:g} kWh battery. "
           f"This is an estimate for planning; get a site survey and installer quote before buying.")
    return {"demand": round(demand, 2), "solar_kw": solar_kw, "battery_kwh": battery, "cost": round(cost),
            "monthly_saving": round(monthly_saving), "annual_saving": round(annual_saving), "payback_years": round(payback, 1),
            "co2_tonnes": round(co2_t, 2), "coverage": round(coverage * 100), "psh": psh, "needed_kw": round(needed_kw, 2),
            "max_kw": round(max_kw, 2), "breakdown": breakdown, "hourly_demand": demand_h, "hourly_solar": solar_h,
            "monthly": [round(monthly_saving * f) for f in MONTH_FACTORS], "months": MONTHS,
            "warnings": warnings, "reasons": reasons, "recommendation": rec}
