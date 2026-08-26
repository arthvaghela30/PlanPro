import math
import webbrowser

MACHINE_CATALOGUE = {
    "1": {
        "name": "CNC Lathe",
        "units_per_hour": 50,
        "hourly_cost": 800,
        "description": "Precision turning of cylindrical parts"
    },
    "2": {
        "name": "CNC Milling Machine",
        "units_per_hour": 35,
        "hourly_cost": 1200,
        "description": "Complex surface and profile machining"
    },
    "3": {
        "name": "3D Printer (FDM)",
        "units_per_hour": 4,
        "hourly_cost": 300,
        "description": "Rapid prototyping and low-volume production"
    },
    "4": {
        "name": "Injection Molding Machine",
        "units_per_hour": 200,
        "hourly_cost": 2000,
        "description": "High-volume plastic part production"
    },
    "5": {
        "name": "Hydraulic Press",
        "units_per_hour": 80,
        "hourly_cost": 600,
        "description": "Sheet metal forming and stamping"
    },
    "6": {
        "name": "Welding Station (MIG)",
        "units_per_hour": 15,
        "hourly_cost": 400,
        "description": "Metal joining and fabrication"
    },
    "7": {
        "name": "Laser Cutting Machine",
        "units_per_hour": 60,
        "hourly_cost": 1500,
        "description": "High precision sheet cutting"
    },
    "8": {
        "name": "CNC Grinding Machine",
        "units_per_hour": 25,
        "hourly_cost": 900,
        "description": "Surface finishing and tight tolerance work"
    },
    "9": {
        "name": "Die Casting Machine",
        "units_per_hour": 120,
        "hourly_cost": 2500,
        "description": "High-volume metal part casting"
    },
    "10": {
        "name": "Conveyor Assembly Line",
        "units_per_hour": 300,
        "hourly_cost": 1800,
        "description": "Mass assembly and packaging"
    }
}
SHIFT_CATALOGUE = {
    "1": {
        "name": "Morning Shift",
        "hours_per_day": 8,
        "workers": 5,
        "wage_per_hour": 150,
        "description": "Standard day shift — 6AM to 2PM"
    },
    "2": {
        "name": "Afternoon Shift",
        "hours_per_day": 8,
        "workers": 5,
        "wage_per_hour": 150,
        "description": "Standard afternoon shift — 2PM to 10PM"
    },
    "3": {
        "name": "Night Shift",
        "hours_per_day": 8,
        "workers": 4,
        "wage_per_hour": 190,
        "description": "Night shift — 10PM to 6AM (25% wage premium)"
    },
    "4": {
        "name": "Double Shift",
        "hours_per_day": 16,
        "workers": 10,
        "wage_per_hour": 150,
        "description": "Two back-to-back shifts — maximum output"
    },
    "5": {
        "name": "Half Day Shift",
        "hours_per_day": 4,
        "workers": 3,
        "wage_per_hour": 150,
        "description": "Short shift — maintenance or low demand periods"
    },
    "6": {
        "name": "Weekend Shift",
        "hours_per_day": 10,
        "workers": 6,
        "wage_per_hour": 200,
        "description": "Weekend overtime shift (33% wage premium)"
    }
}
class Machine:
    def __init__(self, name, units_per_hour, hourly_cost):
        self.name = name
        self.units_per_hour = units_per_hour
        self.hourly_cost = hourly_cost
        self.is_bottleneck = False

class Shift:
    def __init__(self, name, hours_per_day, workers, wage_per_hour):
        self.name = name
        self.hours_per_day = hours_per_day
        self.workers = workers
        self.wage_per_hour = wage_per_hour

class ProductionPlan:
    def __init__(self, target_units, machine, shift):  
        self.target_units = target_units
        self.machine = machine  
        self.shift = shift      
        self.overtime_hours = 0

    def units_per_day(self):
        return self.machine.units_per_hour * self.shift.hours_per_day

    def days_needed(self):
        return math.ceil(self.target_units / self.units_per_day())  

    def labour_cost(self):
        return self.shift.workers * self.shift.wage_per_hour * self.shift.hours_per_day

    def machine_cost(self):
        return self.machine.hourly_cost * self.shift.hours_per_day  
    def total_cost(self):
        return (self.labour_cost() + self.machine_cost()) * self.days_needed()  

    def cost_per_unit(self):
        return self.total_cost() / self.target_units  

    def check_feasibility(self, deadline):
        total_machine_hours = self.target_units / self.machine.units_per_hour
        normal_shift_hours_available = self.shift.hours_per_day * deadline
        overtime_machine_hours = max(0, total_machine_hours - normal_shift_hours_available)
        
        required_units_per_day = self.target_units / deadline
        required_machine_hours_per_day = required_units_per_day / self.machine.units_per_hour
        overtime_hours_per_day = max(0, required_machine_hours_per_day - self.shift.hours_per_day)
        
        feasible = required_machine_hours_per_day <= 24
        
        if not feasible:
            ot_cost = 0
            machine_ot_cost = 0
            labour_ot_cost = 0
        else:
            machine_ot_cost = overtime_machine_hours * self.machine.hourly_cost
            labour_ot_cost = overtime_machine_hours * self.shift.workers * self.shift.wage_per_hour * 1.5
            ot_cost = machine_ot_cost + labour_ot_cost
            
        return {
            "target_units": self.target_units,
            "deadline": deadline,
            "normal_capacity": self.units_per_day(),
            "required_capacity": required_units_per_day,
            "normal_shift_hours": self.shift.hours_per_day,
            "required_operating_hours": required_machine_hours_per_day,
            "overtime_required_per_day": overtime_hours_per_day,
            "max_capacity": self.machine.units_per_hour * 24,
            "feasible": feasible,
            "total_ot_machine_hours": overtime_machine_hours,
            "ot_cost": ot_cost,
            "machine_ot_cost": machine_ot_cost,
            "labour_ot_cost": labour_ot_cost
        }

