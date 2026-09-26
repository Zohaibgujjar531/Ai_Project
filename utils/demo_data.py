"""
Ready-to-use demo project so the app is fully explorable without a Groq API
key — useful for a hackathon demo, offline testing, or when the live API
call fails. Mirrors exactly the schema each agent normally returns, so the
same rendering code in app.py works for both live and demo data.
"""

DEMO_PROJECT_IDEA = "Build a solar-powered irrigation system for a 5-acre farm."

DEMO_BRIEF = {
    "project_name": "Solar-Powered Irrigation System",
    "objective": "Deliver reliable, low-cost irrigation for a 5-acre farm using solar power.",
    "description": (
        "A standalone solar photovoltaic system driving a water pump to "
        "irrigate 5 acres of cropland, reducing dependence on grid "
        "electricity or diesel pumps."
    ),
    "project_type": "Agricultural / Renewable Energy Hardware",
    "complexity": "Medium",
    "region": "Pakistan",
    "currency": "PKR",
    "key_assumptions": [
        "Farm has unobstructed sun exposure for at least 6 peak sun hours/day",
        "A water source (well or canal) is accessible within reasonable pumping distance",
        "Grid connection is unavailable or unreliable at the site",
    ],
    "clarifying_questions": [
        "What is the water source and its depth (borewell vs surface)?",
        "What crop and soil type determine the irrigation water demand?",
        "Is grid power available at all as a backup?",
    ],
}

DEMO_REQUIREMENTS = {
    "functional_requirements": [
        "Deliver sufficient daily water volume to irrigate 5 acres",
        "Operate autonomously during daylight hours without manual intervention",
        "Provide basic monitoring of pump status and water flow",
    ],
    "technical_requirements": [
        "Solar PV array sized to pump's power draw and daily sun hours",
        "DC or AC submersible/surface pump matched to head and flow rate",
        "MPPT solar pump controller or inverter",
        "Mounting structure rated for local wind loads",
    ],
    "user_requirements": [
        "Simple on/off operation requiring no technical training",
        "Visible status indicators (running / fault)",
    ],
    "hardware_software_requirements": [
        "Solar panels (~5-7 kW array, assumption pending site assessment)",
        "Solar pump controller with dry-run protection",
        "Submersible or surface pump",
        "Piping, valves, and drip/sprinkler distribution network",
        "Optional: mobile monitoring app / IoT flow sensor",
    ],
    "assumptions": [
        "5 acres requires an estimated 40,000-60,000 liters/day depending on crop and season",
        "Water table depth assumed moderate (< 50m); deep wells would raise pump cost",
    ],
    "dependencies": [
        "Site assessment must precede system sizing",
        "Water source yield test must precede pump selection",
    ],
    "missing_information": [
        "Exact crop type and irrigation schedule",
        "Water source type and depth",
        "Distance from water source to field",
    ],
}

DEMO_TASKS = {
    "tasks": [
        {"id": "T1", "name": "Site assessment", "description": "Survey land, sun exposure, and water source.", "priority": "High", "dependencies": [], "resources": ["Site engineer"], "duration_days": 3},
        {"id": "T2", "name": "Water requirement analysis", "description": "Calculate daily/seasonal water demand for 5 acres.", "priority": "High", "dependencies": ["T1"], "resources": ["Agronomist"], "duration_days": 2},
        {"id": "T3", "name": "Solar system sizing", "description": "Size PV array and battery/backup based on pump load.", "priority": "High", "dependencies": ["T2"], "resources": ["Solar engineer"], "duration_days": 3},
        {"id": "T4", "name": "Pump selection", "description": "Select pump matching flow rate and total dynamic head.", "priority": "High", "dependencies": ["T2"], "resources": ["Solar engineer"], "duration_days": 2},
        {"id": "T5", "name": "Irrigation design", "description": "Design pipe network and drip/sprinkler layout.", "priority": "Medium", "dependencies": ["T2"], "resources": ["Irrigation designer"], "duration_days": 4},
        {"id": "T6", "name": "Procurement", "description": "Source panels, pump, controller, piping and mounting hardware.", "priority": "High", "dependencies": ["T3", "T4", "T5"], "resources": ["Procurement officer"], "duration_days": 10},
        {"id": "T7", "name": "Mounting structure installation", "description": "Install racking/mounting for solar array.", "priority": "Medium", "dependencies": ["T6"], "resources": ["Installation crew"], "duration_days": 3},
        {"id": "T8", "name": "Electrical installation", "description": "Wire panels, controller and pump; install protection devices.", "priority": "High", "dependencies": ["T7"], "resources": ["Electrician"], "duration_days": 3},
        {"id": "T9", "name": "Pipe & distribution installation", "description": "Lay pipes and install drip/sprinkler distribution.", "priority": "Medium", "dependencies": ["T6"], "resources": ["Installation crew"], "duration_days": 5},
        {"id": "T10", "name": "System testing", "description": "Test pump output, flow rate, and solar generation under load.", "priority": "High", "dependencies": ["T8", "T9"], "resources": ["Solar engineer"], "duration_days": 3},
        {"id": "T11", "name": "Deployment & handover", "description": "Commission system and train farm operator.", "priority": "High", "dependencies": ["T10"], "resources": ["Project lead"], "duration_days": 2},
    ]
}

