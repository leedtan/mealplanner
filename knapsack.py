from sr26abbr import load


db = load.load()


orig_target = dict(
    Fiber_TD=38,
    Protein=155,
    Vit_A_RAE=900,
    Vit_C=90,
    Vit_D_mcg=15,
    Vit_E=15,
    Vit_K=120,
    Thiamin=1.2,
    Riboflavin=1.3,
    Niacin=16,
    Vit_B6=1.3,
    Folate_Tot=400,
    Vit_B12=2.4,
    Panto_acid=5,
    # Biotin=30 mcg,
    Choline_Tot=550,
    Calcium=1000,
    Iron=8,
    Magnesium=400,
    Manganese=2.3,
    # Molybdenum = 45 mcg
    Phosphorus=700,
    Potassium=4700,
    Selenium=55,
    Sodium=1500,
    Zinc=11,
    )

empty_micros = dict(
    Fiber_TD=0,
    Protein=0,
    Vit_A_RAE=0,
    Vit_C=0,
    Vit_D_mcg=0,
    Vit_E=0,
    Vit_K=0,
    Thiamin=0,
    Riboflavin=0,
    Niacin=0,
    Vit_B6=0,
    Folate_Tot=0,
    Vit_B12=0,
    Panto_acid=0,
    # Biotin=30 mcg,
    Choline_Tot=0,
    Calcium=0,
    Iron=0,
    Magnesium=0,
    Manganese=0,
    # Molybdenum = 45 mcg
    Phosphorus=0,
    Potassium=0,
    Selenium=0,
    Sodium=0,
    Zinc=0,
    )

	
	
#divide nutritient by calorie
def get_db_nuts(target_keys):
    db_nuts = {tkey: {} for tkey in target_keys}
    for key in db.keys():
        cal = db[key]["Energ_Kcal"]
        for tkey in target_keys:
            db_nuts[tkey][key] = (db[key][tkey] / cal
                                  if db[key][tkey] and cal else 0)
    return db_nuts

#sorts nuts by nutrient density
def get_sorted_nuts(db_nuts, target_keys):
    sorted_nuts = dict()
    for tkey in target_keys:
        sorted_nuts[tkey] = sorted(
            db_nuts[tkey].iteritems(), reverse=True, key=lambda x: x[1])
    return sorted_nuts

#pick top from each micronutrient
def get_meal(sorted_nuts, target_keys):
    meal = []
    for tkey in target_keys:
        k, v = sorted_nuts[tkey][0]
        weight = target[tkey] / (v * db[k]["Energ_Kcal"])
        meal.append((k, weight))

        for key in target_keys:
            if key == tkey:
                target[key] = 0
            elif db[k][key]:
                target[key] = (0 if db[k][key] * weight > target[key]
                               else target[key] - db[k][key] * weight)
    return meal

#return a sorted listed of tuples of (itemcode, fit_val), sorted by fit_val
#where fit_val = get_fit_val(item, target, target_keys, cur_macros)

def get_best(db_copy, target_keys, cur_micros):
	sorted_nuts = dict()
	sorted_nuts = sorted(
		db_copy.iteritems(), reverse=True, 
		key=lambda x: get_fit_val(x, target_keys, cur_micros))
	return sorted_nuts[0]
	
	#def get_best(db_nuts, target_keys, cur_micros):
	#sorted_nuts = dict()
	#sorted_nuts[0] = sorted(
#		db_nuts[0].iteritems(), reverse=True, 
#		key=lambda x: get_fit_val(x, target_keys, cur_micros))
#	return sorted_nuts[0][0]
name = 0
nut = 0
def get_fit_val(item, target_keys, cur_micros):
	add_val = 0
	fit_val = 0
	if item[1]["Energ_Kcal"] == 0:
		return 0;
	for tkey in target_keys:
		name = item[1]
		orig = orig_target[tkey]
		cur = cur_micros[tkey]
		nut = item[1][tkey]
		#fit_val += (orig - cur)*nut/(orig^2)
		if (not(item[1][tkey])):
			break
		try:
			add_val = (orig_target[tkey] - cur_micros[tkey])*item[1][tkey]/(orig_target[tkey]^2)
			fit_val += max(add_val, 0)
		except:
			fit_val = fit_val
	return fit_val/(item[1]["Energ_Kcal"])
db_copy = db.copy()
target_keys = orig_target.keys()
target = orig_target.copy()
cur_micros = empty_micros.copy()
calories = 0
db_nuts = get_db_nuts(target_keys)
meal = []
def find_answer():
	while True:
	    db_copy = db.copy()
	    target = orig_target.copy()
	    cur_micros = empty_micros.copy()
	    calories = 0
	    db_nuts = get_db_nuts(target_keys)
	    meal = []
	    while calories < 2000:
			best_food = get_best(db_copy, target_keys, cur_micros)
			weight = 1
			meal.append((best_food[0], weight))
			for key in target_keys:
				cur = cur_micros[key]
				best_food_zero = best_food[0]
				dbzero = db_copy[best_food[0]]
				dbkey = db_copy[best_food[0]][key]
				if (not(db_copy[best_food[0]][key])):
					continue
				cur_micros[key] = (cur_micros[key] + db_copy[best_food[0]][key] * weight)
			calories += db_copy[best_food[0]]["Energ_Kcal"] * weight
			del db_copy[best_food[0]]
		
	    #sorted_nuts = get_sorted_nuts(db_nuts, target_keys)
	    #meal = get_meal(sorted_nuts, target_keys)
	
	    sums = dict(Sugar_Tot=0, FA_Sat=0, Cholestrl=0, Energ_Kcal=0)
	    for item, weight in meal:
	        if weight:
	            print item, "%.2f" % (weight * 100), db[item]["Shrt_Desc"]
	        for sum_key in sums.keys():
	            if db[item][sum_key]:
	                sums[sum_key] += db[item][sum_key] * weight
	    print sums
	
	    keycode = raw_input("Item code to remove: ")
	    print "Removing [%s]" % keycode
	    if len(keycode) < 5:
	        for key in db.keys():
	            if key.startswith(keycode):
	                db.pop(key)
	    else:
	        db.pop(keycode)
	    find_answer()    
	    
find_answer()
    # rotate thru first to optimize
#    target_keys.append(target_keys.pop(0))
