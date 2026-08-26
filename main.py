from production_planner import Machine, Shift, ProductionPlan, generate_dashboard, MACHINE_CATALOGUE, SHIFT_CATALOGUE
import os
machines = []
shifts = []
plan = None

def select_machine_prompt():
    print("\n── Machine Catalogue ──────────────────────────────")
    print(f"  {'#':<4} {'Machine':<30} {'Units/Hr':<12} {'Cost/Hr':<12}")
    print("  " + "─" * 65)
    for key, m in MACHINE_CATALOGUE.items():
        print(f"  {key:<4} {m['name']:<30} {m['units_per_hour']:<12} ₹{m['hourly_cost']:<11}")
    print("  " + "─" * 65)

    while True:
        pick = input("\n  Select machine number (or 0 to add custom): ").strip()

        if pick == "0":
            name = input("  Machine name: ")
            units_per_hour = float(input("  Units per hour: "))
            hourly_cost = float(input("  Hourly cost (₹): "))
            return Machine(name, units_per_hour, hourly_cost)

        elif pick in MACHINE_CATALOGUE:
            m = MACHINE_CATALOGUE[pick]
            print(f"\n  📋 {m['description']}")
            return Machine(m["name"], m["units_per_hour"], m["hourly_cost"])

        else:
            print("  ⚠ Invalid selection.")

def select_shift_prompt():
    print("\n── Shift Catalogue ──────────────────────────────")
    print(f"  {'#':<4} {'Shift':<30} {'Hours/Day':<12} {'Workers':<12} {'Wage/Hr'}")
    print("  " + "─" * 65)
    for key, s in SHIFT_CATALOGUE.items():
        print(f"  {key:<4} {s['name']:<30} {s['hours_per_day']:<12} {s['workers']:<12} ₹{s['wage_per_hour']}")
    print("  " + "─" * 65)

    while True:
        pick = input("\n  Select shift number (or 0 to add custom): ").strip()

        if pick == "0":
            name = input("  Shift name: ")
            hours_per_day = float(input("  Hours per day: "))
            workers = int(input("  Number of workers: "))
            wage_per_hour = float(input("  Wage per hour (₹): "))  
            return Shift(name, hours_per_day, workers, wage_per_hour)

        elif pick in SHIFT_CATALOGUE:
            s = SHIFT_CATALOGUE[pick]
            print(f"\n  📋 {s['description']}")
            return Shift(s["name"], s["hours_per_day"], s["workers"], s["wage_per_hour"])

        else:
            print("  ⚠ Invalid selection.")

def pick_configured_machine():
    if len(machines) == 1:
        print(f"  ✅ Machine selected: {machines[0].name}")
        return machines[0]
    else:
        print("\n  Available Machines:")
        for i, m in enumerate(machines):
            print(f"    {i+1}. {m.name} — {m.units_per_hour} units/hr")
        while True:
            try:
                m_choice = int(input("  Pick a machine (number): ")) - 1
                if 0 <= m_choice < len(machines):
                    return machines[m_choice]
            except ValueError:
                pass
            print("  ⚠ Invalid selection.")

def pick_configured_shift():
    if len(shifts) == 1:
        print(f"  ✅ Shift selected: {shifts[0].name}")
        return shifts[0]
    else:
        print("\n  Available Shifts:")
        for i, s in enumerate(shifts):
            print(f"    {i+1}. {s.name} — {s.hours_per_day} hrs/day, {s.workers} workers")
        while True:
            try:
                s_choice = int(input("  Pick a shift (number): ")) - 1
                if 0 <= s_choice < len(shifts):
                    return shifts[s_choice]
            except ValueError:
                pass
            print("  ⚠ Invalid selection.")

