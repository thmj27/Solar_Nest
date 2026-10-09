# ☀ SolarNest — Eco-Tourism Homestay Microgrid Sizing Planner (PS09)

**From your energy needs to your solar plan — made simple.**

This document explains the whole project in plain language. You do not need to know programming to understand it.

---

## 1. What is this project?

SolarNest is a **website** that helps owners of homestays and small eco-resorts answer three questions:

1. How much electricity do we use every day?
2. How big should our **solar panel system** be (in kW)?
3. How big should our **battery** be (in kWh)?

The owner answers a few easy questions (location, property size, appliances, usage). The website then calculates a recommendation, shows the estimated **cost, monthly savings and CO₂ reduction**, draws charts, lets the owner **save the plan**, and lets them **print it as a PDF report**.

No real solar hardware is needed. Everything is done by software calculations.

> **Important:** All numbers are **estimates for planning**. A real installation always needs a site visit and a quote from a professional installer. The website says this on its pages.

---

## 2. Words you will see (simple glossary)

| Word | Simple meaning |
|---|---|
| **kW (kilowatt)** | The *power* of something. A 5 kW solar system is "big enough to produce 5 kW at its best". |
| **kWh (kilowatt-hour)** | An amount of *energy*. This is what appears on an electricity bill. A 1 kW heater running for 1 hour uses 1 kWh. |
| **Solar panel capacity** | How big the solar system is, in kW. |
| **Battery capacity** | How much energy the battery can store, in kWh. |
| **Peak sun hours** | How many hours per day the sun is strong enough to give full power. It differs by region (e.g. Rajasthan has more than Meghalaya). |
| **Performance ratio** | Real-life losses (heat, dust, wires, inverter). We assume the system delivers about 75% of the ideal. |
| **Depth of discharge (DoD)** | You should not drain a battery to zero. We assume only 80% of it is usable. |
| **Backup days** | How many days of night-time electricity the battery should cover. |
| **Grid tariff** | The price you pay per unit (kWh) of electricity from the electricity company. |
| **Occupancy** | How full your property usually is (e.g. 70% of the time). |

---

## 3. What the user experiences (the journey)

```
Home page → Sign Up / Login → "Your Solar Future Starts Here" → Let's Get Started
→ 1. Location → 2. Property → 3. Appliances → 4. Usage → 5. Solar needs
→ 6. Results dashboard → Save / Edit / Recalculate → Download report
```

**Pages in the website**

1. **Home page** — introduction, how it works, features, Get Started button.
2. **Sign Up** — name, email, password, confirm password. Nothing else.
3. **Login** — email and password.
4. **"Your Solar Future Starts Here"** — a welcome page with the *Let's Get Started* button.
5. **Planning wizard** — five steps with a progress bar:
   - *Location:* choose a state and city from dropdowns.
   - *Property:* homestay / eco-resort / other, rooms, guests, roof area, budget.
   - *Appliances:* tap cards for lights, fans, ACs, fridges, TVs, water heaters, others. Each has ready-made default values (quantity, watts, hours per day) that experts can change.
   - *Usage:* occupancy slider, evening/night usage slider, battery backup choice. Small "?" icons explain terms.
   - *Solar needs:* name your project and press Calculate.
6. **Results dashboard** — the recommendation, six information cards, three charts and a "why this size?" explanation.
7. **My Projects** — all saved plans as cards (View, Edit, Delete).
8. **Project details** — the full dashboard of one saved plan with the buttons *Edit Project*, *Recalculate*, *Download Report*.
9. **Report page** — a clean printable page; use *Print / Save as PDF*.
10. **Admin dashboard** — only for the administrator (see section 8).

---

## 4. How to run it on your computer (Windows)

You need **Python** installed (version 3.9 or newer).

1. Open the project folder (the one that contains `app.py`).
2. Click the folder address bar, type `cmd` and press Enter. A black window opens in that folder.
3. Create a private environment (only once):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install the one needed tool, Flask (only once):
   ```
   python -m pip install flask
   ```
5. Start the website:
   ```
   python app.py
   ```
6. Open a browser and go to **http://127.0.0.1:5000**
7. To stop it, go back to the black window and press **Ctrl + C**.

The next time, you only need steps 2, `venv\Scripts\activate`, 5 and 6.

**Admin login (built in):** `admin@solar.local` / `admin123`
(Change this password before showing the project to the public.)