def generate_dashboard(plan):
    import plotly.graph_objects as go
    import plotly.io as pio
    import webbrowser
    import os

        # ── SHIFT COMPARISON MATRIX LOGIC ──
    from production_planner import SHIFT_CATALOGUE, Shift
    shift_matrix_rows = ""
    deadline = getattr(plan, 'deadline', 7)
    
    for s_key, s_data in SHIFT_CATALOGUE.items():
        s = Shift(s_data['name'], s_data['hours_per_day'], s_data['workers'], s_data['wage_per_hour'])
        # We need a temporary plan to check feasibility across different shifts
        from production_planner import ProductionPlan
        temp_plan = ProductionPlan(plan.target_units, plan.machine, s)
        feas = temp_plan.check_feasibility(deadline)
        
        if s.name == plan.shift.name:
            status = '<span style="color:var(--primary); font-weight:600;">Selected</span>'
        elif not feas['feasible']:
            status = '<span style="color:var(--danger); font-weight:600;">Not Feasible</span>'
        elif feas['overtime_required_per_day'] > 0:
            status = '<span style="color:var(--warning); font-weight:600;">OT Required</span>'
        else:
            status = '<span style="color:var(--success); font-weight:600;">Feasible</span>'
            
        cost_day = s.hours_per_day * plan.machine.hourly_cost + s.hours_per_day * s.workers * s.wage_per_hour
        upd = plan.machine.units_per_hour * s.hours_per_day
        
        is_selected = "background: rgba(59, 130, 246, 0.1); border-left: 3px solid var(--primary);" if s.name == plan.shift.name else "border-left: 3px solid transparent;"
        
        shift_matrix_rows += f"""
        <tr style="{is_selected} border-bottom: 1px solid var(--border-color);">
            <td style="padding: 12px; font-weight: 600;">{s.name} </td>
            <td style="padding: 12px; font-family: var(--font-data);">{upd:,.0f} units</td>
            <td style="padding: 12px; font-family: var(--font-data);">₹{cost_day:,.0f}</td>
            <td style="padding: 12px;">{status}</td>
        </tr>
        """
        
    shift_matrix_html = f"""
    <div class="glass-panel" style="margin-bottom: 24px;">
        <div class="panel-header" style="margin-bottom: 16px;">
            <div class="panel-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Shift Comparison Matrix (For {plan.machine.name})
            </div>
        </div>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
            <thead>
                <tr>
                    <th style="padding: 12px; color: var(--text-2); font-weight: 600; text-transform: uppercase; font-size: 11px; border-bottom: 1px solid var(--border-color);">Shift</th>
                    <th style="padding: 12px; color: var(--text-2); font-weight: 600; text-transform: uppercase; font-size: 11px; border-bottom: 1px solid var(--border-color);">Output / Day</th>
                    <th style="padding: 12px; color: var(--text-2); font-weight: 600; text-transform: uppercase; font-size: 11px; border-bottom: 1px solid var(--border-color);">Cost / Day</th>
                    <th style="padding: 12px; color: var(--text-2); font-weight: 600; text-transform: uppercase; font-size: 11px; border-bottom: 1px solid var(--border-color);">Status ({deadline}-Day)</th>
                </tr>
            </thead>
            <tbody>
                {shift_matrix_rows}
            </tbody>
        </table>
    </div>
    """

    # ── CHART 1: Cost Breakdown — Donut ──
    total_machine_cost = plan.machine_cost() * plan.days_needed()
    total_labour_cost = plan.labour_cost() * plan.days_needed()
    total_run_cost = plan.total_cost()
    
    fig1 = go.Figure(go.Pie(
        labels=["Labour Cost", "Machine Cost"],
        values=[total_labour_cost, total_machine_cost],
        hole=0.65,
        marker=dict(
            colors=["#6366f1", "#06b6d4"],
            line=dict(color="#0A0F1E", width=4)
        ),
        textinfo="label+percent",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"
    ))
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(
            text=f"₹{total_run_cost:,.0f}<br><span style='font-size:10px'>Total</span>",
            x=0.5, y=0.5, font=dict(size=14, color="white"), showarrow=False
        )]
    )
    chart_donut = pio.to_html(fig1, full_html=False, include_plotlyjs=False)

    cost_receipt_html = f"""
    <div style="display:flex; flex-direction:column; justify-content:center; padding: 16px; background: rgba(0,0,0,0.2); border-radius: 12px; font-family: var(--font-data); height: 100%;">
        <div style="display:flex; justify-content:space-between; margin-bottom: 12px; color: var(--text-2); font-size: 13px;">
            <span>Machine Cost</span>
            <span>₹{total_machine_cost:,.0f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 12px; color: var(--text-2); font-size: 13px;">
            <span>Labour Cost</span>
            <span>₹{total_labour_cost:,.0f}</span>
        </div>
        <div style="border-top: 1px dashed var(--border-color); margin-bottom: 12px;"></div>
        <div style="display:flex; justify-content:space-between; font-weight: 700; font-size: 16px; color: var(--text-1);">
            <span>TOTAL COST</span>
            <span>₹{total_run_cost:,.0f}</span>
        </div>
    </div>
    """

    # ── CHART 2: Daily Cost Accumulation — Area ──
    days = list(range(0, plan.days_needed() + 1))
    daily_cost = plan.labour_cost() + plan.machine_cost()
    cumulative_cost = [daily_cost * d for d in days]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=days, y=cumulative_cost,
        mode="lines",
        line=dict(color="#6366f1", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
        hovertemplate="Day %{x}<br>Cost: ₹%{y:,.0f}<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=30, l=50, r=10),
        xaxis=dict(title="Day", showgrid=False, color="#475569",
                   tickfont=dict(color="#64748B"), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1E293B", color="#475569",
                   tickfont=dict(color="#64748B"), zeroline=False,
                   tickprefix="₹", tickformat=",.0f"),
        hovermode="x unified"
    )
    chart_cost_accum = pio.to_html(fig2, full_html=False, include_plotlyjs=False)

    # ── CHART 3: Production Progress — Stepped Line ──
    days_range = list(range(0, plan.days_needed() + 1))
    units_produced = [min(plan.units_per_day() * d, plan.target_units) for d in days_range]

    fig3 = go.Figure()
    # Target zone
    fig3.add_hrect(
        y0=plan.target_units * 0.9, y1=plan.target_units,
        fillcolor="rgba(16,185,129,0.05)",
        line_width=0
    )
    # Progress line
    fig3.add_trace(go.Scatter(
        x=days_range, y=units_produced,
        mode="lines+markers",
        line=dict(color="#06b6d4", width=3, shape="spline"),
        marker=dict(size=7, color="#06b6d4",
                    line=dict(color="#0A0F1E", width=2)),
        fill="tozeroy",
        fillcolor="rgba(6,182,212,0.06)",
        name="Units Produced",
        hovertemplate="Day %{x}<br>Units: %{y:,.0f}<extra></extra>"
    ))
    # Target line
    fig3.add_hline(
        y=plan.target_units,
        line=dict(color="#EF4444", dash="dot", width=1.5),
        annotation_text=f"Target: {plan.target_units:,}",
        annotation_font=dict(color="#EF4444", size=11)
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=20, b=30, l=50, r=60),
        xaxis=dict(title="Production Day", showgrid=False, color="#475569",
                   tickfont=dict(color="#64748B"), zeroline=False),
        yaxis=dict(title="Units", showgrid=True, gridcolor="#1E293B",
                   color="#475569", tickfont=dict(color="#64748B"),
                   zeroline=False, tickformat=","),
        hovermode="x unified"
    )
    chart_progress = pio.to_html(fig3, full_html=False, include_plotlyjs=False)

    # ── CHART 4: Machine Utilization Gauge ──
    required_machine_hours_per_day = (plan.target_units / deadline) / plan.machine.units_per_hour
    utilization = min(round((required_machine_hours_per_day / plan.shift.hours_per_day) * 100, 1), 100)
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=utilization,
        number={'suffix': "%", 'font': {'color': '#06b6d4', 'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "#06b6d4"},
            'bgcolor': "rgba(255,255,255,0.05)",
            'steps': [
                {'range': [0, 50], 'color': "rgba(239,68,68,0.2)"},
                {'range': [50, 80], 'color': "rgba(245,158,11,0.2)"},
                {'range': [80, 100], 'color': "rgba(16,185,129,0.2)"}
            ],
        }
    ))
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=20, l=20, r=20),
        height=300
    )
    chart_gauge = pio.to_html(fig4, full_html=False, include_plotlyjs=False)

    # ── CHART 5: Cost Comparison Bar ──
    fig5 = go.Figure(go.Bar(
        x=[plan.labour_cost(), plan.machine_cost()],
        y=["Labour", "Machine"],
        orientation='h',
        marker=dict(color=["#6366f1", "#06b6d4"], line=dict(color="#0A0F1E", width=2)),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
    ))
    fig5.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=30, l=70, r=20),
        xaxis=dict(showgrid=True, gridcolor="#1E293B", color="#475569", zeroline=False, tickprefix="₹"),
        yaxis=dict(showgrid=False, color="#94A3B8", tickfont=dict(size=13)),
        height=300
    )
    chart_bar = pio.to_html(fig5, full_html=False, include_plotlyjs=False)

    # ── OVERTIME SECTION LOGIC ──
    deadline = getattr(plan, 'deadline', 7)
    feas = plan.check_feasibility(deadline)
    ot_cost_7 = feas['ot_cost']
    overtime_html = ""
    
    if not feas['feasible']:
        overtime_html = f"""
        <div class="glass-panel" style="margin-top: 32px; border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 30px rgba(239, 68, 68, 0.05);">
            <div class="panel-header" style="margin-bottom: 24px;">
                <div class="panel-title" style="color: var(--danger); font-size: 20px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    Deadline Not Feasible ({deadline}-Day)
                </div>
            </div>
            <div style="background:rgba(239, 68, 68, 0.05); padding:16px; border-radius:12px; border:1px solid rgba(239, 68, 68, 0.15);">
                <p style="color:var(--text-2); font-size:14px; line-height:1.6;">
                    Target volume of <b>{plan.target_units:,} units</b> requires <b>{feas['required_operating_hours']:.2f} hours/day</b> of machine time, which exceeds the physical limit of 24 hours/day. 
                </p>
                <p style="color:var(--text-2); font-size:14px; margin-top:8px;">
                    <b>Recommendations:</b> Extend the deadline or use an additional machine.
                </p>
            </div>
        </div>
        """
    elif feas['overtime_required_per_day'] > 0:
        fig_ot = go.Figure(go.Pie(
            labels=["Machine OT Cost", "Labour OT Cost (1.5x)"],
            values=[feas['machine_ot_cost'], feas['labour_ot_cost']],
            hole=0.6,
            marker=dict(colors=["#06b6d4", "#f43f5e"], line=dict(color="#0A0F1E", width=3)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"
        ))
        fig_ot.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=200
        )
        chart_ot = pio.to_html(fig_ot, full_html=False, include_plotlyjs=False)

        req_throughput = round(plan.target_units / (deadline * plan.shift.hours_per_day))

        overtime_html = f"""
        <!-- OVERTIME SECTION -->
        <div class="glass-panel" style="margin-top: 32px; border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 30px rgba(239, 68, 68, 0.05);">
            <div class="panel-header" style="margin-bottom: 24px;">
                <div class="panel-title" style="color: var(--danger); font-size: 20px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    Overtime Alert & Analysis
                </div>
            </div>
            
            <div class="chart-grid" style="grid-template-columns: 1fr 1fr; gap: 24px;">
                <div style="display:flex; flex-direction:column; gap:16px;">
                    
                    <!-- WHY OVERTIME -->
                    <div style="background:rgba(239, 68, 68, 0.05); padding:16px; border-radius:12px; border:1px solid rgba(239, 68, 68, 0.15);">
                        <h4 style="color:var(--text-1); margin-bottom:8px; font-size:15px;">Why is Overtime Required?</h4>
                        <p style="color:var(--text-2); font-size:14px; line-height:1.6;">
                            Target volume of <b>{plan.target_units:,} units</b> requires <b>{feas['required_operating_hours']:.2f} hours/day</b> of machine time. This exceeds the normal {plan.shift.hours_per_day}-hour shift capacity by <b>{feas['overtime_required_per_day']:.2f} hours/day</b>.
                        </p>
                    </div>
                    
                    <!-- COSTS -->
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                        <div style="background:var(--bg-surface-hover); padding:16px; border-radius:12px; border:1px solid var(--border-color);">
                            <div style="font-size:12px; color:var(--text-3); text-transform:uppercase; font-weight:600; margin-bottom:4px;">Extra Machine Hours</div>
                            <div style="font-family:var(--font-data); font-size:24px; font-weight:700; color:var(--danger);">{feas['total_ot_machine_hours']:.2f} hrs</div>
                        </div>
                        <div style="background:var(--bg-surface-hover); padding:16px; border-radius:12px; border:1px solid var(--border-color);">
                            <div style="font-size:12px; color:var(--text-3); text-transform:uppercase; font-weight:600; margin-bottom:4px;">Overtime Cost</div>
                            <div style="font-family:var(--font-data); font-size:24px; font-weight:700; color:var(--danger);">₹{ot_cost_7:,.0f}</div>
                            <div style="font-size:11px; color:var(--text-3); margin-top:8px; line-height:1.4;">Machine OT Cost = OT Hours × Machine Rate<br>Labour OT Cost = OT Hours × Workers × Labour Rate × 1.5</div>
                        </div>
                    </div>
                    
                    <!-- RESOLUTION -->
                    <div style="background:rgba(16, 185, 129, 0.05); padding:16px; border-radius:12px; border:1px solid rgba(16, 185, 129, 0.15);">
                        <h4 style="color:var(--success); margin-bottom:8px; font-size:15px;">How to Avoid This Cost?</h4>
                        <ul style="color:var(--text-2); font-size:13px; line-height:1.7; padding-left:20px; margin:0;">
                            <li><b>Increase Shift Length:</b> Deploy a longer shift (currently {plan.shift.hours_per_day}h/day).</li>
                            <li><b>Upgrade Machinery:</b> Use a machine capable of at least <b>{req_throughput} units/hr</b>.</li>
                            <li><b>Parallel Production:</b> Offload units to a secondary machine.</li>
                        </ul>
                    </div>
                </div>
                
                <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; background:var(--bg-surface-hover); border-radius:16px; border: 1px solid var(--border-color); padding: 16px;">
                    <h4 style="margin-bottom:16px; color:var(--text-2); font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">Overtime Cost Breakdown</h4>
                    <div class="chart-wrapper" style="width:100%; min-height:220px; position:relative;">
                        {chart_ot}
                    </div>
                </div>
            </div>
        </div>
        """

    # ── HARDWARE SPECS LOGIC ──
    specs = {
        "CNC Milling": {"class": "Heavy Machining", "power": "45 kW/hr", "maint": "Every 500 hrs"},
        "CNC Lathe": {"class": "Precision Turning", "power": "30 kW/hr", "maint": "Every 400 hrs"},
        "Hydraulic Press": {"class": "Forming & Forging", "power": "80 kW/hr", "maint": "Every 1000 hrs"},
        "Conveyor Assembly Line": {"class": "Continuous Automation", "power": "15 kW/hr", "maint": "Monthly"}
    }
    m_specs = specs.get(plan.machine.name, {"class": "Standard Industrial", "power": "N/A", "maint": "Standard Interval"})
    
    specs_html = f'''<div style="margin-top: 16px; padding: 16px; background: rgba(0,0,0,0.2); border-radius: 8px; border-left: 3px solid var(--primary);">
        <div style="font-size:11px; color:var(--text-3); text-transform:uppercase; margin-bottom:12px; font-weight:600;">Hardware Specifications</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
            <span style="color:var(--text-2);">Asset Class</span><span style="color:var(--text-1); font-weight:500;">{m_specs['class']}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
            <span style="color:var(--text-2);">Power Draw</span><span style="color:var(--text-1); font-family:var(--font-data);">{m_specs['power']}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
            <span style="color:var(--text-2);">Maintenance</span><span style="color:var(--text-1);">{m_specs['maint']}</span>
        </div>
        <div style="border-top:1px dashed var(--border-color); margin:12px 0;"></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
            <span style="color:var(--text-2);">Operational Cost</span><span style="font-family:var(--font-data); font-weight:600;">₹{plan.machine.hourly_cost}/hr</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px;">
            <span style="color:var(--text-2);">Throughput Max</span><span style="font-family:var(--font-data); font-weight:600;">{plan.machine.units_per_hour}/hr</span>
        </div>
    </div>'''

    # ── CALENDAR LOGIC ──
    import datetime, calendar
    now = datetime.datetime.now()
    days_needed = plan.days_needed()
    end_date = now + datetime.timedelta(days=days_needed)
    
    cal = calendar.monthcalendar(now.year, now.month)
    month_name = calendar.month_name[now.month]
    
    cal_html = ""
    for week in cal:
        cal_html += "<tr>"
        for day in week:
            if day == 0:
                cal_html += '<td style="padding: 2px;"></td>'
            else:
                day_date = datetime.datetime(now.year, now.month, day)
                is_today = (day == now.day)
                
                # Check if day is within the production window
                in_range = False
                is_end = False
                
                # Zero out hours/minutes for accurate date comparison
                date_only_now = now.date()
                date_only_day = day_date.date()
                date_only_end = end_date.date()
                
                if date_only_now <= date_only_day <= date_only_end:
                    in_range = True
                if date_only_day == date_only_end:
                    is_end = True
                
                style = "width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 10px; border-radius: 4px; margin: auto;"
                if is_end:
                    style += " background: var(--success); color: white; font-weight: bold; box-shadow: 0 0 10px var(--success-glow);"
                elif is_today:
                    style += " background: var(--primary); color: white; font-weight: bold; box-shadow: 0 0 10px var(--primary-glow);"
                elif in_range:
                    style += " background: rgba(59, 130, 246, 0.2); color: var(--text-1);"
                else:
                    style += " color: var(--text-2);"
                
                cal_html += f'<td style="padding: 2px; text-align: center;"><div style="{style}">{day}</div></td>'
        cal_html += "</tr>"
        
    calendar_html = f'''
    <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px; backdrop-filter: var(--glass-blur); display: flex; gap: 16px; align-items: center;">
        <div style="flex-shrink: 0;">
            <div style="font-size: 10px; font-weight: 600; color: var(--text-1); text-transform: uppercase; margin-bottom: 6px;">{month_name} {now.year}</div>
            <table style="border-collapse: collapse; font-family: var(--font-data);">
                <thead>
                    <tr>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">Mo</th>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">Tu</th>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">We</th>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">Th</th>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">Fr</th>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">Sa</th>
                        <th style="font-size: 9px; color: var(--text-3); font-weight: normal; padding-bottom: 4px;">Su</th>
                    </tr>
                </thead>
                <tbody>
                    {cal_html}
                </tbody>
            </table>
        </div>
        <div style="border-left: 1px dashed var(--border-color); padding-left: 16px; display: flex; flex-direction: column; justify-content: center; gap: 12px;">
            <div>
                <div style="display:flex; align-items:center; gap:6px; font-size: 9px; color: var(--text-2); text-transform: uppercase; margin-bottom:2px;">
                    <div style="width:8px; height:8px; border-radius:2px; background:var(--primary);"></div>
                    Commence
                </div>
                <div style="font-size: 13px; font-weight: 600; color: var(--text-1);">{now.strftime("%b %d, %Y")}</div>
            </div>
            <div>
                <div style="display:flex; align-items:center; gap:6px; font-size: 9px; color: var(--text-2); text-transform: uppercase; margin-bottom:2px;">
                    <div style="width:8px; height:8px; border-radius:2px; background:var(--success);"></div>
                    Delivery
                </div>
                <div style="font-size: 13px; font-weight: 600; color: var(--text-1);">{end_date.strftime("%b %d, %Y")}</div>
            </div>
        </div>
    </div>
    '''

    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PlanPro - Production Planning</title>
    
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    
    <!-- Professional Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* ==========================================================================
           1. DESIGN SYSTEM & CSS VARIABLES
           ========================================================================== */
        :root {{
            /* Core Colors */
            --primary: #3b82f6; --primary-glow: rgba(59, 130, 246, 0.4);
            --success: #10b981; --success-glow: rgba(16, 185, 129, 0.4);
            --warning: #f59e0b; --warning-glow: rgba(245, 158, 11, 0.4);
            --danger:  #ef4444; --danger-glow:  rgba(239, 68, 68, 0.4);
            --purple:  #8b5cf6; --purple-glow:  rgba(139, 92, 246, 0.4);

            /* Typography */
            --font-ui: 'Inter', sans-serif;
            --font-display: 'Plus Jakarta Sans', sans-serif;
            --font-data: 'Space Grotesk', monospace;

            /* Spacing */
            --s-1: 8px; --s-2: 16px; --s-3: 24px; --s-4: 32px;
            
            /* Transitions */
            --transition-fast: 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            --transition-smooth: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        [data-theme="dark"] {{
            --bg-app: #030712;
            --bg-surface: rgba(17, 24, 39, 0.6);
            --bg-surface-hover: rgba(31, 41, 55, 0.8);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(255, 255, 255, 0.2);
            --text-1: #f9fafb; --text-2: #9ca3af; --text-3: #6b7280;
            --shadow-float: 0 20px 40px rgba(0,0,0,0.4);
            --mouse-glow: rgba(255, 255, 255, 0.04);
            --glass-blur: blur(24px);
            --chart-grid: rgba(255, 255, 255, 0.05);
            --chart-text: #94a3b8;
        }}

        [data-theme="light"] {{
            --bg-app: #f8fafc;
            --bg-surface: rgba(255, 255, 255, 0.7);
            --bg-surface-hover: rgba(255, 255, 255, 1);
            --border-color: rgba(15, 23, 42, 0.08);
            --border-highlight: rgba(15, 23, 42, 0.15);
            --text-1: #0f172a; --text-2: #475569; --text-3: #94a3b8;
            --shadow-float: 0 20px 40px rgba(0,0,0,0.06);
            --mouse-glow: rgba(0, 0, 0, 0.02);
            --glass-blur: blur(24px);
            --chart-grid: rgba(15, 23, 42, 0.05);
            --chart-text: #475569;
        }}

        /* ==========================================================================
           2. GLOBAL RESET & BASE
           ========================================================================== */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ height: 100%; overflow: hidden; }}
        body {{
            font-family: var(--font-ui); background-color: var(--bg-app); color: var(--text-1);
            transition: background 0.4s ease, color 0.4s ease; -webkit-font-smoothing: antialiased;
            background-image: radial-gradient(circle at 0% 0%, var(--primary-glow) 0%, transparent 40%),
                              radial-gradient(circle at 100% 100%, var(--purple-glow) 0%, transparent 40%);
        }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 10px; }}

        /* ==========================================================================
           3. APPLICATION LAYOUT
           ========================================================================== */
        .app-shell {{ display: flex; flex-direction: column; height: 100vh; width: 100vw; overflow: hidden; }}
        
        .main-wrapper {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }}

        /* ==========================================================================
           4. TOP NAVIGATION
           ========================================================================== */
        .navbar {{
            height: 80px; padding: 0 var(--s-4); display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid var(--border-color); background: rgba(3,7,18,0.4);
            backdrop-filter: blur(12px); z-index: 50;
        }}
        .breadcrumb {{ display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; color: var(--text-2); }}
        .breadcrumb .current {{ color: var(--text-1); font-weight: 600; background: var(--bg-surface); padding: 4px 12px; border-radius: 100px; border: 1px solid var(--border-color); }}
        
        .icon-btn {{ width: 40px; height: 40px; border-radius: 50%; background: transparent; border: 1px solid transparent; display: flex; align-items: center; justify-content: center; color: var(--text-2); cursor: pointer; transition: var(--transition-fast); }}
        .icon-btn:hover {{ background: var(--bg-surface); border-color: var(--border-color); color: var(--text-1); transform: translateY(-2px); }}

        /* ==========================================================================
           5. DASHBOARD GRID & GLASS PANELS
           ========================================================================== */
        .scroll-area {{ flex: 1; overflow-y: auto; overflow-x: hidden; padding-bottom: var(--s-6); }}
        .dashboard-container {{ padding: var(--s-4); max-width: 1800px; margin: 0 auto; display: grid; grid-template-columns: 1fr 360px; gap: var(--s-4); }}
        @media (max-width: 1400px) {{ .dashboard-container {{ grid-template-columns: 1fr; }} }}
        
        .main-col {{ display: flex; flex-direction: column; gap: var(--s-4); }}
        .right-col {{ display: flex; flex-direction: column; gap: var(--s-3); }}

        .glass-panel {{
            background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 24px;
            backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
            padding: var(--s-3); position: relative; overflow: hidden; display: flex; flex-direction: column;
            transition: transform var(--transition-smooth), box-shadow var(--transition-smooth), border-color var(--transition-fast);
        }}
        .glass-panel::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(800px circle at var(--mouse-x, 0) var(--mouse-y, 0), var(--mouse-glow), transparent 40%);
            opacity: 0; transition: opacity 0.5s; pointer-events: none; z-index: 0;
        }}
        .glass-panel:hover::before {{ opacity: 1; }}
        .glass-panel:hover {{ border-color: var(--border-highlight); transform: translateY(-4px); box-shadow: var(--shadow-float); }}
        
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--s-3); position: relative; z-index: 1; }}
        .panel-title {{ font-family: var(--font-display); font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; }}

        /* ==========================================================================
           6. EXECUTIVE KPIs & MODULES
           ========================================================================== */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--s-3); }}
        .kpi-card {{ padding: 24px; z-index: 1; }}
        .kpi-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }}
        .kpi-label {{ font-size: 13px; font-weight: 600; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-family: var(--font-data); font-size: 40px; font-weight: 700; line-height: 1; margin-bottom: 12px; color: var(--text-1); }}
        
        /* ==========================================================================
           7. CHART FIXES
           ========================================================================== */
        .chart-grid {{ display: grid; grid-template-columns: 5fr 4fr; gap: var(--s-3); }}
        @media (max-width: 1000px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
        
        .chart-wrapper {{
            position: relative; width: 100%; flex: 1 1 auto; min-height: 250px; 
            display: flex; flex-direction: column; z-index: 1;
        }}
        .chart-wrapper > div {{ flex: 1 1 auto; width: 100% !important; display: flex; flex-direction: column; }}
        .plotly-graph-div {{ flex: 1 1 auto; width: 100% !important; height: 100% !important; }}
        
        /* Light mode filter hack for python-generated dark charts */
        html[data-theme="light"] .plotly-graph-div {{ filter: invert(1) hue-rotate(180deg) brightness(1.1); }}

        /* ==========================================================================
           8. TIMELINE & RIGHT PANEL
           ========================================================================== */
        .v-timeline {{ position: relative; padding-left: 24px; margin-top: 16px; z-index: 1; }}
        .v-timeline::before {{ content: ''; position: absolute; left: 5px; top: 8px; bottom: 8px; width: 2px; background: var(--border-color); }}
        .tl-node {{ position: relative; margin-bottom: 24px; }}
        .tl-dot {{ position: absolute; left: -24px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: var(--bg-app); border: 2px solid var(--border-color); transition: var(--transition-fast); }}
        .tl-node:hover .tl-dot {{ transform: scale(1.3); }}
        
        .ai-card {{ background: rgba(139, 92, 246, 0.05); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 16px; padding: 16px; margin-bottom: 12px; display: flex; gap: 12px; cursor: pointer; transition: transform var(--transition-fast); z-index: 1; }}
        .ai-card:hover {{ transform: translateX(4px); border-color: var(--purple); }}

        .btn-premium {{ background: var(--text-1); color: var(--bg-app); border: none; padding: 10px 20px; border-radius: 12px; font-weight: 600; font-size: 13px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: transform var(--transition-fast); z-index: 50; }}
        .btn-premium:hover {{ transform: scale(1.05); }}

        @media print {{
            html, body {{ background: white !important; color: black !important; height: auto !important; overflow: visible !important; }}
            .navbar {{ display: none !important; }}
            .app-shell {{ display: block !important; height: auto !important; overflow: visible !important; }}
            .main-wrapper {{ display: block !important; height: auto !important; overflow: visible !important; }}
            .scroll-area {{ display: block !important; height: auto !important; overflow: visible !important; }}
            .glass-panel {{ box-shadow: none !important; border: 1px solid #e2e8f0 !important; break-inside: avoid; background: white !important; -webkit-print-color-adjust: exact; margin-bottom: 24px !important; }}
            .dashboard-container {{ display: grid !important; max-width: 100% !important; padding: 0 !important; gap: 24px !important; grid-template-columns: 1fr 300px !important; }}
            .right-col {{ display: flex !important; }}
            .chart-grid {{ display: grid !important; grid-template-columns: 1fr 1fr !important; }}
            .plotly-graph-div {{ filter: invert(1) hue-rotate(180deg) brightness(1.1); }}
        }}
    </style>
</head>
<body>
    <div class="app-shell">
        
        <!-- MAIN WRAPPER -->
        <div class="main-wrapper">
            
            <!-- NAVBAR -->
            <header class="navbar">
                <div class="nav-left" style="display:flex; align-items:center; gap:24px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, var(--primary), var(--purple)); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px var(--primary-glow); flex-shrink: 0;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                        </div>
                        <div>
                            <div style="font-family: var(--font-display); font-weight: 800; font-size: 20px; letter-spacing: -0.5px; color: var(--text-1); line-height: 1;">PlanPro</div>
                            <div style="font-size: 10px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; font-weight:600;">Production Planning & Cost Analysis Dashboard</div>
                        </div>
                    </div>
                    
                    <div class="breadcrumb" style="border-left: 1px solid var(--border-color); padding-left: 24px; height: 32px; display:flex; align-items:center;">
                        <span id="header-date"></span> <span style="margin:0 8px; color:var(--text-3);">/</span>
                        <span class="current">{plan.machine.name}</span>
                    </div>
                </div>
                
                <div class="nav-right" style="display:flex; align-items:center; gap:16px;">
                    <button id="theme-btn" class="icon-btn" title="Toggle Theme"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg></button>
                    <div id="user-profile" style="display:flex; align-items:center; gap:12px; background:var(--bg-surface); border:1px solid var(--border-color); padding:4px 16px 4px 4px; border-radius:100px; cursor:pointer;" title="Click to change name">
                        <div id="user-initials" style="width:32px; height:32px; border-radius:50%; background:var(--primary); display:flex; align-items:center; justify-content:center; font-weight:700; color:#fff; font-size:12px;">JD</div>
                        <span id="user-name" style="font-size:13px; font-weight:600;">J. Doe</span>
                    </div>
                </div>
            </header>

            <!-- SCROLL AREA -->
            <div class="scroll-area">
                <div class="dashboard-container">
                    
                    <!-- LEFT COLUMN (Main Data) -->
                    <div class="main-col">
                        
                        <!-- Header -->
                        <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                            <div>
                                <h1 style="font-family: var(--font-display); font-size: 32px; font-weight: 800; letter-spacing: -1px; margin-bottom: 8px;">Executive Analytics</h1>
                                <div style="display:flex; gap: 16px; color: var(--text-2); font-size: 14px; font-weight: 500;">
                                    <span>{plan.shift.name} ({plan.shift.hours_per_day}h)</span><span>•</span><span id="datetime"></span>
                                </div>
                            </div>
                            {calendar_html}
                        </div>

                        <!-- 1. KPI GRID -->
                        <div class="kpi-grid">
                            <div class="glass-panel kpi-card" style="border-top: 4px solid var(--primary);">
                                <div class="kpi-top">
                                    <div class="kpi-label">Target Volume</div>
                                </div>
                                <div class="kpi-value num-counter" data-target="{plan.target_units}">0</div>
                                <div style="font-size:13px; color:var(--text-2);">Capacity: {plan.units_per_day():,.0f}/day</div>
                            </div>
                            
                            <div class="glass-panel kpi-card" style="border-top: 4px solid var(--success);">
                                <div class="kpi-top">
                                    <div class="kpi-label">Production Days</div>
                                </div>
                                <div class="kpi-value num-counter" data-target="{plan.days_needed()}">0</div>
                                <div style="font-size:13px; color:var(--text-2);">Standard Shift Schedule</div>
                            </div>

                            <div class="glass-panel kpi-card" style="border-top: 4px solid var(--warning);">
                                <div class="kpi-top">
                                    <div class="kpi-label">Total Capital</div>
                                </div>
                                <div class="kpi-value">₹<span class="num-counter" data-target="{plan.total_cost()}">0</span></div>
                                <div style="font-size:13px; color:var(--text-2);">₹{plan.labour_cost()+plan.machine_cost():,.0f} Burn/Day</div>
                            </div>

                            <div class="glass-panel kpi-card" style="border-top: 4px solid var(--purple);">
                                <div class="kpi-top">
                                    <div class="kpi-label">Unit Economics</div>
                                </div>
                                <div class="kpi-value">₹<span class="num-counter" data-target="{plan.cost_per_unit()}">0</span></div>
                                <div style="font-size:13px; color:var(--text-2);">Cost per Unit</div>
                            </div>
                        </div>

                        {shift_matrix_html}
                        
                        <!-- 2. ANALYTICS CHARTS -->
                        <div class="chart-grid">
                            <!-- Progress Line -->
                            <div class="glass-panel" style="display:flex; flex-direction:column; min-height:380px;">
                                <div class="panel-header">
                                    <div class="panel-title">Production Velocity Trajectory</div>
                                </div>
                                <div class="chart-wrapper">
                                    {chart_progress}
                                </div>
                            </div>

                            <!-- Cost Donut & Breakdown -->
                            <div class="glass-panel" style="display:flex; flex-direction:column; min-height:380px;">
                                <div class="panel-header">
                                    <div class="panel-title">Cost Distribution & Breakdown</div>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1; align-items: center;">
                                    <div class="chart-wrapper" id="donut-wrapper" style="min-height: 200px;">
                                        {chart_donut}
                                    </div>
                                    {cost_receipt_html}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Cost Area Chart -->
                        <div class="glass-panel" style="display:flex; flex-direction:column; min-height:350px;">
                            <div class="panel-header">
                                <div class="panel-title">Cumulative Production Cost</div>
                            </div>
                            <div class="chart-wrapper">
                                {chart_cost_accum}
                            </div>
                        </div>

                        <!-- EXTENDED CHARTS ROW -->
                        <div class="chart-grid">
                            <div class="glass-panel" style="display:flex; flex-direction:column; min-height:300px;">
                                <div class="panel-header">
                                    <div class="panel-title">Shift Utilization</div>
                                </div>
                                <div class="chart-wrapper">
                                    {chart_gauge}
                                </div>
                            </div>
                            <div class="glass-panel" style="display:flex; flex-direction:column; min-height:300px;">
                                <div class="panel-header">
                                    <div class="panel-title">Daily Operations Breakdown</div>
                                </div>
                                <div class="chart-wrapper">
                                    {chart_bar}
                                </div>
                            </div>
                        </div>
                        
                        {overtime_html}

                    </div>

                    <!-- RIGHT COLUMN (Intelligence) -->
                    <div class="right-col">
                        
                        <!-- Factory Status -->
                        <div class="glass-panel">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                                <div class="kpi-label">Machine Health</div>
                                <span style="font-size:12px; font-weight:600; color:var(--success); background:rgba(16,185,129,0.1); padding:4px 10px; border-radius:100px;">Optimal</span>
                            </div>
                            <h3 style="font-family:var(--font-display); font-size:18px; margin-bottom:8px;">{plan.machine.name}</h3>
                            <p style="font-size:13px; color:var(--text-2); margin-bottom: 16px;">Telemetry indicates nominal operation. Vibration and thermal metrics normal.</p>
                            
                            {specs_html}
                        </div>

                        <!-- 7-Day Deadline Assessment -->
                        <div class="glass-panel">
                            <div class="kpi-label" style="margin-bottom:16px;">Deadline Risk ({deadline}-Day)</div>
                            {f'<div style="background:rgba(239, 68, 68, 0.05); border:1px solid rgba(239, 68, 68, 0.2); border-radius:12px; padding:16px; position:relative; z-index:1;"><h4 style="font-size:14px; font-weight:600; margin-bottom:4px; color:var(--text-1);">Deadline Impossible</h4><p style="font-size:13px; color:var(--danger); line-height:1.4;">Target physically impossible within {deadline} days using current machine capacity.</p></div>' if not feas['feasible'] else f'<div style=\"background:rgba(245, 158, 11, 0.05); border:1px solid rgba(245, 158, 11, 0.2); border-radius:12px; padding:16px; position:relative; z-index:1;\"><h4 style=\"font-size:14px; font-weight:600; margin-bottom:4px; color:var(--text-1);\">Overtime Required</h4><p style=\"font-size:13px; color:var(--warning); line-height:1.4;\">Target exceeds {deadline}-day capacity. Authorization needed for ₹{ot_cost_7:,.0f} overtime budget.<br><br><b>Assumption:</b><br>Machine OT Cost = OT Hours × Machine Rate<br>Labour OT Cost = OT Hours × Workers × Labour Rate × 1.5</p></div>' if feas['overtime_required_per_day'] > 0 else f'<div style="background:rgba(16, 185, 129, 0.05); border:1px solid rgba(16, 185, 129, 0.2); border-radius:12px; padding:16px; position:relative; z-index:1;"><h4 style="font-size:14px; font-weight:600; margin-bottom:4px; color:var(--text-1);">Fulfillment Verified</h4><p style="font-size:13px; color:var(--success); line-height:1.4;">Plan validates within {deadline}-day window. No overtime capital required.</p></div>'}
                        </div>

                        <!-- AI Recommendations -->
                        <div class="glass-panel">
                            <div class="kpi-label" style="margin-bottom:16px;">AI Insights</div>
                            
                            <div class="ai-card">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                                <div>
                                    <h5 style="font-size:13px; font-weight:600; margin-bottom:4px;">Energy Optimization</h5>
                                    <p style="font-size:12px; color:var(--text-3); line-height:1.4;">Night shift deployment reduces HVAC overhead by 12%.</p>
                                </div>
                            </div>
                            
                            <div class="ai-card">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>
                                <div>
                                    <h5 style="font-size:13px; font-weight:600; margin-bottom:4px;">Predictive Maintenance</h5>
                                    <p style="font-size:12px; color:var(--text-3); line-height:1.4;">Lubrication required after 120hrs of operation.</p>
                                </div>
                            </div>
                        </div>

                        <!-- Timeline -->
                        <div class="glass-panel">
                            <div class="kpi-label" style="margin-bottom:16px;">Execution Timeline</div>
                            <div class="v-timeline">
                                <div class="tl-node">
                                    <div class="tl-dot" style="background:var(--success); border-color:var(--success); box-shadow:0 0 10px var(--success-glow);"></div>
                                    <div><h5 style="font-size:14px; font-weight:600; margin-bottom:4px;">System Configured</h5><p style="font-size:13px; color:var(--text-3);">Target: {plan.target_units:,} units.</p></div>
                                </div>
                                <div class="tl-node">
                                    <div class="tl-dot" style="border-color:var(--primary);"></div>
                                    <div><h5 style="font-size:14px; font-weight:600; color:var(--primary); margin-bottom:4px;">Active Run</h5><p style="font-size:13px; color:var(--text-3);">Velocity: {plan.units_per_day():,.0f}/day.</p></div>
                                </div>
                                <div class="tl-node" style="opacity:0.5;">
                                    <div class="tl-dot"></div>
                                    <div><h5 style="font-size:14px; font-weight:600; margin-bottom:4px;">Target Completion</h5><p style="font-size:13px; color:var(--text-3);">Day {plan.days_needed()}</p></div>
                                </div>
                            </div>
                        </div>

                        <!-- System Assumptions -->
                        <div class="glass-panel" style="margin-top: 24px; background: rgba(0,0,0,0.3);">
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-2)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                                <div class="kpi-label" style="margin:0; font-size:12px;">System Assumptions</div>
                            </div>
                            <ul style="color:var(--text-2); font-size:12px; line-height:1.6; padding-left:16px; margin:0;">
                                <li style="margin-bottom:4px;">Calculations assume 100% machine uptime (0% maintenance delay).</li>
                                <li style="margin-bottom:4px;">Labour costs reflect standard base pay, excluding contractor premiums.</li>
                                                                <li style="margin-bottom:4px;">Costing Assumption: Each scheduled production day is charged as a complete shift, including the final partial-production day.</li>
                                <li style="margin-bottom:4px;">Production Plan Constraint: The system is designed to manage a single active production plan at a time. Each production plan contains one selected machine, one selected shift, and one target quantity. A new plan can replace the existing plan only after user confirmation.</li>
                                <li>Overtime budgets exceeding ₹100,000 require Level 2 management sign-off.</li>
                            </ul>
                            <div style="margin-top:16px; padding-top:12px; border-top:1px solid var(--border-color); font-size:10px; color:var(--text-3); text-align:center; font-family:var(--font-data);">
                                Generated by PlanPro Core Systems
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            
            // User Profile Name Management
            const userProfile = document.getElementById('user-profile');
            const userName = document.getElementById('user-name');
            const userInitials = document.getElementById('user-initials');

            const savedName = localStorage.getItem('planpro_username') || 'J. Doe';
            const updateName = (name) => {{
                userName.innerText = name;
                const words = name.trim().split(' ');
                let initials = words[0][0].toUpperCase();
                if(words.length > 1) initials += words[words.length-1][0].toUpperCase();
                userInitials.innerText = initials;
            }};
            updateName(savedName);

            userProfile.addEventListener('click', () => {{
                const newName = prompt("Enter your name:", userName.innerText);
                if(newName && newName.trim().length > 0) {{
                    localStorage.setItem('planpro_username', newName.trim());
                    updateName(newName.trim());
                }}
            }});



            // 1. Plotly Post-Processing Engine
            const fixPlotlyCharts = () => {{
                const charts = document.querySelectorAll('.plotly-graph-div');
                const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                
                const rootStyle = getComputedStyle(document.documentElement);
                const textColor = rootStyle.getPropertyValue('--chart-text').trim() || '#94a3b8';
                const gridColor = rootStyle.getPropertyValue('--chart-grid').trim() || 'rgba(255,255,255,0.05)';
                
                charts.forEach(chart => {{
                    if (!chart.data || !chart.layout) return;
                    
                    const isPie = chart.data[0].type === 'pie';
                    const isIndicator = chart.data[0].type === 'indicator';
                    
                    const layoutUpdate = {{
                        'font.family': 'Inter, sans-serif',
                        'font.color': textColor,
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                        'hoverlabel.bgcolor': isDark ? '#0f172a' : '#ffffff',
                        'hoverlabel.bordercolor': isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                        'hoverlabel.font.family': 'Inter, sans-serif',
                        'hoverlabel.font.size': 13,
                        'autosize': true
                    }};

                    if (isPie) {{
                        layoutUpdate['showlegend'] = true;
                        layoutUpdate['legend.orientation'] = 'h';
                        layoutUpdate['legend.y'] = -0.1;
                        layoutUpdate['legend.x'] = 0.5;
                        layoutUpdate['legend.xanchor'] = 'center';
                        layoutUpdate['margin.t'] = 20;
                        layoutUpdate['margin.b'] = 40;
                        layoutUpdate['margin.l'] = 20;
                        layoutUpdate['margin.r'] = 20;
                        
                        Plotly.restyle(chart, {{
                            'textinfo': 'percent',
                            'hoverinfo': 'label+value+percent'
                        }});
                        
                        if (chart.layout.annotations && chart.layout.annotations.length > 0) {{
                            const ann = chart.layout.annotations[0];
                            ann.font.family = 'Plus Jakarta Sans, sans-serif';
                            ann.font.color = isDark ? '#f9fafb' : '#0f172a';
                            layoutUpdate['annotations'] = [ann];
                        }}
                    }} else if (isIndicator) {{
                        layoutUpdate['margin.t'] = 40;
                        layoutUpdate['margin.b'] = 20;
                        layoutUpdate['margin.l'] = 20;
                        layoutUpdate['margin.r'] = 20;
                    }} else {{
                        layoutUpdate['margin.t'] = 20;
                        layoutUpdate['margin.b'] = 40;
                        layoutUpdate['margin.l'] = 60;
                        layoutUpdate['margin.r'] = 20;
                        layoutUpdate['xaxis.showgrid'] = false;
                        layoutUpdate['yaxis.showgrid'] = true;
                        layoutUpdate['yaxis.gridcolor'] = gridColor;
                        layoutUpdate['xaxis.color'] = textColor;
                        layoutUpdate['yaxis.color'] = textColor;
                    }}

                    Plotly.relayout(chart, layoutUpdate);
                    Plotly.Plots.resize(chart);
                }});
            }};

            setTimeout(fixPlotlyCharts, 100);

            window.addEventListener('resize', () => {{
                document.querySelectorAll('.plotly-graph-div').forEach(chart => {{
                    if(chart.layout) Plotly.Plots.resize(chart);
                }});
            }});

            const updateTime = () => {{
                const now = new Date();
                document.getElementById('datetime').innerText = now.toLocaleString('en-US', {{ weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }});
                document.getElementById('header-date').innerText = now.toLocaleString('en-US', {{ weekday: 'short', month: 'long', day: 'numeric' }});
            }};
            updateTime(); setInterval(updateTime, 1000);

            document.querySelector('.scroll-area').addEventListener('mousemove', e => {{
                document.querySelectorAll('.glass-panel').forEach(card => {{
                    const rect = card.getBoundingClientRect();
                    card.style.setProperty('--mouse-x', `${{e.clientX - rect.left}}px`);
                    card.style.setProperty('--mouse-y', `${{e.clientY - rect.top}}px`);
                }});
            }});

            document.querySelectorAll('.num-counter').forEach(counter => {{
                const target = parseFloat(counter.getAttribute('data-target'));
                if (isNaN(target)) return;
                let startTime = null;
                const formatNum = num => num % 1 !== 0 ? num.toFixed(2) : Math.floor(num).toLocaleString('en-US');
                const step = (timestamp) => {{
                    if (!startTime) startTime = timestamp;
                    const progress = Math.min((timestamp - startTime) / 2000, 1);
                    const ease = 1 - Math.pow(1 - progress, 4); 
                    counter.innerText = formatNum(target * ease);
                    if (progress < 1) requestAnimationFrame(step);
                    else counter.innerText = formatNum(target);
                }};
                requestAnimationFrame(step);
            }});

            const themeBtn = document.getElementById('theme-btn');
            let isDark = true;
            themeBtn.addEventListener('click', (e) => {{
                e.preventDefault();
                isDark = !isDark;
                document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
                setTimeout(fixPlotlyCharts, 50);
            }});
        }});
    </script>
</body>
</html>"""

    path = os.path.join(os.path.dirname(__file__), "production_dashboard.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ Dashboard saved: {path}")
    webbrowser.open(f"file://{os.path.abspath(path)}")