DEMO_COST = {
    "currency": "PKR",
    "line_items": [
        {"item": "Solar panels (~6kW)", "category": "Equipment", "quantity": "12 panels", "unit_cost": 45000, "total_cost": 540000},
        {"item": "Solar pump controller/inverter", "category": "Equipment", "quantity": "1", "unit_cost": 180000, "total_cost": 180000},
        {"item": "Submersible pump", "category": "Equipment", "quantity": "1", "unit_cost": 220000, "total_cost": 220000},
        {"item": "Mounting structure", "category": "Equipment", "quantity": "1 set", "unit_cost": 90000, "total_cost": 90000},
        {"item": "Pipes & drip/sprinkler network", "category": "Equipment", "quantity": "5 acres", "unit_cost": 60000, "total_cost": 300000},
        {"item": "Electrical wiring & protection", "category": "Installation", "quantity": "1 lot", "unit_cost": 70000, "total_cost": 70000},
        {"item": "Installation labor", "category": "Labor", "quantity": "12 days", "unit_cost": 8000, "total_cost": 96000},
        {"item": "System testing & commissioning", "category": "Testing", "quantity": "1 lot", "unit_cost": 40000, "total_cost": 40000},
        {"item": "Annual maintenance (year 1)", "category": "Maintenance", "quantity": "1 lot", "unit_cost": 60000, "total_cost": 60000},
    ],
    "subtotal": 1596000,
    "contingency_percent": 12,
    "total_estimated_cost": 1787520,
    "notes": (
        "Preliminary AI-generated estimate based on typical Pakistan market "
        "ranges as of the last known pricing data; obtain vendor quotations "
        "before committing budget."
    ),
}

DEMO_RISKS = {
    "risks": [
        {"risk": "Insufficient solar generation on cloudy days", "probability": "Medium", "impact": "High", "severity": "High", "mitigation": "Size array with margin + add small battery buffer or backup diesel pump."},
        {"risk": "Pump failure or premature wear", "probability": "Medium", "impact": "High", "severity": "High", "mitigation": "Select pump rated above peak demand; schedule preventive maintenance."},
        {"risk": "Water source yield lower than expected", "probability": "Medium", "impact": "High", "severity": "High", "mitigation": "Conduct a pump/yield test before finalizing system sizing."},
        {"risk": "Equipment procurement delays", "probability": "Medium", "impact": "Medium", "severity": "Medium", "mitigation": "Order long-lead items (panels, controller) early; identify backup suppliers."},
        {"risk": "Installation quality issues (leaks, wiring faults)", "probability": "Low", "impact": "Medium", "severity": "Medium", "mitigation": "Use experienced installation crew and conduct thorough testing before handover."},
        {"risk": "Theft or vandalism of panels in remote field", "probability": "Low", "impact": "Medium", "severity": "Low", "mitigation": "Install fencing/locking mounts and consider basic security signage."},
    ]
}

DEMO_TIMELINE = {
    "phases": [
        {"phase": "Planning", "task_ids": ["T1", "T2"], "start_day": 0, "end_day": 5},
        {"phase": "Design", "task_ids": ["T3", "T4", "T5"], "start_day": 5, "end_day": 9},
        {"phase": "Procurement", "task_ids": ["T6"], "start_day": 9, "end_day": 19},
        {"phase": "Installation", "task_ids": ["T7", "T8", "T9"], "start_day": 19, "end_day": 27},
        {"phase": "Testing", "task_ids": ["T10"], "start_day": 27, "end_day": 30},
        {"phase": "Deployment", "task_ids": ["T11"], "start_day": 30, "end_day": 32},
    ],
    "milestones": [
        {"milestone": "Site assessment complete", "day": 3},
        {"milestone": "System design finalized", "day": 9},
        {"milestone": "Equipment on site", "day": 19},
        {"milestone": "Installation complete", "day": 27},
        {"milestone": "System commissioned", "day": 32},
    ],
    "total_duration_days": 32,
}

DEMO_RESOURCES = {
    "human_resources": ["Site engineer", "Agronomist", "Solar engineer", "Irrigation designer", "Electrician", "Installation crew", "Procurement officer", "Project lead"],
    "hardware": ["Solar panels", "Solar pump controller/inverter", "Submersible pump", "Mounting structure", "Piping & drip/sprinkler network"],
    "software": ["Optional IoT monitoring dashboard"],
    "materials": ["Cabling", "Fasteners", "Waterproofing/sealant"],
    "tools": ["Multimeter", "Pipe cutting/fitting tools", "Torque wrench"],
    "external_services": ["Equipment vendor/supplier", "Local electrician (if subcontracted)"],
}

DEMO_FINAL_SUMMARY = {
    "executive_summary": (
        "This is a technically straightforward, moderate-cost solar irrigation "
        "project that is feasible within roughly one month, provided the site "
        "assessment confirms adequate sun exposure and water yield before "
        "procurement begins."
    ),
    "feasibility_verdict": "Feasible, contingent on a satisfactory site and water-yield assessment.",
    "recommendations": [
        {"recommendation": "Run the water source yield test before finalizing pump selection (T4).", "reason": "Pump failure and insufficient water availability are the two highest-severity risks identified."},
        {"recommendation": "Add 10-15% oversizing margin to the solar array beyond the base calculation.", "reason": "Protects against cloudy-day generation shortfalls, the top-ranked risk."},
        {"recommendation": "Order panels, controller and pump (T6) as early as possible, in parallel with T5 design work.", "reason": "Procurement is the longest task (10 days) and sits on the critical path."},
        {"recommendation": "Budget the full 12% contingency rather than treating it as optional.", "reason": "Remote-site installation and imported-component pricing carry real volatility."},
        {"recommendation": "Include a locking mount and basic signage in the installation scope.", "reason": "Theft/vandalism was flagged as a risk for unattended field equipment."},
    ],
}