### If something goes wrong

| Problem | Fix |
|---|---|
| `No module named 'flask'` | Run `python -m pip install flask` in the same window where you run the app. |
| Port 5000 already in use | Open `app.py`, change the last line to `app.run(debug=True, port=5001)`, and visit `127.0.0.1:5001`. |
| Charts are empty | You need internet the first time (the chart library loads online). |
| Page looks old after a change | Press **Ctrl + F5** in the browser. |
| Want to start fresh | Stop the app, delete the file `solar.db`, start again. |

---

## 5. What is inside the project folder (file by file)

```
solar-planner/
├── app.py            ← the "manager" of the website
├── calc.py           ← the "brain": all solar formulas
├── requirements.txt  ← list of tools needed (just Flask)
├── solar.db          ← the saved data (created automatically on first run)
├── README.md         ← this file
├── templates/        ← the page layouts (HTML)
│   ├── base.html        top menu + footer used by every page
│   ├── home.html        landing page
│   ├── auth.html        login and sign-up forms
│   ├── start.html       "Your Solar Future Starts Here"
│   ├── wizard.html      the wizard page shell
│   ├── project.html     saved project / results page
│   ├── _results.html    cards, warnings, recommendation, charts (reused)
│   ├── _inputs.html     property + appliance table (reused)
│   ├── projects.html    "My Projects"
│   ├── report.html      printable report
│   └── admin.html       admin dashboard
└── static/           ← design and behaviour of pages
    ├── style.css        colours, fonts, cards, animations
    └── wizard.js        makes the step-by-step wizard work
```

**What each technology does (in everyday words):**

| Technology | Role | Analogy |
|---|---|---|
| **HTML** | The structure of a page (headings, buttons, tables) | The walls and rooms of a building |
| **CSS** | How it looks (green theme, rounded cards, spacing) | Paint and decoration |
| **JavaScript** | Makes pages interactive (wizard steps, charts) | Electricity and switches |
| **Python** | The programming language of the "back office" | The staff who do the work |
| **Flask** | A Python tool that turns Python code into a website | The reception desk that receives requests and returns pages |
| **SQLite** | A simple database stored in one file (`solar.db`) | A filing cabinet |
| **Chart.js** | Draws the charts | A chart-drawing assistant |
| **Git/GitHub** | Saves versions of the code and shares it with the team | A shared, time-travelling folder |

### What `app.py` does
It is the traffic controller. It:
- creates the database tables the first time,
- handles **sign up, login, logout**,
- shows each page,
- receives the wizard answers, checks them, asks `calc.py` to calculate, and **saves the project**,
- handles **edit, recalculate, delete**,
- protects pages (you must log in; admin pages need admin rights),
- gathers the statistics for the admin page.

### What `calc.py` does
It contains **all the solar maths** in one place, with the formulas explained at the top of the file. It also contains the list of states and cities with their sunshine values, and the **checks** that reject bad inputs (negative numbers, absurd quantities, etc.).

---

## 6. How the calculation works (explained step by step)

All of this is in `calc.py`. The results change with every input — nothing is hard-coded.

1. **Energy per appliance per day (kWh)**
   `quantity × watts × hours per day ÷ 1000`
2. **Daily demand** = total of all appliances × occupancy %.
3. **Solar size needed (kW)** = daily demand ÷ (peak sun hours × 0.75)
4. **Roof limit (kW)** = roof area (m²) ÷ 10 (about 10 m² of roof per kW).
   The final solar size is the needed size, **but not more than the roof allows**. If the roof is too small, the website warns you.
5. **Battery size (kWh)** = daily demand × night share × backup days ÷ (0.8 usable × 0.9 efficiency)
6. **Cost (₹)** = (solar kW × ₹55,000 + battery kWh × ₹18,000) × 1.15
   (the 15% covers wiring, inverter, mounting and installation). The website warns you if the cost is above your budget.
7. **Monthly savings (₹)** = energy solar supplies per day × ₹8 per kWh × 30 days
8. **Payback (years)** = cost ÷ yearly savings
9. **CO₂ saved per year** = solar energy used per year × 0.82 kg per kWh

**Worked example** (Munnar, Kerala · 80 m² roof · 10 lights of 10 W for 6 h + 2 ACs of 1500 W for 6 h · 70% occupancy · 55% night use · 1 backup day):