def main():
    global machines, shifts, plan

    while True:
        print("\n── PlanPro ──")
        print("1. Configure Machines")
        print("2. Configure Shifts")
        print("3. Plan Production Run")
        print("4. View Cost Analysis")
        print("5. Deadline Feasibility Check")
        print("6. Export Dashboard")
        print("0. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            m = select_machine_prompt()
            machines.append(m)
            print(f"  ✅ Machine '{m.name}' added to available resources.")

        elif choice == "2":
            s = select_shift_prompt()
            shifts.append(s)
            print(f"  ✅ Shift '{s.name}' added to available resources.")

        elif choice == "3":
            if not machines or not shifts:
                print("  ⚠ Add at least one machine and one shift first.")
                continue

            if plan is None:
                print("\n── Production Planning ──")
                selected_machine = pick_configured_machine()
                selected_shift = pick_configured_shift()
                target = int(input("  Enter Target Units: "))
                plan = ProductionPlan(target_units=target, machine=selected_machine, shift=selected_shift)
                print(f"  ✅ Plan created: {target} units on {selected_machine.name} with {selected_shift.name} shift.")
            else:
                print("\n── Production Planning ──")
                print("\n  ⚠ Only one production plan can be active at a time.")
                print("\n  Current Plan:")
                print(f"  Machine : {plan.machine.name}")
                print(f"  Shift   : {plan.shift.name}")
                print(f"  Target  : {plan.target_units:,} units\n")
                
                print("  1. Create New Plan")
                print("  2. Modify Current Plan")
                print("  3. Back")
                
                sub_choice = input("\n  Select an option: ").strip()
                
                if sub_choice == "1":
                    print("\n  ⚠ A production plan already exists.")
                    print("  Creating a new plan will replace the current plan.")
                    confirm = input("\n  Continue? (Y/N): ").strip().upper()
                    if confirm == 'Y':
                        selected_machine = pick_configured_machine()
                        selected_shift = pick_configured_shift()
                        target = int(input("  Enter Target Units: "))
                        plan = ProductionPlan(target_units=target, machine=selected_machine, shift=selected_shift)
                        print(f"  ✅ Plan created: {target} units on {selected_machine.name} with {selected_shift.name} shift.")
                
                elif sub_choice == "2":
                    while True:
                        print("\n  Modify Current Plan:")
                        print("  1. Change Machine")
                        print("  2. Change Shift")
                        print("  3. Change Target")
                        print("  4. Back")
                        
                        mod_choice = input("\n  Select an option: ").strip()
                        
                        if mod_choice == "1":
                            plan.machine = pick_configured_machine()
                            print(f"  ✅ Machine updated to: {plan.machine.name}")
                        elif mod_choice == "2":
                            plan.shift = pick_configured_shift()
                            print(f"  ✅ Shift updated to: {plan.shift.name}")
                        elif mod_choice == "3":
                            plan.target_units = int(input("  Enter Target Units: "))
                            print(f"  ✅ Target updated to: {plan.target_units:,}")
                        elif mod_choice == "4":
                            break
                        else:
                            print("  ⚠ Invalid selection.")
                
                elif sub_choice == "3":
                    pass

        elif choice == "4":
            if plan is None:
                print("  ⚠ Create a production plan first (option 3).")
            else:
                print("\n── Production Summary ────────────────")
                print(f"  Machine          : {plan.machine.name}")
                print(f"  Shift            : {plan.shift.name}")
                print(f"  Target Units     : {plan.target_units:,}")
                print(f"  Units/Day        : {plan.units_per_day():,.0f}")
                print(f"  Normal Completion Time : {plan.days_needed()} days")
                print(f"  Labour Cost/Day  : ₹{plan.labour_cost():,.0f}")
                print(f"  Machine Cost/Day : ₹{plan.machine_cost():,.0f}")
                print(f"  Total Cost       : ₹{plan.total_cost():,.0f}")
                print(f"  Cost per Unit    : ₹{plan.cost_per_unit():,.2f}")

        elif choice == "5":
            if plan is None:
                print("  ⚠ Create a production plan first (option 3).")
            else:
                deadline = int(input("  Deadline (days): "))
                plan.deadline = deadline
                res = plan.check_feasibility(deadline)
                
                print("\n  Deadline Feasibility Analysis")
                print("  ────────────────────────────────")
                print(f"  Target Units          : {res['target_units']:,}")
                print(f"  Requested Deadline     : {res['deadline']} days")
                print()
                print(f"  Normal Capacity        : {res['normal_capacity']:,.0f} units/day")
                print(f"  Required Capacity      : {res['required_capacity']:,.0f} units/day")
                print(f"  Capacity Gap           : {max(0, res['required_capacity'] - res['normal_capacity']):,.0f} units/day")
                print()
                print(f"  Normal Operating Time  : {res['normal_shift_hours']:.2f} hrs/day")
                print(f"  Required Operating Time: {res['required_operating_hours']:.2f} hrs/day")
                print(f"  Overtime Required      : {res['overtime_required_per_day']:.2f} hrs/day")
                print(f"  24-Hour Theoretical Capacity : {res['max_capacity']:,.0f} units/day")
                print()
                print("  Status:")
                if not res["feasible"]:
                    print("  ✕ DEADLINE NOT FEASIBLE")
                    print()
                    print("  Reason:")
                    print(f"  Required operating time: {res['required_operating_hours']:.2f} hours/day")
                    print("  Maximum available: 24 hours/day")
                    print(f"  Shortfall: {(res['required_operating_hours'] - 24):.2f} hours/day")
                    print()
                    print("  Recommendations:")
                    print("  • Extend the deadline")
                    print("  • Use an additional machine")
                elif res["overtime_required_per_day"] > 0:
                    print("  ✓ FEASIBLE WITH OVERTIME")
                    print()
                    print("  Overtime Cost Analysis")
                    print("  ────────────────────────────")
                    print(f"  Overtime Hours/Day       : {res['overtime_required_per_day']:.2f} hrs")
                    print(f"  Total Overtime Hours     : {res['total_ot_machine_hours']:.2f} hrs")
                    print()
                    print(f"  Machine Overtime Cost    : ₹{res['machine_ot_cost']:,.0f}")
                    print(f"  Labour Overtime Cost     : ₹{res['labour_ot_cost']:,.0f}")
                    print("  ────────────────────────────")
                    print(f"  Total Overtime Cost      : ₹{res['ot_cost']:,.0f}")
                    print()
                    print("  (Assumptions:")
                    print("   Machine OT Cost = OT Hours × Machine Rate")
                    print("   Labour OT Cost = OT Hours × Workers × Labour Rate × 1.5)")
                else:
                    print("  ✓ FEASIBLE WITHOUT OVERTIME")
                    print()
                    
        elif choice == "6":
            if plan is None:
                print("  ⚠ Create a production plan first (option 3).")
            else:
                generate_dashboard(plan)

        elif choice == "0":
            break
        else:
            print("  ⚠ Invalid selection.")

if __name__ == "__main__":
    main()
