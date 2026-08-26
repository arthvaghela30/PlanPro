from production_planner import Machine, Shift, ProductionPlan
import main

# Test 1
print("=== TEST 1 ===")
machine = Machine("CNC Milling", 35, 1200)
shift = Shift("Afternoon", 8, 5, 150)
plan = ProductionPlan(5000, machine, shift)
res1 = plan.check_feasibility(7)
print(res1)
print(f"Feasible: {res1['feasible']} (Expected: True)")
print(f"OT Cost: {res1['ot_cost']} (Expected ~ 201943)")
print(f"Max Capacity: {res1['max_capacity']} (Expected 840)")
print(f"Required Capacity: {res1['required_capacity']} (Expected 714.29)")
print(f"Normal Capacity: {res1['normal_capacity']} (Expected 280)")
print()

# Test 2
print("=== TEST 2 ===")
plan = ProductionPlan(5000, machine, shift)
res2 = plan.check_feasibility(20)
print(res2)
print(f"Feasible: {res2['feasible']} (Expected: True)")
print(f"OT Cost: {res2['ot_cost']} (Expected: 0)")
print()

# Test 3
print("=== TEST 3 ===")
plan = ProductionPlan(5000, machine, shift)
res3 = plan.check_feasibility(5)
print(res3)
print(f"Feasible: {res3['feasible']} (Expected: False)")
print(f"OT Cost: {res3['ot_cost']} (Expected: 0)")
print()

# Set globals for main.py to quickly run choice 5
main.plan = plan
print("Ready for manual UI test if needed.")