- Lights 0.6 kWh + ACs 18 kWh = 18.6 kWh → × 70% = **13.0 kWh/day**
- Sun hours for Kerala = 4.9 → each kW gives 4.9 × 0.75 = 3.675 kWh/day
- Solar needed = 13.0 ÷ 3.675 = 3.5 kW → rounded up to **4 kW** (roof allows 8 kW, so it fits)
- Battery = 13.0 × 0.55 ÷ 0.72 = 9.9 → **10 kWh**
- Cost = (4 × 55,000 + 10 × 18,000) × 1.15 = **₹4,60,000**
- Savings = 13.0 × 8 × 30 ≈ **₹3,100 per month**

**Monthly savings chart:** the average is adjusted by a seasonal factor (more sun in March–May, less in monsoon June–August).
**Daily chart:** shows your electricity use hour by hour against the solar output, which follows a sun-shaped curve from 6 am to 6 pm.

### Where the settings come from
The prices, tariff, efficiency, etc. are stored in the database (table `settings`) and the **admin can change them** without touching code. After changing them, press **Recalculate** on a project to apply them.

---

## 7. The recommendation engine

It is a simple, honest rule-based approach (no AI/ML). It:
1. computes the numbers above,
2. writes a sentence such as *"we recommend approximately a 4 kW solar system with a 10 kWh battery"*,
3. lists **reasons** (energy demand, sunshine in your location, roof space, battery backup, budget),
4. adds **warnings** when needed:
   - roof too small for the demand,
   - cost above budget,
   - no battery selected.

---

## 8. Admin dashboard

Log in as admin to see:
- **Statistics:** total users, total projects, average system size, most common property type.
- **Calculation parameters:** edit and save (performance ratio, battery usable %, cost per kW, tariff, CO₂ factor, etc.).
- **Users** list, **Projects** list (with delete).
- **Appliance defaults, solar panel models and battery models** (view only in this version).

Normal users who try to open `/admin` get a "forbidden" error.

---

## 9. The database (the filing cabinet)

Stored in `solar.db`. Tables:

| Table | What it keeps |
|---|---|
| `users` | name, email, **scrambled (hashed) password**, admin flag |
| `projects` | project name, property type, state, city, solar kW, battery kWh, cost, plus the full answers and results |
| `appliances` | default appliance values shown in the wizard |
| `solar_panels` | sample panel models and prices |
| `batteries` | sample battery models and prices |
| `settings` | the adjustable calculation parameters |

Note: instead of separate Properties and Project_Appliances tables, each project stores its inputs and results together in one record. This keeps the code simple and easy to explain.

---

## 10. Safety and security features

- Passwords are **never stored as text** — only as hashed (scrambled) values.
- Login sessions keep users signed in; pages redirect to login when needed.
- Users can only open **their own** projects.
- Admin pages are only for admins.
- Database commands use **parameters**, which protects against SQL injection.
- All inputs are checked in the browser **and again on the server** (email format, password strength, quantities, hours, roof area, budget, and so on).

**Not included yet (be honest in your presentation):** CSRF protection, login-attempt limits, email verification, password reset, HTTPS. These would be added before a real public launch.

---

## 11. Known limitations

- Sunshine values are **state-level approximations**, not exact city data.
- The PDF is created through the browser's *Print → Save as PDF*, not a built-in PDF generator.
- Admin cannot yet edit users, appliances, panels or batteries (only parameters).
- Prices are typical assumed values and will differ from real market quotes.
- The website needs internet only for loading the chart library.

## 12. Ideas for future improvement

- Use real solar data (NASA POWER or PVGIS) for each city.
- Built-in PDF generator (e.g. ReportLab).
- Separate database tables for properties and project appliances.
- Admin editing for appliances, panels and batteries.
- Panel and battery model suggestions from the specification tables.
- Password reset by email, CSRF protection, deployment online.

---

## 13. Tips for explaining the project in your presentation

1. **Problem:** homestay owners do not know how big a solar system they need.
2. **Solution:** a guided website that turns simple answers into a solar plan.
3. **Demo:** sign up → wizard → results → save → report.
4. **Explain one calculation live** using the worked example in section 6.
5. **Show the admin panel** changing a price, then press *Recalculate* on a project to show the result updating.
6. **Be honest:** say these are estimates and mention the limitations in section 11.

---

*SolarNest — PS09 student project. Planning estimates only; always confirm with a professional site survey before buying equipment.*
