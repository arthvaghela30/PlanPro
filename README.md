# PlanPro — Production Planning & Costing Dashboard

A web-based production planning tool for modeling machines, shifts, and production runs, with cost analysis and deadline feasibility checks, built with a clean dark industrial aesthetic.

## Features
- Configure machines and shifts from a built-in catalogue or add fully custom ones
- Create and manage production plans with target units, assigned machine, and assigned shift
- Cost analysis showing labour cost, machine cost, total cost, and cost per unit
- Deadline feasibility check with automatic overtime cost breakdown when targets can't be met in normal hours
- Exportable HTML dashboard with charts, a shift comparison matrix, and a production timeline calendar
- Dark industrial-themed UI for a clean, professional look

## Tech Stack
- **Python (OOP)** — core planning and cost logic
- **Plotly** — interactive charts in the exported dashboard
- **HTML/CSS** — dark industrial-themed dashboard output

## Project Structure
```
planpro/
├── main.py                    # CLI entry point
├── production_planner.py      # Machine, Shift, ProductionPlan classes + dashboard generation
├── production_dashboard.html  # Sample generated dashboard output
├── test_feasibility.py        # Unit tests for feasibility calculations
└── README.md
```

## Future Improvements
- Persist plans and catalogues to a database instead of in-memory storage
- Support multiple simultaneous production plans/lines
- Add constraint-based scheduling to minimize total cost across machine/shift combinations
